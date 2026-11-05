"""Multi-Agent Advisory and Self-Evolving Surrogate Optimization Package."""
from __future__ import annotations

from src.agents.crew import AgentRoleSpec, C3MRAdvisoryCrew
from src.agents.evolver import CandidateState, SurrogateEvolver

__all__ = [
    "AgentRoleSpec",
    "C3MRAdvisoryCrew",
    "CandidateState",
    "SurrogateEvolver",
]

