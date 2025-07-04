"""
Core module for OpenHands Advanced.

This module provides the core functionality for the OpenHands Advanced AI agent.
"""

# Import submodules
from openhands.core import config
from openhands.core import decision
from openhands.core import learning
from openhands.core import metacognition

# Export main classes
from openhands.core.autonomous_agent import AutonomousAgent
from openhands.core.decision import AutonomousDecisionSystem
from openhands.core.learning import AdaptiveLearningSystem
from openhands.core.metacognition import MetaCognitiveSystem

__all__ = [
    "config",
    "decision",
    "learning",
    "metacognition",
    "AutonomousAgent",
    "AutonomousDecisionSystem",
    "AdaptiveLearningSystem",
    "MetaCognitiveSystem"
]