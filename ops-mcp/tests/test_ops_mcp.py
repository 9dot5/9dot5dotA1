"""Tests for the security-relevant behaviour of OPS-MCP. Run: python -m unittest discover -s tests -v"""

import datetime
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ops_mcp import capabilities as caps  # noqa: E402
from ops_mcp.adapters.builtin import NodesAdapter, NotConfiguredAdapter, RepoKnowledgeAdapter  # noqa: E402
from ops_mcp.approval import ApprovalStore  # noqa: E402
from ops_mcp.audit import AuditLog, GENESIS  # noqa: E402
from ops_mcp.errors import AuditUnavailable, Forbidden, GateClosed, InvalidRequest, Unauthenticated  # noqa: E402
from ops_mcp.gate import SecurityGate, StaticGate  # noqa: E402
from ops_mcp.gateway import Gateway, request_hash  # noqa: E402
from ops_mcp.identity import TokenVerifier, mint  # noqa: E402
from ops_mcp.policy import PolicyEngine, load_roles  # noqa: E402
from ops_mcp.server import McpServer, tools_list  # noqa: E402

KEY = b"k" * 32
DIGEST = "sha256:" + "a" * 64
ENABLED_NODES = {
    "alentejo": {"name": "PC Alentejo", "enabled": True, "manual_only": False},
    "sigma": {"name": "Sigma", "enabled": True, "manual_only": True},
    "lsd2": {"name": "LSD2", "enabled": False, "manual_only": True},
}
ROLES_RAW = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))["roles"]


def events(harness):
    return [json.loads(line)["event"] for line in harness.audit_path.read_text().splitlines() if line.strip()]


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


class CountingAdapter:
    def __init__(self):
        self.calls = []

    def execute(self, capability, node, args):
        self.calls.append((capability, node))
        return {"status": "ok"}


class Harness:
    def __init__(self, nodes=None, gate_open=True):
        self.gate_open = gate_open
        self.clock = Clock()
        self.nodes = nodes if nodes is not None else ENABLED_NODES
        self.tmp = tempfile.TemporaryDirectory()
        self.audit_path = Path(self.tmp.name) / "audit.jsonl"
        self.audit = AuditLog(self.audit_path, clock=lambda: datetime.datetime.fromtimestamp(
            self.clock(), datetime.timezone.utc))
        self.counting = CountingAdapter()
        adapters = {c: NotConfiguredAdapter() for c in caps.CAPABILITIES}
        for name in ("restart_service", "start_service", "stop_service", "deploy_service"):
            adapters[name] = self.counting
        adapters["get_nodes"] = NodesAdapter(self.nodes)
        adapters["search_adr"] = RepoKnowledgeAdapter(ROOT.parent / "adr")
        self.gateway = Gateway(
            verifier=TokenVerifier(KEY, clock=self.clock),
            policy=PolicyEngine(load_roles(ROLES_RAW), self.nodes),
            approvals=ApprovalStore(clock=self.clock),
            audit=self.audit,
            adapters=adapters,
            nodes=self.nodes,
            gate=StaticGate(self.gate_open),
        )

    def token(self, sub, kind, roles, ttl=3600):
        return mint(KEY, sub, kind, roles, client_id="test", ttl_s=ttl, now=self.clock())

    def owner(self):
        return self.token("rui", "human", ["owner"])

    def operator(self):
        return self.token("agent-executor", "agent", ["agent_operator"])

    def reader(self):
        return self.token("agent-reader", "agent", ["agent_reader"])

    def close(self):
        self.tmp.cleanup()


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def test_missing_token_is_refused_and_recorded(self):
        with self.assertRaises(Unauthenticated):
            self.h.gateway.call(None, "get_nodes", {})
        self.assertEqual(events(self.h), ["denied"])

    def test_forged_token_is_refused(self):
        forged = mint(b"x" * 32, "rui", "human", ["owner"], "test", now=self.h.clock())
        with self.assertRaises(Unauthenticated):
            self.h.gateway.call(forged, "get_nodes", {})

    def test_expired_token_is_refused(self):
        token = self.h.token("rui", "human", ["owner"], ttl=10)
        self.h.clock.t += 11
        with self.assertRaises(Unauthenticated):
            self.h.gateway.call(token, "get_nodes", {})

    def test_tampered_payload_is_refused(self):
        token = self.h.owner()
        body, sig = token.split(".")
        import base64
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        payload["roles"] = ["owner", "extra"]
        new_body = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        with self.assertRaises(Unauthenticated):
            self.h.gateway.call(new_body + "." + sig, "get_nodes", {})

    def test_short_signing_key_is_rejected(self):
        with self.assertRaises(ValueError):
            TokenVerifier(b"short")


class TestSchemaAndScope(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def test_unknown_capability_is_refused(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.call(self.h.reader(), "run_shell", {"cmd": "id"})

    def test_unknown_argument_is_refused(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.call(self.h.reader(), "get_system_status", {"node": "alentejo", "shell": "x"})

    def test_tag_instead_of_digest_is_refused(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.call(self.h.owner(), "deploy_service",
                                {"node": "alentejo", "service": "qdrant", "digest": "latest"})

    def test_unknown_node_is_refused(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.call(self.h.reader(), "get_system_status", {"node": "elsewhere"})

    def test_integer_bounds_are_enforced(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.call(self.h.reader(), "search_adr", {"query": "x", "limit": 9999})

    def test_oversized_string_is_refused(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.call(self.h.reader(), "search_adr", {"query": "x" * 201})


class TestRbac(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def test_reader_cannot_write(self):
        with self.assertRaises(Forbidden):
            self.h.gateway.call(self.h.reader(), "restart_service", {"node": "alentejo", "service": "qdrant"})
        self.assertEqual(self.h.counting.calls, [])

    def test_workflow_role_is_limited_to_listed_capabilities(self):
        token = self.h.token("backup-verify", "workflow", ["workflow_health"])
        self.h.gateway.call(token, "get_alerts", {})
        with self.assertRaises(Forbidden):
            self.h.gateway.call(token, "get_gpu_status", {"node": "alentejo"})

    def test_role_not_in_policy_grants_nothing(self):
        token = self.h.token("ghost", "agent", ["invented_role"])
        with self.assertRaises(Forbidden):
            self.h.gateway.call(token, "get_nodes", {})

    def test_read_is_allowed_without_approval(self):
        result = self.h.gateway.call(self.h.reader(), "get_nodes", {})
        self.assertEqual({n["id"] for n in result["nodes"]}, {"alentejo", "sigma", "lsd2"})

    def test_disabled_node_is_refused_even_for_owner(self):
        with self.assertRaises(Forbidden):
            self.h.gateway.call(self.h.owner(), "get_system_status", {"node": "lsd2"})

    def test_manual_only_node_refuses_writes(self):
        with self.assertRaises(Forbidden):
            self.h.gateway.call(self.h.owner(), "restart_service", {"node": "sigma", "service": "x"})


class TestApprovals(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.args = {"node": "alentejo", "service": "qdrant"}

    def tearDown(self):
        self.h.close()

    def _request(self):
        out = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.assertEqual(out["status"], "approval_required")
        return out["request_id"]

    def test_write_without_approval_does_not_reach_adapter(self):
        self._request()
        self.assertEqual(self.h.counting.calls, [])

    def test_owner_approval_allows_exactly_one_execution(self):
        rid = self._request()
        self.h.gateway.approve(self.h.owner(), rid)
        self.assertEqual(self.h.gateway.call(self.h.operator(), "restart_service", self.args)["status"], "ok")
        self.assertEqual(len(self.h.counting.calls), 1)
        again = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.assertEqual(again["status"], "approval_required")
        self.assertEqual(len(self.h.counting.calls), 1)

    def test_agent_cannot_approve(self):
        rid = self._request()
        with self.assertRaises(Forbidden):
            self.h.gateway.approve(self.h.operator(), rid)

    def test_requester_cannot_approve_own_request(self):
        same = self.h.token("rui", "human", ["owner"])
        rid = self._request_as(same)
        with self.assertRaises(Forbidden):
            self.h.gateway.approve(same, rid)

    def test_approval_is_bound_to_request_content(self):
        rid = self._request()
        self.h.gateway.approve(self.h.owner(), rid)
        changed = {"node": "alentejo", "service": "other"}
        out = self.h.gateway.call(self.h.operator(), "restart_service", changed)
        self.assertEqual(out["status"], "approval_required")
        self.assertEqual(self.h.counting.calls, [])

    def test_approval_expires(self):
        rid = self._request()
        self.h.gateway.approve(self.h.owner(), rid)
        self.h.clock.t += 15 * 60 + 1
        out = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.assertEqual(out["status"], "approval_required")
        self.assertEqual(self.h.counting.calls, [])

    def test_approval_cannot_be_used_by_another_requester(self):
        rid = self._request()
        self.h.gateway.approve(self.h.owner(), rid)
        other = self.h.token("agent-other", "agent", ["agent_operator"])
        self.assertEqual(self.h.gateway.call(other, "restart_service", self.args)["status"], "approval_required")
        self.assertEqual(self.h.counting.calls, [])

    def test_approving_an_unknown_request_is_refused(self):
        with self.assertRaises(InvalidRequest):
            self.h.gateway.approve(self.h.owner(), "does-not-exist")

    def test_request_hash_is_stable_for_equal_content(self):
        a = request_hash("restart_service", "alentejo", {"node": "alentejo", "service": "q"})
        b = request_hash("restart_service", "alentejo", {"service": "q", "node": "alentejo"})
        self.assertEqual(a, b)

    def _request_as(self, token):
        out = self.h.gateway.call(token, "restart_service", self.args)
        return out["request_id"]


class TestAudit(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def test_every_call_leaves_attempt_and_result(self):
        self.h.gateway.call(self.h.reader(), "get_nodes", {})
        events = [json.loads(line)["event"] for line in self.h.audit_path.read_text().splitlines()]
        self.assertEqual(events, ["attempt", "result"])

    def test_chain_verifies(self):
        self.h.gateway.call(self.h.reader(), "get_nodes", {})
        ok, count, _ = self.h.audit.verify()
        self.assertTrue(ok)
        self.assertEqual(count, 2)

    def test_editing_a_record_breaks_the_chain(self):
        self.h.gateway.call(self.h.reader(), "get_nodes", {})
        lines = self.h.audit_path.read_text().splitlines()
        record = json.loads(lines[1])
        record["capability"] = "get_alerts"
        lines[1] = json.dumps(record, sort_keys=True)
        self.h.audit_path.write_text("\n".join(lines) + "\n")
        ok, _, message = self.h.audit.verify()
        self.assertFalse(ok)
        self.assertIn("altered", message)

    def test_deleting_a_record_breaks_the_chain(self):
        self.h.gateway.call(self.h.reader(), "get_nodes", {})
        lines = self.h.audit_path.read_text().splitlines()
        self.h.audit_path.write_text("\n".join(lines[1:]) + "\n")
        ok, _, _ = self.h.audit.verify()
        self.assertFalse(ok)

    def test_empty_log_has_genesis_head(self):
        self.assertEqual(self.h.audit.verify(), (True, 0, "no audit log yet"))
        self.assertEqual(GENESIS, "0" * 64)

    def test_unwritable_audit_blocks_the_action(self):
        blocked = Path(self.h.tmp.name) / "file-not-dir"
        blocked.write_text("x")
        bad = AuditLog(blocked / "audit.jsonl")
        self.h.gateway._audit = bad
        with self.assertRaises(AuditUnavailable):
            self.h.gateway.call(self.h.owner(), "restart_service", {"node": "alentejo", "service": "q"})
        self.assertEqual(self.h.counting.calls, [])

    def test_approval_is_recorded(self):
        out = self.h.gateway.call(self.h.operator(), "restart_service", {"node": "alentejo", "service": "q"})
        self.h.gateway.approve(self.h.owner(), out["request_id"])
        self.assertIn("approval_granted", events(self.h))


class TestKnowledgeAndNodes(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def test_search_adr_finds_ops_mcp_decision(self):
        out = self.h.gateway.call(self.h.reader(), "search_adr", {"query": "Operations MCP"})
        ids = [r["adr"] for r in out["results"]]
        self.assertIn("ADR-0029", ids)

    def test_search_adr_reports_status_of_each_hit(self):
        out = self.h.gateway.call(self.h.reader(), "search_adr", {"query": "ADR-0029"})
        statuses = {r["adr"]: r["status"] for r in out["results"]}
        self.assertEqual(statuses.get("ADR-0029"), "Proposed")

    def test_unconfigured_sources_say_so(self):
        out = self.h.gateway.call(self.h.reader(), "search_jira", {"query": "PLAT"})
        self.assertEqual(out["status"], "not_configured")

    def test_unconfigured_infrastructure_reads_say_so(self):
        out = self.h.gateway.call(self.h.reader(), "get_gpu_status", {"node": "alentejo"})
        self.assertEqual(out["status"], "not_configured")


class TestApiContract(unittest.TestCase):
    def test_every_required_capability_is_registered(self):
        required = {
            "get_nodes", "get_inventory", "get_system_status",
            "get_vm_status", "get_storage_status", "get_network_status",
            "get_gpu_status", "get_openwebui_status", "get_ollama_status", "get_qdrant_status", "get_models",
            "restart_service", "stop_service", "start_service", "deploy_service",
            "get_alerts", "get_incidents", "get_availability",
            "search_adr", "search_confluence", "search_jira",
        }
        self.assertEqual(set(caps.CAPABILITIES), required)

    def test_write_capabilities_are_exactly_the_four_operations(self):
        writes = {n for n, c in caps.CAPABILITIES.items() if c.tier == caps.WRITE}
        self.assertEqual(writes, {"restart_service", "stop_service", "start_service", "deploy_service"})

    def test_api_document_lists_every_capability(self):
        text = (ROOT / "docs" / "API.md").read_text(encoding="utf-8")
        for name in caps.CAPABILITIES:
            self.assertIn(f"`{name}`", text, name)

    def test_tools_list_matches_registry(self):
        names = {t["name"] for t in tools_list()["tools"]}
        self.assertEqual(names, set(caps.CAPABILITIES))

    def test_schemas_reject_extra_properties(self):
        for tool in tools_list()["tools"]:
            self.assertFalse(tool["inputSchema"]["additionalProperties"], tool["name"])


class TestServer(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.server = McpServer(self.h.gateway, self.h.reader(), client_id="test-client")

    def tearDown(self):
        self.h.close()

    def test_initialize_and_tools_list(self):
        init = self.server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertIn("serverInfo", init["result"])
        listed = self.server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(listed["result"]["tools"]), len(caps.CAPABILITIES))

    def test_notification_gets_no_response(self):
        self.assertIsNone(self.server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tool_call_returns_result_text(self):
        resp = self.server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                                   "params": {"name": "get_nodes", "arguments": {}}})
        self.assertNotIn("isError", resp["result"])
        self.assertIn("alentejo", resp["result"]["content"][0]["text"])

    def test_refusal_is_an_error_result_not_a_crash(self):
        resp = self.server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                   "params": {"name": "run_shell", "arguments": {}}})
        self.assertTrue(resp["result"]["isError"])

    def test_unknown_method_is_a_protocol_error(self):
        resp = self.server.handle({"jsonrpc": "2.0", "id": 5, "method": "shell/exec"})
        self.assertEqual(resp["error"]["code"], -32601)


class FailingAudit(AuditLog):
    """An audit log that cannot write. Used to prove that state does not change when the record fails."""

    def __init__(self, path, fail_on=None):
        super().__init__(path)
        self.fail_on = fail_on
        self.writes = 0

    def append(self, event, fields):
        if self.fail_on is None or event == self.fail_on:
            raise AuditUnavailable("forced failure for test")
        return super().append(event, fields)


class TestR22AuditBeforeStateChange(unittest.TestCase):
    """R-22: a state change must not happen unless its audit record was written first."""

    def setUp(self):
        self.h = Harness()
        self.args = {"node": "alentejo", "service": "qdrant"}

    def tearDown(self):
        self.h.close()

    def test_failed_approval_record_grants_nothing(self):
        out = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.h.gateway._audit = FailingAudit(self.h.audit_path, fail_on="approval_granted")
        with self.assertRaises(AuditUnavailable):
            self.h.gateway.approve(self.h.owner(), out["request_id"])
        # Still pending: the approval must not exist without its record.
        record = self.h.gateway._approvals._records[out["request_id"]]
        self.assertIsNone(record.approver_sub)
        self.h.gateway._audit = AuditLog(self.h.audit_path)
        again = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.assertEqual(again["status"], "approval_required")
        self.assertEqual(self.h.counting.calls, [])

    def test_failed_use_record_leaves_approval_unused_and_action_undone(self):
        out = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.h.gateway.approve(self.h.owner(), out["request_id"])
        self.h.gateway._audit = FailingAudit(self.h.audit_path, fail_on="approval_used")
        with self.assertRaises(AuditUnavailable):
            self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.assertEqual(self.h.counting.calls, [])
        self.assertFalse(self.h.gateway._approvals._records[out["request_id"]].used)

    def test_authorisation_is_recorded_before_the_action(self):
        out = self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        self.h.gateway.approve(self.h.owner(), out["request_id"])
        self.h.gateway.call(self.h.operator(), "restart_service", self.args)
        events = [e["event"] for e in map(json.loads, self.h.audit_path.read_text().splitlines())]
        self.assertLess(events.index("approval_used"), len(events) - 1)
        self.assertEqual(events[-1], "result")
        self.assertLess(events.index("approval_used"), events.index("result"))


class TestR23ApprovalPersistence(unittest.TestCase):
    """R-23: pending and used approvals survive a restart (ADR-0032)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.journal = Path(self.tmp.name) / "approvals.jsonl"
        self.clock = Clock()

    def tearDown(self):
        self.tmp.cleanup()

    def _store(self):
        return ApprovalStore(clock=self.clock, journal=self.journal)

    def _principal(self, sub, kind="agent", roles=("agent_operator",)):
        from ops_mcp.identity import Principal
        return Principal(sub=sub, kind=kind, roles=tuple(roles), client_id="t")

    def test_pending_request_survives_restart(self):
        store = self._store()
        rec = store.request("h" * 64, self._principal("agent-a"), "restart_service", "alentejo")
        reloaded = self._store()
        self.assertIn(rec.request_id, reloaded._records)

    def test_approved_request_survives_restart_and_is_usable_once(self):
        store = self._store()
        rec = store.request("h" * 64, self._principal("agent-a"), "restart_service", "alentejo")
        store.check_approve(rec.request_id, self._principal("rui", "human", ["owner"]), True)
        store.commit_approve(rec.request_id, "rui")
        reloaded = self._store()
        usable = reloaded.find_usable(self._principal("agent-a"), "h" * 64)
        self.assertIsNotNone(usable)
        reloaded.commit_use(usable.request_id)
        self.assertIsNone(self._store().find_usable(self._principal("agent-a"), "h" * 64))

    def test_used_flag_persists(self):
        store = self._store()
        rec = store.request("h" * 64, self._principal("agent-a"), "restart_service", "alentejo")
        store.commit_approve(rec.request_id, "rui")
        store.commit_use(rec.request_id)
        self.assertTrue(self._store()._records[rec.request_id].used)

    def test_journal_failure_leaves_state_unchanged(self):
        store = self._store()
        rec = store.request("h" * 64, self._principal("agent-a"), "restart_service", "alentejo")
        (Path(self.tmp.name) / "file-not-dir").write_text("x")
        blocked = ApprovalStore(clock=self.clock, journal=Path(self.tmp.name) / "file-not-dir" / "approvals.jsonl")
        blocked._records[rec.request_id] = rec
        from ops_mcp.errors import StoreUnavailable
        with self.assertRaises(StoreUnavailable):
            blocked.commit_use(rec.request_id)
        self.assertFalse(rec.used)


class TestSecurityGate(unittest.TestCase):
    """Operations MCP cannot reach a node until the gate is open (ADR-0031)."""

    def test_closed_gate_refuses_node_reads_even_for_owner(self):
        h = Harness(gate_open=False)
        try:
            with self.assertRaises(GateClosed):
                h.gateway.call(h.owner(), "get_system_status", {"node": "alentejo"})
            self.assertIn("denied", [json.loads(l)["event"] for l in h.audit_path.read_text().splitlines()])
        finally:
            h.close()

    def test_closed_gate_refuses_writes_and_creates_no_approval(self):
        h = Harness(gate_open=False)
        try:
            with self.assertRaises(GateClosed):
                h.gateway.call(h.operator(), "restart_service", {"node": "alentejo", "service": "q"})
            self.assertEqual(h.gateway._approvals._records, {})
        finally:
            h.close()

    def test_closed_gate_still_allows_local_capabilities(self):
        h = Harness(gate_open=False)
        try:
            self.assertIn("nodes", h.gateway.call(h.reader(), "get_nodes", {}))
            self.assertEqual(h.gateway.call(h.reader(), "search_adr", {"query": "ADR-0029"})["count"] >= 1, True)
        finally:
            h.close()

    def test_real_gate_is_closed_while_adrs_are_proposed(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr = Path(tmp)
            for n in ("0029", "0030", "0031", "0032", "0033"):
                (adr / f"ADR-{n}-x.md").write_text("# X\n\n- **Status:** Proposed\n", encoding="utf-8")
            gate = SecurityGate({"threat_model_reviewed_by": "rui", "threat_model_review_date": "2026-11-01",
                                 "permission_matrix_approved_by": "rui",
                                 "permission_matrix_approved_date": "2026-11-01"}, adr)
            self.assertFalse(gate.is_open())
            self.assertIn("ADR-0029", gate.status()["missing"])

    def test_real_gate_needs_every_condition(self):
        with tempfile.TemporaryDirectory() as tmp:
            adr = Path(tmp)
            for n in ("0029", "0030", "0031", "0032", "0033"):
                (adr / f"ADR-{n}-x.md").write_text("# X\n\n- **Status:** Accepted\n", encoding="utf-8")
            empty = SecurityGate({"threat_model_reviewed_by": "", "threat_model_review_date": "",
                                  "permission_matrix_approved_by": "", "permission_matrix_approved_date": ""}, adr)
            self.assertFalse(empty.is_open())
            full = SecurityGate({"threat_model_reviewed_by": "rui", "threat_model_review_date": "2026-11-01",
                                 "permission_matrix_approved_by": "rui",
                                 "permission_matrix_approved_date": "2026-11-01"}, adr)
            self.assertTrue(full.is_open())

    def test_shipped_configuration_is_closed(self):
        from ops_mcp.app import build_gateway
        with tempfile.TemporaryDirectory() as tmp:
            gw = build_gateway(b"k" * 32, Path(tmp) / "audit.jsonl")
            self.assertFalse(gw._gate.is_open())


if __name__ == "__main__":
    unittest.main()
