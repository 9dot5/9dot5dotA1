"""Error types. Each carries a stable code so clients can tell refusals apart."""


class OpsError(Exception):
    code = "error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class Unauthenticated(OpsError):
    code = "unauthenticated"


class Forbidden(OpsError):
    code = "forbidden"


class GateClosed(Forbidden):
    """The security gate is closed: no node may be contacted (ADR-0031, gate)."""

    code = "gate_closed"


class InvalidRequest(OpsError):
    code = "invalid_request"


class AuditUnavailable(OpsError):
    """Raised when an audit record cannot be written. The action is then refused (fail closed)."""

    code = "audit_unavailable"


class StoreUnavailable(OpsError):
    """Raised when the approval journal cannot be written. The state change is then refused."""

    code = "store_unavailable"
