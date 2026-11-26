"""AnnabanOS supervised external-agent collaboration gateway.

Simulation/advisory scope only. This package does not boot kernels or execute tasks.
"""
from .agent_gateway import AgentGateway
from .auth_manager import AuthManager, AgentIdentity
from .capability_policy import CapabilityPolicy
from .session_manager import SessionManager

__all__ = [
    "AgentGateway",
    "AgentIdentity",
    "AuthManager",
    "CapabilityPolicy",
    "SessionManager",
]
