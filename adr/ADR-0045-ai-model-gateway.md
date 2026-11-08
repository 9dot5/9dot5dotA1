# ADR-0045: AI model gateway (aigw) on PC Alentejo

- **Status:** Proposed
- **Date:** 2026-11-08
- **Deciders:** Rui Silva (`9dot5`)
- **Review by:** 2027-05-08
- **Related:** ADR-0004, ADR-0007, ADR-0010, ADR-0011, ADR-0017, ADR-0025, ADR-0031, ADR-0034, ADR-0035, ADR-0042, ADR-0043, ADR-0044, [roadmap/PHASE_04_AI_PLATFORM.md](../roadmap/PHASE_04_AI_PLATFORM.md), [operations/SERVICE_CATALOG.md](../operations/SERVICE_CATALOG.md), [governance/ROI_MATRIX.md](../governance/ROI_MATRIX.md), [RISK_REGISTER.md](../RISK_REGISTER.md) (R-40, R-41, R-42)

## Context

On 2026-11-08 the owner asked that the GPU of PC Alentejo (`host-ops-01`) serve AI to the owner's applications "as a resource that apps can consume, like microservices". The owner also asked that the host can use Claude, OpenAI and Gemini APIs when needed, with "everything abstract and configurable". Owner statement: this must "coexist with what we already have in 9dot5dotA1".

Facts, measured or checked on 2026-11-08:
- **Ollama on `host-ops-01`.**
  - It runs on an RTX 3060 Ti with 8 GB VRAM, serving qwen3:8b, qwen3:1.7b, qwen2.5-coder:7b, llama3.1:8b and nomic-embed-text.
  - It has no authentication; a firewall rule admits only the Tailscale range.
  - The k3s ARC runner pods use it directly.
- **A prototype gateway exists**, in the private repository `9dot5/ai-gateway` (owner's choice of a Go gateway over LiteLLM). It runs in a Podman container on `host-ops-01`.
- **Capacity test** (ADR-0007 decision 2), through the gateway with 200 output tokens per request:

  | Load | Result |
  |---|---|
  | qwen3:8b, 1 request | 2.4 s |
  | qwen3:8b, 16 concurrent | 16/16 served, about 65 tokens/s aggregate, GPU never above 2 requests in flight |
  | qwen3:1.7b, 16 concurrent | about 97 to 134 tokens/s aggregate |
  | qwen3:8b, thinking left on, short question | 14 s and 400 tokens spent reasoning, with an empty answer |
- **Subscriptions are not usable here.** The owner's subscription plans (Claude Pro, Gemini AI Pro, Devin) do not license use by third-party tools (homelab-gitops `docs/registo.md`). Pay-per-use API keys do.
- **Agent CLIs are already governed.** They are tools under ADR-0042, get work through GitHub (ADR-0034, ADR-0043), and every tool call is audited (ADR-0017).

## Decision

1. **`aigw` is the inference service of `host-ops-01`.** It exposes an OpenAI-compatible API on TCP 4000, in a container that runs:
   - as a non-root user;
   - with a read-only root filesystem;
   - with all capabilities dropped.

   Port 4000 is reachable only from loopback, local containers and the Tailscale range, under the same firewall pattern as Ollama and Open WebUI. Applications reach models through `aigw`, not through Ollama directly.
2. **One key per consumer.** Each application, and each agent identity that needs a model, gets its own `aigw_` key with:
   - a model allow-list;
   - a rate limit;
   - a concurrency limit.

   Only the key's SHA-256 is stored, in a config file outside any repository.
3. **Providers are configuration.**
   - Backends are the local Ollama and, optionally, three cloud providers:
     - Anthropic, through the official SDK;
     - OpenAI;
     - Gemini, through its OpenAI-compatible endpoint.
   - Provider keys are read from environment variables filled from a secrets file outside any repository.
   - A backend without its key receives no traffic.
4. **Hosted APIs follow the data class** (ADR-0007 decision 3):
   - A consumer that handles Internal data or above is not granted any cloud alias.
   - Cloud aliases are granted per consumer by the owner.
   - An alias with a fallback (for example, local first and then Claude) falls back only for consumers granted the fallback alias.
   - The default grant is local models only.
5. **aigw does not run agent CLIs.** Claude Code, Devin, Gemini CLI and Codex remain tools under ADR-0042, started per ADR-0034 and ADR-0043. They may use `aigw` as their model endpoint, each with its own key. No HTTP endpoint starts an agent session.
6. **Observability without content.** Each request is logged with:
   - consumer, alias, backend, model;
   - status, duration, tokens.

   Prompts and responses are never logged. Prometheus metrics on `/metrics` feed the monitoring stack of ADR-0035.

7. **Deployed by Ansible (ADR-0025).**
   - **Target.** The aigw container is managed by an `ansible/roles/aigw` role through `ansible-pull` on `host-ops-01`, like the monitoring stack (ADR-0035). The role covers the container, its port binding and its health check.
   - **Not in the repository.** The config with consumer key hashes and the provider secrets file stay outside the repository (ADR-0025 decision 5). The role takes their paths, not their contents.
   - **Until the role is merged.** The container running since 2026-11-08 was started by hand with `podman compose` from the aigw repository. It is a prototype. It is recorded in SERVICE_CATALOG as "Production (planned)" and must not be documented as available before the role applies it.

## Options considered

| Option | Benefits | Costs and risks | ROI score |
|---|---|---|---|
| A: Own Go gateway, providers as config, agent CLIs out of scope (chosen) | One API for every app; per-consumer keys, limits and usage; cloud fallback without app changes; fits ADR-0042; learning value | Code to maintain; the Claude adapter covers text, not tools or images, yet | 4.00 (estimate) |
| B: LiteLLM proxy | Mature; many providers | Python service plus a database to run; less control; not chosen by the owner | Not scored |
| C: Apps call Ollama and the clouds directly | Nothing to build | Ollama has no authentication; provider keys spread across apps; no usage view | Rejected |
| D: Also wrap agent CLIs behind HTTP | One endpoint for everything | Bypasses ADR-0017, ADR-0034 and ADR-0042; breaches subscription terms | Rejected |

Score for A is an estimate. Values: value 4, frequency 4, cost 4 (owned hardware; cloud use is opt-in and pay-per-use), risk 3, reversibility 5, learning 5. Weighted sum: 12 + 8 + 12 + 9 + 10 + 5 = 56, divided by 14 = 4.00.

## Consequences

- Positive: applications use the local GPU through a standard API, with keys, limits and metrics.
- Positive: changing or adding a provider, or a second GPU host, is a config change.
- Positive: this is the first measured model-serving result for Phase 04. It also mitigates the cost score of the "Local AI models" row in the ROI matrix: the hardware is owned and measured.
- Negative: a new service on `host-ops-01`, which is not yet admitted under ADR-0031.
- Negative: cloud calls cost money (R-40). Mitigations:
  - per-consumer grants and rate limits;
  - token metrics per consumer.

  There is no spend budget yet.
- Negative: provider keys sit on `host-ops-01` in a user-only file (R-41). Mitigations:
  - one key per provider, revocable at the provider;
  - no key in Git;
  - a move to the secret manager of ADR-0014 when it exists.
- Negative: a consumer wrongly granted a cloud alias would send its data to a provider (R-42). Mitigation: grants are owner decisions per consumer, and the default grant is local only.
- Follow-up: `ansible/roles/aigw` (decision 7), with `ansible-lint` and a syntax check in the pull request (ADR-0025 decision 6). The container image is published to the registry of the private aigw repository and pinned by digest.
- Follow-up (owner): run `scripts/firewall-tailscale.ps1` from the aigw repository, elevated, and enable Podman machine start at logon. The firewall rule moves into the role when Windows settings are in scope (ADR-0025 decision 3).
- Follow-up: scrape `/metrics` from the monitoring stack (ADR-0035) and add the alerts in the aigw runbook.
- Follow-up: point the OpenCode agents in the ARC runner pods at `aigw`, with a key per agent identity, instead of at Ollama directly.

## Security and compliance notes

- **Trust boundaries.** TB-8 (developer hosts) gains a service reachable over Tailscale. Outbound HTTPS to the providers appears only when their keys are set.
- **Data classes.** Prompts sent to a cloud provider leave the platform. That is why decision 4 ties cloud aliases to the consumer's data class. Logs and metrics hold no content.
- **Controls.**
  - Keys exist only as hashes.
  - Unknown models and providers without keys are refused with a visible error, not silently rerouted.
  - The container runs unprivileged.
- **Threats.**
  - A leaked consumer key allows model use up to that consumer's grants and limits. Revoke it by removing its hash.
  - A prompt injected into an agent (T-03) can spend cloud tokens through that agent's key, bounded by its grants and rate limit.
