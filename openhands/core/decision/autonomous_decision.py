"""
Autonomous Decision System for OpenHands Advanced.

This module implements a multi-level decision making system that allows the agent
to make decisions at different levels of complexity without human intervention.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union
from dataclasses import dataclass
import json
import os
import time
import random

logger = logging.getLogger(__name__)

@dataclass
class Decision:
    """A decision made by the decision engine."""
    id: str
    level: str  # tactical, strategic, executive
    context: Dict[str, Any]
    options: List[Dict[str, Any]]
    selected_option: Dict[str, Any]
    confidence: float
    reasoning: str
    timestamp: float

@dataclass
class Outcome:
    """The outcome of a decision."""
    decision_id: str
    success: bool
    metrics: Dict[str, float]
    feedback: str
    timestamp: float

class TacticalDecisionEngine:
    """
    Makes short-term, immediate decisions based on current context.
    
    Tactical decisions are focused on immediate actions and responses,
    typically with a time horizon of minutes to hours.
    """
    
    def __init__(self):
        self.decisions = []
        self.outcomes = []
    
    def decide(self, context: Dict[str, Any], problem_space: Dict[str, Any]) -> Decision:
        """
        Make a tactical decision based on the current context and problem space.
        
        Args:
            context: The current context
            problem_space: The problem space, including constraints and options
            
        Returns:
            A tactical decision
        """
        options = problem_space.get("options", [])
        constraints = problem_space.get("constraints", {})
        
        if not options:
            # Generate default options if none provided
            options = self._generate_default_options(context, problem_space)
        
        # Filter options based on constraints
        valid_options = self._filter_options(options, constraints)
        
        if not valid_options:
            # If no valid options, relax constraints
            logger.warning("No valid options found, relaxing constraints")
            relaxed_constraints = self._relax_constraints(constraints)
            valid_options = self._filter_options(options, relaxed_constraints)
        
        # Select the best option
        selected_option, confidence, reasoning = self._select_best_option(valid_options, context)
        
        # Create decision
        decision = Decision(
            id=f"tactical_{int(time.time())}_{random.randint(1000, 9999)}",
            level="tactical",
            context=context,
            options=valid_options,
            selected_option=selected_option,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=time.time()
        )
        
        self.decisions.append(decision)
        return decision
    
    def _generate_default_options(self, context: Dict[str, Any], problem_space: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate default options based on the context and problem space."""
        # This is a placeholder - in a real implementation, this would generate
        # meaningful options based on the context and problem space
        return [
            {"id": "option_1", "action": "default_action_1", "expected_outcome": "outcome_1"},
            {"id": "option_2", "action": "default_action_2", "expected_outcome": "outcome_2"}
        ]
    
    def _filter_options(self, options: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter options based on constraints."""
        if not constraints:
            return options
        
        valid_options = []
        for option in options:
            valid = True
            for key, value in constraints.items():
                if key in option and option[key] != value:
                    valid = False
                    break
            
            if valid:
                valid_options.append(option)
        
        return valid_options
    
    def _relax_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Relax constraints to find more options."""
        # Simple implementation: remove one constraint at random
        if not constraints:
            return {}
        
        relaxed = constraints.copy()
        if relaxed:
            key_to_remove = random.choice(list(relaxed.keys()))
            del relaxed[key_to_remove]
        
        return relaxed
    
    def _select_best_option(self, options: List[Dict[str, Any]], context: Dict[str, Any]) -> Tuple[Dict[str, Any], float, str]:
        """Select the best option based on the context."""
        if not options:
            # Return a default option if no options are available
            default_option = {"id": "default", "action": "no_action", "expected_outcome": "unknown"}
            return default_option, 0.0, "No valid options available"
        
        # Simple implementation: select the first option
        # In a real implementation, this would use a more sophisticated selection algorithm
        selected = options[0]
        confidence = 0.8  # Placeholder confidence value
        reasoning = "Selected based on default tactical decision logic"
        
        return selected, confidence, reasoning
    
    def record_outcome(self, outcome: Outcome) -> None:
        """Record the outcome of a decision."""
        self.outcomes.append(outcome)
        
        # Update decision confidence based on outcome
        for decision in self.decisions:
            if decision.id == outcome.decision_id:
                # Adjust confidence based on success
                if outcome.success:
                    decision.confidence = min(1.0, decision.confidence + 0.1)
                else:
                    decision.confidence = max(0.0, decision.confidence - 0.2)
                break

class StrategicDecisionEngine:
    """
    Makes medium-term decisions based on goals and plans.
    
    Strategic decisions involve planning and resource allocation,
    typically with a time horizon of days to weeks.
    """
    
    def __init__(self):
        self.decisions = []
        self.outcomes = []
        self.plans = {}
    
    def decide(self, context: Dict[str, Any], problem_space: Dict[str, Any]) -> Decision:
        """
        Make a strategic decision based on the current context and problem space.
        
        Args:
            context: The current context
            problem_space: The problem space, including goals and resources
            
        Returns:
            A strategic decision
        """
        goals = problem_space.get("goals", [])
        resources = problem_space.get("resources", {})
        constraints = problem_space.get("constraints", {})
        
        # Generate options based on goals and resources
        options = self._generate_options(goals, resources, constraints)
        
        # Evaluate options against goals
        evaluated_options = self._evaluate_options(options, goals)
        
        # Select the best option
        selected_option, confidence, reasoning = self._select_best_option(evaluated_options, context)
        
        # Create decision
        decision = Decision(
            id=f"strategic_{int(time.time())}_{random.randint(1000, 9999)}",
            level="strategic",
            context=context,
            options=evaluated_options,
            selected_option=selected_option,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=time.time()
        )
        
        self.decisions.append(decision)
        
        # Create or update plan
        self._update_plan(decision)
        
        return decision
    
    def _generate_options(self, goals: List[Dict[str, Any]], resources: Dict[str, Any], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate options based on goals and resources."""
        options = []
        
        for goal in goals:
            # Generate options for each goal
            goal_options = self._generate_options_for_goal(goal, resources, constraints)
            options.extend(goal_options)
        
        return options
    
    def _generate_options_for_goal(self, goal: Dict[str, Any], resources: Dict[str, Any], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate options for a specific goal."""
        # This is a placeholder - in a real implementation, this would generate
        # meaningful options based on the goal, resources, and constraints
        return [
            {
                "id": f"option_{goal['id']}_1",
                "goal_id": goal["id"],
                "action": "strategic_action_1",
                "resource_usage": {"time": 2, "compute": 1},
                "expected_outcome": "outcome_1",
                "alignment_score": 0.8
            },
            {
                "id": f"option_{goal['id']}_2",
                "goal_id": goal["id"],
                "action": "strategic_action_2",
                "resource_usage": {"time": 1, "compute": 2},
                "expected_outcome": "outcome_2",
                "alignment_score": 0.7
            }
        ]
    
    def _evaluate_options(self, options: List[Dict[str, Any]], goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate options against goals."""
        evaluated_options = []
        
        for option in options:
            # Find the goal this option is for
            goal_id = option.get("goal_id")
            goal = next((g for g in goals if g["id"] == goal_id), None)
            
            if goal:
                # Calculate goal alignment score
                alignment_score = option.get("alignment_score", 0.5)
                
                # Calculate resource efficiency
                resource_usage = option.get("resource_usage", {})
                efficiency_score = 1.0 - sum(resource_usage.values()) / (len(resource_usage) * 3) if resource_usage else 0.5
                
                # Calculate overall score
                overall_score = 0.7 * alignment_score + 0.3 * efficiency_score
                
                # Add scores to option
                option_with_scores = option.copy()
                option_with_scores["alignment_score"] = alignment_score
                option_with_scores["efficiency_score"] = efficiency_score
                option_with_scores["overall_score"] = overall_score
                
                evaluated_options.append(option_with_scores)
            else:
                # If goal not found, just add the option as is
                evaluated_options.append(option)
        
        return evaluated_options
    
    def _select_best_option(self, options: List[Dict[str, Any]], context: Dict[str, Any]) -> Tuple[Dict[str, Any], float, str]:
        """Select the best option based on scores and context."""
        if not options:
            # Return a default option if no options are available
            default_option = {"id": "default", "action": "no_action", "expected_outcome": "unknown"}
            return default_option, 0.0, "No valid options available"
        
        # Sort options by overall score (descending)
        sorted_options = sorted(options, key=lambda x: x.get("overall_score", 0), reverse=True)
        
        # Select the option with the highest score
        selected = sorted_options[0]
        confidence = selected.get("overall_score", 0.5)
        reasoning = f"Selected based on highest overall score ({confidence:.2f})"
        
        return selected, confidence, reasoning
    
    def _update_plan(self, decision: Decision) -> None:
        """Create or update a plan based on the decision."""
        # Extract goal ID from the selected option
        goal_id = decision.selected_option.get("goal_id")
        
        if not goal_id:
            return
        
        # Create or update plan for this goal
        if goal_id not in self.plans:
            self.plans[goal_id] = {
                "goal_id": goal_id,
                "decisions": [],
                "status": "in_progress",
                "created_at": time.time(),
                "updated_at": time.time()
            }
        
        # Add decision to plan
        self.plans[goal_id]["decisions"].append(decision.id)
        self.plans[goal_id]["updated_at"] = time.time()
    
    def record_outcome(self, outcome: Outcome) -> None:
        """Record the outcome of a decision."""
        self.outcomes.append(outcome)
        
        # Update decision confidence based on outcome
        for decision in self.decisions:
            if decision.id == outcome.decision_id:
                # Adjust confidence based on success
                if outcome.success:
                    decision.confidence = min(1.0, decision.confidence + 0.1)
                else:
                    decision.confidence = max(0.0, decision.confidence - 0.2)
                
                # Update plan status if needed
                goal_id = decision.selected_option.get("goal_id")
                if goal_id and goal_id in self.plans:
                    if not outcome.success:
                        # If a decision failed, mark the plan as needing revision
                        self.plans[goal_id]["status"] = "needs_revision"
                
                break

class ExecutiveDecisionEngine:
    """
    Makes long-term, high-level decisions based on vision and strategy.
    
    Executive decisions involve setting direction and priorities,
    typically with a time horizon of months to years.
    """
    
    def __init__(self):
        self.decisions = []
        self.outcomes = []
        self.vision = {}
        self.strategies = {}
    
    def decide(self, context: Dict[str, Any], problem_space: Dict[str, Any]) -> Decision:
        """
        Make an executive decision based on the current context and problem space.
        
        Args:
            context: The current context
            problem_space: The problem space, including vision and priorities
            
        Returns:
            An executive decision
        """
        vision = problem_space.get("vision", {})
        priorities = problem_space.get("priorities", [])
        constraints = problem_space.get("constraints", {})
        
        # Update vision if provided
        if vision:
            self.vision = vision
        
        # Generate strategic options
        options = self._generate_strategic_options(priorities, constraints)
        
        # Evaluate options against vision and priorities
        evaluated_options = self._evaluate_options(options, self.vision, priorities)
        
        # Select the best option
        selected_option, confidence, reasoning = self._select_best_option(evaluated_options, context)
        
        # Create decision
        decision = Decision(
            id=f"executive_{int(time.time())}_{random.randint(1000, 9999)}",
            level="executive",
            context=context,
            options=evaluated_options,
            selected_option=selected_option,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=time.time()
        )
        
        self.decisions.append(decision)
        
        # Update strategies
        self._update_strategies(decision)
        
        return decision
    
    def _generate_strategic_options(self, priorities: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategic options based on priorities."""
        options = []
        
        for priority in priorities:
            # Generate options for each priority
            priority_options = self._generate_options_for_priority(priority, constraints)
            options.extend(priority_options)
        
        return options
    
    def _generate_options_for_priority(self, priority: Dict[str, Any], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate options for a specific priority."""
        # This is a placeholder - in a real implementation, this would generate
        # meaningful options based on the priority and constraints
        return [
            {
                "id": f"option_{priority['id']}_1",
                "priority_id": priority["id"],
                "strategy": "executive_strategy_1",
                "resource_allocation": {"time": 10, "budget": 5, "personnel": 3},
                "expected_outcome": "long_term_outcome_1",
                "alignment_score": 0.9,
                "risk_level": "medium"
            },
            {
                "id": f"option_{priority['id']}_2",
                "priority_id": priority["id"],
                "strategy": "executive_strategy_2",
                "resource_allocation": {"time": 5, "budget": 10, "personnel": 2},
                "expected_outcome": "long_term_outcome_2",
                "alignment_score": 0.8,
                "risk_level": "low"
            }
        ]
    
    def _evaluate_options(self, options: List[Dict[str, Any]], vision: Dict[str, Any], priorities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate options against vision and priorities."""
        evaluated_options = []
        
        for option in options:
            # Find the priority this option is for
            priority_id = option.get("priority_id")
            priority = next((p for p in priorities if p["id"] == priority_id), None)
            
            if priority:
                # Calculate vision alignment score
                vision_alignment = option.get("alignment_score", 0.5)
                
                # Calculate priority importance
                priority_importance = priority.get("importance", 0.5)
                
                # Calculate risk factor (lower risk is better)
                risk_level = option.get("risk_level", "medium")
                risk_factor = {"low": 0.8, "medium": 0.5, "high": 0.2}.get(risk_level, 0.5)
                
                # Calculate overall score
                overall_score = 0.4 * vision_alignment + 0.4 * priority_importance + 0.2 * risk_factor
                
                # Add scores to option
                option_with_scores = option.copy()
                option_with_scores["vision_alignment"] = vision_alignment
                option_with_scores["priority_importance"] = priority_importance
                option_with_scores["risk_factor"] = risk_factor
                option_with_scores["overall_score"] = overall_score
                
                evaluated_options.append(option_with_scores)
            else:
                # If priority not found, just add the option as is
                evaluated_options.append(option)
        
        return evaluated_options
    
    def _select_best_option(self, options: List[Dict[str, Any]], context: Dict[str, Any]) -> Tuple[Dict[str, Any], float, str]:
        """Select the best option based on scores and context."""
        if not options:
            # Return a default option if no options are available
            default_option = {"id": "default", "strategy": "no_strategy", "expected_outcome": "unknown"}
            return default_option, 0.0, "No valid options available"
        
        # Sort options by overall score (descending)
        sorted_options = sorted(options, key=lambda x: x.get("overall_score", 0), reverse=True)
        
        # Select the option with the highest score
        selected = sorted_options[0]
        confidence = selected.get("overall_score", 0.5)
        reasoning = f"Selected based on highest overall score ({confidence:.2f})"
        
        return selected, confidence, reasoning
    
    def _update_strategies(self, decision: Decision) -> None:
        """Update strategies based on the decision."""
        # Extract priority ID from the selected option
        priority_id = decision.selected_option.get("priority_id")
        
        if not priority_id:
            return
        
        # Create or update strategy for this priority
        strategy_id = f"strategy_{priority_id}"
        self.strategies[strategy_id] = {
            "id": strategy_id,
            "priority_id": priority_id,
            "decisions": [decision.id],
            "strategy": decision.selected_option.get("strategy", "unknown"),
            "status": "active",
            "created_at": time.time(),
            "updated_at": time.time()
        }
    
    def record_outcome(self, outcome: Outcome) -> None:
        """Record the outcome of a decision."""
        self.outcomes.append(outcome)
        
        # Update decision confidence based on outcome
        for decision in self.decisions:
            if decision.id == outcome.decision_id:
                # Adjust confidence based on success
                if outcome.success:
                    decision.confidence = min(1.0, decision.confidence + 0.1)
                else:
                    decision.confidence = max(0.0, decision.confidence - 0.2)
                
                # Update strategy status if needed
                priority_id = decision.selected_option.get("priority_id")
                if priority_id:
                    strategy_id = f"strategy_{priority_id}"
                    if strategy_id in self.strategies:
                        if not outcome.success:
                            # If a decision failed, mark the strategy as needing revision
                            self.strategies[strategy_id]["status"] = "needs_revision"
                
                break

class AutonomousDecisionSystem:
    """
    A multi-level decision making system that can make decisions at different levels of complexity.
    
    This system allows the agent to:
    1. Analyze problems and determine the appropriate decision level
    2. Make tactical (short-term) decisions
    3. Make strategic (medium-term) decisions
    4. Make executive (long-term) decisions
    5. Validate decisions through simulation
    6. Refine decisions based on feedback
    """
    
    def __init__(self):
        """Initialize the autonomous decision system."""
        self.tactical_engine = TacticalDecisionEngine()
        self.strategic_engine = StrategicDecisionEngine()
        self.executive_engine = ExecutiveDecisionEngine()
        self.decisions = {}
        self.outcomes = {}
        
        logger.info("Autonomous Decision System initialized")
    
    def make_decision(self, context: Dict[str, Any], problem_space: Dict[str, Any]) -> Decision:
        """
        Make a decision based on the context and problem space.
        
        Args:
            context: The current context
            problem_space: The problem space, including constraints and options
            
        Returns:
            A decision
        """
        # Analyze the problem complexity
        complexity = self.analyze_complexity(problem_space)
        logger.info(f"Problem complexity determined as: {complexity}")
        
        # Make decision based on complexity
        if complexity == "tactical":
            decision = self.tactical_engine.decide(context, problem_space)
        elif complexity == "strategic":
            decision = self.strategic_engine.decide(context, problem_space)
        else:  # executive
            decision = self.executive_engine.decide(context, problem_space)
        
        # Store the decision
        self.decisions[decision.id] = decision
        
        # Validate the decision
        expected_outcomes = problem_space.get("expected_outcomes", {})
        validated_decision = self.validate_decision(decision, expected_outcomes)
        
        return validated_decision
    
    def analyze_complexity(self, problem_space: Dict[str, Any]) -> str:
        """
        Analyze the complexity of the problem and determine the appropriate decision level.
        
        Args:
            problem_space: The problem space
            
        Returns:
            The complexity level: "tactical", "strategic", or "executive"
        """
        # Check if complexity is explicitly specified
        if "complexity" in problem_space:
            specified_complexity = problem_space["complexity"]
            if specified_complexity in ["tactical", "strategic", "executive"]:
                return specified_complexity
        
        # Determine complexity based on problem space characteristics
        
        # Check for tactical indicators
        if "options" in problem_space or "immediate_action" in problem_space:
            return "tactical"
        
        # Check for strategic indicators
        if "goals" in problem_space or "resources" in problem_space or "plan" in problem_space:
            return "strategic"
        
        # Check for executive indicators
        if "vision" in problem_space or "priorities" in problem_space or "long_term" in problem_space:
            return "executive"
        
        # Default to tactical if no clear indicators
        return "tactical"
    
    def validate_decision(self, decision: Decision, expected_outcomes: Dict[str, Any]) -> Decision:
        """
        Validate a decision by simulating its outcome.
        
        Args:
            decision: The decision to validate
            expected_outcomes: Expected outcomes for validation
            
        Returns:
            The validated decision, possibly refined
        """
        # Simulate the outcome of the decision
        simulation = self.simulate_outcome(decision)
        
        # Compare with expected outcomes
        if expected_outcomes:
            match_score = self.compare_outcomes(simulation, expected_outcomes)
            logger.info(f"Decision validation score: {match_score:.2f}")
            
            # If match score is too low, refine the decision
            if match_score < 0.85:
                logger.info(f"Decision validation score below threshold, refining decision")
                return self.refine_decision(decision, expected_outcomes)
        
        return decision
    
    def simulate_outcome(self, decision: Decision) -> Dict[str, Any]:
        """
        Simulate the outcome of a decision.
        
        Args:
            decision: The decision to simulate
            
        Returns:
            The simulated outcome
        """
        # This is a placeholder - in a real implementation, this would use
        # a more sophisticated simulation model
        
        # Extract relevant information from the decision
        selected_option = decision.selected_option
        expected_outcome = selected_option.get("expected_outcome", "unknown")
        
        # Simple simulation based on confidence
        success_probability = decision.confidence
        success = random.random() < success_probability
        
        # Generate simulated outcome
        simulation = {
            "success": success,
            "outcome": expected_outcome if success else "unexpected_outcome",
            "confidence": success_probability,
            "metrics": {
                "effectiveness": random.uniform(0.5, 1.0) if success else random.uniform(0.0, 0.5),
                "efficiency": random.uniform(0.5, 1.0) if success else random.uniform(0.0, 0.5)
            }
        }
        
        return simulation
    
    def compare_outcomes(self, simulation: Dict[str, Any], expected_outcomes: Dict[str, Any]) -> float:
        """
        Compare simulated outcomes with expected outcomes.
        
        Args:
            simulation: The simulated outcome
            expected_outcomes: The expected outcomes
            
        Returns:
            A match score between 0 and 1
        """
        if not expected_outcomes:
            return 1.0
        
        # Calculate match score based on key metrics
        matches = 0
        total = 0
        
        # Check success
        if "success" in expected_outcomes:
            total += 1
            if simulation.get("success") == expected_outcomes.get("success"):
                matches += 1
        
        # Check outcome
        if "outcome" in expected_outcomes:
            total += 1
            if simulation.get("outcome") == expected_outcomes.get("outcome"):
                matches += 1
        
        # Check metrics
        sim_metrics = simulation.get("metrics", {})
        exp_metrics = expected_outcomes.get("metrics", {})
        
        for key, exp_value in exp_metrics.items():
            if key in sim_metrics:
                total += 1
                sim_value = sim_metrics[key]
                # Consider a match if within 20% of expected value
                if abs(sim_value - exp_value) <= 0.2 * exp_value:
                    matches += 1
        
        # Calculate match score
        match_score = matches / total if total > 0 else 1.0
        
        return match_score
    
    def refine_decision(self, decision: Decision, expected_outcomes: Dict[str, Any]) -> Decision:
        """
        Refine a decision to better match expected outcomes.
        
        Args:
            decision: The decision to refine
            expected_outcomes: The expected outcomes
            
        Returns:
            The refined decision
        """
        # This is a placeholder - in a real implementation, this would use
        # a more sophisticated refinement process
        
        # Create a new context with hints from expected outcomes
        refined_context = decision.context.copy()
        refined_context["expected_outcomes"] = expected_outcomes
        refined_context["previous_decision"] = {
            "id": decision.id,
            "selected_option": decision.selected_option,
            "confidence": decision.confidence
        }
        
        # Create a new problem space with the original options but additional constraints
        problem_space = {
            "options": decision.options,
            "constraints": {
                "avoid_option": decision.selected_option.get("id")
            },
            "expected_outcomes": expected_outcomes
        }
        
        # Make a new decision with the refined context and problem space
        if decision.level == "tactical":
            refined_decision = self.tactical_engine.decide(refined_context, problem_space)
        elif decision.level == "strategic":
            refined_decision = self.strategic_engine.decide(refined_context, problem_space)
        else:  # executive
            refined_decision = self.executive_engine.decide(refined_context, problem_space)
        
        # Store the refined decision
        self.decisions[refined_decision.id] = refined_decision
        
        return refined_decision
    
    def record_outcome(self, decision_id: str, success: bool, metrics: Dict[str, float] = None, feedback: str = "") -> None:
        """
        Record the actual outcome of a decision.
        
        Args:
            decision_id: The ID of the decision
            success: Whether the decision was successful
            metrics: Performance metrics
            feedback: Feedback on the decision
        """
        if decision_id not in self.decisions:
            logger.warning(f"Decision {decision_id} not found")
            return
        
        decision = self.decisions[decision_id]
        
        # Create outcome
        outcome = Outcome(
            decision_id=decision_id,
            success=success,
            metrics=metrics or {},
            feedback=feedback,
            timestamp=time.time()
        )
        
        # Store outcome
        self.outcomes[decision_id] = outcome
        
        # Update decision engine
        if decision.level == "tactical":
            self.tactical_engine.record_outcome(outcome)
        elif decision.level == "strategic":
            self.strategic_engine.record_outcome(outcome)
        else:  # executive
            self.executive_engine.record_outcome(outcome)
        
        logger.info(f"Recorded outcome for decision {decision_id}: success={success}")
    
    def get_decision_history(self, level: str = None) -> List[Decision]:
        """
        Get the history of decisions, optionally filtered by level.
        
        Args:
            level: The decision level to filter by
            
        Returns:
            List of decisions
        """
        if level:
            return [d for d in self.decisions.values() if d.level == level]
        else:
            return list(self.decisions.values())
    
    def get_outcome_history(self) -> List[Outcome]:
        """
        Get the history of outcomes.
        
        Returns:
            List of outcomes
        """
        return list(self.outcomes.values())