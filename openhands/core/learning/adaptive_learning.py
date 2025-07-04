"""
Adaptive Learning System for OpenHands Advanced.

This module implements a continuous learning system that allows the agent to learn
from interactions, adapt its behavior, and improve over time without human intervention.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import json
import os
import time

logger = logging.getLogger(__name__)

@dataclass
class Pattern:
    """A pattern extracted from interaction data."""
    context: Dict[str, Any]
    action: Dict[str, Any]
    outcome: Dict[str, Any]
    success_rate: float
    timestamp: float

@dataclass
class Strategy:
    """A strategy for solving a particular type of problem."""
    name: str
    problem_type: str
    steps: List[Dict[str, Any]]
    success_rate: float
    usage_count: int
    last_used: float

class SemanticMemoryBank:
    """Stores and retrieves patterns and experiences with semantic understanding."""
    
    def __init__(self, storage_path: str = None):
        self.patterns = []
        self.storage_path = storage_path or os.path.join(os.path.expanduser("~"), ".openhands", "memory")
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_patterns()
    
    def store(self, patterns: List[Pattern]) -> None:
        """Store new patterns in the memory bank."""
        self.patterns.extend(patterns)
        self._save_patterns()
        logger.info(f"Stored {len(patterns)} new patterns in memory bank")
    
    def retrieve_similar(self, context: Dict[str, Any], top_k: int = 5) -> List[Pattern]:
        """Retrieve patterns similar to the given context."""
        if not self.patterns:
            return []
        
        # Simple similarity calculation - in a real implementation, use embeddings
        similarities = []
        for pattern in self.patterns:
            similarity = self._calculate_similarity(pattern.context, context)
            similarities.append((pattern, similarity))
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [p for p, _ in similarities[:top_k]]
    
    def _calculate_similarity(self, context1: Dict[str, Any], context2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts."""
        # Simple implementation - count matching keys and values
        # In a real implementation, use vector embeddings and cosine similarity
        common_keys = set(context1.keys()) & set(context2.keys())
        if not common_keys:
            return 0.0
        
        matches = sum(1 for k in common_keys if context1[k] == context2[k])
        return matches / len(common_keys)
    
    def _save_patterns(self) -> None:
        """Save patterns to disk."""
        patterns_data = [
            {
                "context": p.context,
                "action": p.action,
                "outcome": p.outcome,
                "success_rate": p.success_rate,
                "timestamp": p.timestamp
            }
            for p in self.patterns
        ]
        
        with open(os.path.join(self.storage_path, "patterns.json"), "w") as f:
            json.dump(patterns_data, f)
    
    def _load_patterns(self) -> None:
        """Load patterns from disk."""
        pattern_file = os.path.join(self.storage_path, "patterns.json")
        if not os.path.exists(pattern_file):
            return
        
        try:
            with open(pattern_file, "r") as f:
                patterns_data = json.load(f)
            
            self.patterns = [
                Pattern(
                    context=p["context"],
                    action=p["action"],
                    outcome=p["outcome"],
                    success_rate=p["success_rate"],
                    timestamp=p["timestamp"]
                )
                for p in patterns_data
            ]
            logger.info(f"Loaded {len(self.patterns)} patterns from memory bank")
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")

class ExperienceDatabase:
    """Stores and analyzes experiences to derive insights and improve strategies."""
    
    def __init__(self, storage_path: str = None):
        self.experiences = []
        self.insights = []
        self.storage_path = storage_path or os.path.join(os.path.expanduser("~"), ".openhands", "experience")
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_experiences()
    
    def add_experience(self, experience: Dict[str, Any]) -> None:
        """Add a new experience to the database."""
        experience["timestamp"] = time.time()
        self.experiences.append(experience)
        self._derive_insights()
        self._save_experiences()
    
    def get_insights(self, domain: str = None) -> List[Dict[str, Any]]:
        """Get insights, optionally filtered by domain."""
        if domain is None:
            return self.insights
        
        return [i for i in self.insights if i.get("domain") == domain]
    
    def _derive_insights(self) -> None:
        """Analyze experiences to derive insights."""
        # Group experiences by domain
        domains = {}
        for exp in self.experiences:
            domain = exp.get("domain", "general")
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(exp)
        
        # Generate insights for each domain
        new_insights = []
        for domain, exps in domains.items():
            # Calculate success rates for different approaches
            approaches = {}
            for exp in exps:
                approach = exp.get("approach", "default")
                if approach not in approaches:
                    approaches[approach] = {"successes": 0, "total": 0}
                
                approaches[approach]["total"] += 1
                if exp.get("success", False):
                    approaches[approach]["successes"] += 1
            
            # Create insights based on success rates
            for approach, stats in approaches.items():
                if stats["total"] >= 5:  # Only consider approaches with enough data
                    success_rate = stats["successes"] / stats["total"]
                    new_insights.append({
                        "domain": domain,
                        "approach": approach,
                        "success_rate": success_rate,
                        "sample_size": stats["total"],
                        "timestamp": time.time()
                    })
        
        # Update insights
        self.insights = new_insights
    
    def _save_experiences(self) -> None:
        """Save experiences to disk."""
        with open(os.path.join(self.storage_path, "experiences.json"), "w") as f:
            json.dump(self.experiences, f)
        
        with open(os.path.join(self.storage_path, "insights.json"), "w") as f:
            json.dump(self.insights, f)
    
    def _load_experiences(self) -> None:
        """Load experiences from disk."""
        exp_file = os.path.join(self.storage_path, "experiences.json")
        insights_file = os.path.join(self.storage_path, "insights.json")
        
        if os.path.exists(exp_file):
            try:
                with open(exp_file, "r") as f:
                    self.experiences = json.load(f)
                logger.info(f"Loaded {len(self.experiences)} experiences")
            except Exception as e:
                logger.error(f"Error loading experiences: {e}")
        
        if os.path.exists(insights_file):
            try:
                with open(insights_file, "r") as f:
                    self.insights = json.load(f)
                logger.info(f"Loaded {len(self.insights)} insights")
            except Exception as e:
                logger.error(f"Error loading insights: {e}")

class AdaptiveLearningSystem:
    """
    A system that enables continuous learning and adaptation based on interactions.
    
    This system allows the agent to:
    1. Extract patterns from interactions
    2. Store and retrieve relevant experiences
    3. Evaluate its own performance
    4. Adapt its behavior based on past experiences
    5. Generate and test new strategies
    """
    
    def __init__(self, config=None):
        """
        Initialize the adaptive learning system.
        
        Args:
            config: Configuration object with learning parameters
        """
        self.config = config or {}
        self.memory_bank = SemanticMemoryBank()
        self.experience_database = ExperienceDatabase()
        self.learning_rate = self.config.get("learning_rate", 0.1)
        self.adaptation_threshold = self.config.get("adaptation_threshold", 0.7)
        self.strategies = self._load_strategies()
        
        logger.info("Adaptive Learning System initialized")
    
    def learn_from_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """
        Learn from an interaction by extracting patterns and updating strategies.
        
        Args:
            interaction_data: Data about the interaction, including context, actions, and outcomes
        """
        # Extract patterns from the interaction
        patterns = self.extract_patterns(interaction_data)
        self.memory_bank.store(patterns)
        
        # Update experience database
        self.experience_database.add_experience({
            "domain": interaction_data.get("domain", "general"),
            "approach": interaction_data.get("approach", "default"),
            "context": interaction_data.get("context", {}),
            "actions": interaction_data.get("actions", []),
            "outcome": interaction_data.get("outcome", {}),
            "success": interaction_data.get("success", False)
        })
        
        # Evaluate performance and adapt if necessary
        performance = self.evaluate_performance(interaction_data)
        logger.info(f"Performance evaluation: {performance:.2f}")
        
        if performance < self.adaptation_threshold:
            logger.info(f"Performance below threshold ({self.adaptation_threshold}), adapting behavior")
            self.adapt_behavior(interaction_data.get("domain", "general"))
    
    def extract_patterns(self, interaction_data: Dict[str, Any]) -> List[Pattern]:
        """
        Extract patterns from interaction data.
        
        Args:
            interaction_data: Data about the interaction
            
        Returns:
            List of extracted patterns
        """
        patterns = []
        
        # Extract basic pattern from the interaction
        context = interaction_data.get("context", {})
        actions = interaction_data.get("actions", [])
        outcome = interaction_data.get("outcome", {})
        success = interaction_data.get("success", False)
        
        # Create a pattern for each action
        for i, action in enumerate(actions):
            # For simplicity, use the same success rate for all actions
            # In a real implementation, attribute success to specific actions
            pattern = Pattern(
                context=context,
                action=action,
                outcome=outcome,
                success_rate=1.0 if success else 0.0,
                timestamp=time.time()
            )
            patterns.append(pattern)
        
        return patterns
    
    def evaluate_performance(self, interaction_data: Dict[str, Any]) -> float:
        """
        Evaluate the performance of the agent based on interaction data.
        
        Args:
            interaction_data: Data about the interaction
            
        Returns:
            Performance score between 0 and 1
        """
        # Simple performance evaluation based on success and efficiency
        success = interaction_data.get("success", False)
        efficiency = interaction_data.get("efficiency", 0.5)
        
        # Weight success more heavily than efficiency
        performance = 0.7 * (1.0 if success else 0.0) + 0.3 * efficiency
        
        return performance
    
    def adapt_behavior(self, domain: str) -> None:
        """
        Adapt behavior based on past experiences.
        
        Args:
            domain: The domain to adapt behavior for
        """
        # Generate new strategies
        new_strategies = self.generate_strategies(domain)
        
        # Test strategies
        best_strategy = self.test_strategies(new_strategies)
        
        # Implement the best strategy
        if best_strategy:
            self.implement_strategy(best_strategy)
    
    def generate_strategies(self, domain: str) -> List[Strategy]:
        """
        Generate new strategies based on insights from the experience database.
        
        Args:
            domain: The domain to generate strategies for
            
        Returns:
            List of generated strategies
        """
        insights = self.experience_database.get_insights(domain)
        
        # Find the most successful approaches
        approaches = {}
        for insight in insights:
            approach = insight.get("approach", "default")
            success_rate = insight.get("success_rate", 0.0)
            
            if approach not in approaches or success_rate > approaches[approach]:
                approaches[approach] = success_rate
        
        # Generate strategies based on successful approaches
        strategies = []
        for approach, success_rate in approaches.items():
            if success_rate > 0.6:  # Only consider reasonably successful approaches
                # Retrieve patterns related to this approach
                relevant_patterns = [p for p in self.memory_bank.patterns 
                                    if p.action.get("approach") == approach and p.success_rate > 0.7]
                
                if relevant_patterns:
                    # Create steps from successful patterns
                    steps = [{"action": p.action, "context": p.context} for p in relevant_patterns[:5]]
                    
                    strategy = Strategy(
                        name=f"{domain}_{approach}_strategy",
                        problem_type=domain,
                        steps=steps,
                        success_rate=success_rate,
                        usage_count=0,
                        last_used=0
                    )
                    strategies.append(strategy)
        
        # If no strategies were generated, create a default one
        if not strategies:
            strategy = Strategy(
                name=f"{domain}_default_strategy",
                problem_type=domain,
                steps=[],
                success_rate=0.5,
                usage_count=0,
                last_used=0
            )
            strategies.append(strategy)
        
        return strategies
    
    def test_strategies(self, strategies: List[Strategy]) -> Optional[Strategy]:
        """
        Test strategies and select the best one.
        
        In a real implementation, this would involve simulation or A/B testing.
        For now, we'll just select the strategy with the highest success rate.
        
        Args:
            strategies: List of strategies to test
            
        Returns:
            The best strategy, or None if no strategies are provided
        """
        if not strategies:
            return None
        
        # Sort by success rate (descending)
        strategies.sort(key=lambda s: s.success_rate, reverse=True)
        
        return strategies[0]
    
    def implement_strategy(self, strategy: Strategy) -> None:
        """
        Implement a strategy by updating the strategy database.
        
        Args:
            strategy: The strategy to implement
        """
        # Update the strategy in our list
        for i, s in enumerate(self.strategies):
            if s.name == strategy.name:
                self.strategies[i] = strategy
                break
        else:
            # Strategy doesn't exist yet, add it
            self.strategies.append(strategy)
        
        # Save strategies
        self._save_strategies()
        
        logger.info(f"Implemented strategy: {strategy.name}")
    
    def get_strategy_for_problem(self, problem_type: str) -> Optional[Strategy]:
        """
        Get the best strategy for a given problem type.
        
        Args:
            problem_type: The type of problem to solve
            
        Returns:
            The best strategy for the problem, or None if no suitable strategy is found
        """
        # Find strategies for this problem type
        relevant_strategies = [s for s in self.strategies if s.problem_type == problem_type]
        
        if not relevant_strategies:
            return None
        
        # Sort by success rate (descending)
        relevant_strategies.sort(key=lambda s: s.success_rate, reverse=True)
        
        # Update usage statistics
        best_strategy = relevant_strategies[0]
        best_strategy.usage_count += 1
        best_strategy.last_used = time.time()
        
        return best_strategy
    
    def _save_strategies(self) -> None:
        """Save strategies to disk."""
        storage_path = os.path.join(os.path.expanduser("~"), ".openhands", "strategies")
        os.makedirs(storage_path, exist_ok=True)
        
        strategies_data = [
            {
                "name": s.name,
                "problem_type": s.problem_type,
                "steps": s.steps,
                "success_rate": s.success_rate,
                "usage_count": s.usage_count,
                "last_used": s.last_used
            }
            for s in self.strategies
        ]
        
        with open(os.path.join(storage_path, "strategies.json"), "w") as f:
            json.dump(strategies_data, f)
    
    def _load_strategies(self) -> List[Strategy]:
        """Load strategies from disk."""
        storage_path = os.path.join(os.path.expanduser("~"), ".openhands", "strategies")
        os.makedirs(storage_path, exist_ok=True)
        
        strategy_file = os.path.join(storage_path, "strategies.json")
        if not os.path.exists(strategy_file):
            return []
        
        try:
            with open(strategy_file, "r") as f:
                strategies_data = json.load(f)
            
            strategies = [
                Strategy(
                    name=s["name"],
                    problem_type=s["problem_type"],
                    steps=s["steps"],
                    success_rate=s["success_rate"],
                    usage_count=s["usage_count"],
                    last_used=s["last_used"]
                )
                for s in strategies_data
            ]
            logger.info(f"Loaded {len(strategies)} strategies")
            return strategies
        except Exception as e:
            logger.error(f"Error loading strategies: {e}")
            return []