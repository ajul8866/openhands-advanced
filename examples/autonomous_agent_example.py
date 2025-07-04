#!/usr/bin/env python3
"""
Example of using the Autonomous Agent in OpenHands Advanced.

This script demonstrates how to create and use the AutonomousAgent class
to process tasks without human intervention.
"""

import logging
import json
import time
import os
import sys

# Add the parent directory to the path so we can import openhands
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openhands.core import AutonomousAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Run the autonomous agent example."""
    logger.info("Starting Autonomous Agent Example")
    
    # Create the autonomous agent
    agent = AutonomousAgent()
    
    # Define some example tasks
    tasks = [
        {
            "id": "task_1",
            "type": "code_generation",
            "description": "Generate a Python function to calculate Fibonacci numbers",
            "domain": "programming",
            "context": {
                "language": "python",
                "complexity": "medium"
            },
            "requirements": {
                "functionality": "Calculate Fibonacci numbers",
                "performance": "Efficient implementation"
            }
        },
        {
            "id": "task_2",
            "type": "data_analysis",
            "description": "Analyze a dataset of customer transactions",
            "domain": "data_science",
            "context": {
                "data_size": "large",
                "data_type": "structured"
            },
            "requirements": {
                "insights": "Customer behavior patterns",
                "visualization": "Key trends"
            }
        },
        {
            "id": "task_3",
            "type": "decision_making",
            "description": "Decide on the best approach for a new project",
            "domain": "project_management",
            "context": {
                "team_size": "medium",
                "timeline": "tight"
            },
            "requirements": {
                "methodology": "Agile or Waterfall",
                "resource_allocation": "Optimal"
            }
        },
        {
            "id": "task_4",
            "type": "system_design",
            "description": "Design a scalable microservice architecture",
            "domain": "architecture",
            "context": {
                "scale": "enterprise",
                "users": "millions",
                "transactions": "high-volume"
            },
            "requirements": {
                "scalability": "horizontal",
                "resilience": "high",
                "performance": "low-latency"
            }
        },
        {
            "id": "task_5",
            "type": "debugging",
            "description": "Debug a memory leak in a production application",
            "domain": "troubleshooting",
            "context": {
                "environment": "production",
                "impact": "critical",
                "urgency": "high"
            },
            "requirements": {
                "root_cause": "identify",
                "solution": "permanent",
                "downtime": "minimal"
            }
        },
        {
            "id": "task_6",
            "type": "security_analysis",
            "description": "Perform a security audit of a web application",
            "domain": "security",
            "context": {
                "application_type": "web",
                "data_sensitivity": "high",
                "compliance": "required"
            },
            "requirements": {
                "vulnerabilities": "identify",
                "recommendations": "prioritized",
                "remediation": "actionable"
            }
        },
        {
            "id": "task_7",
            "type": "knowledge_expansion",
            "description": "Research and summarize advances in quantum computing",
            "domain": "research",
            "context": {
                "depth": "technical",
                "timeframe": "recent",
                "audience": "technical"
            },
            "requirements": {
                "accuracy": "high",
                "comprehensiveness": "thorough",
                "clarity": "technical but accessible"
            }
        }
    ]
    
    # Process each task
    results = []
    for task in tasks:
        logger.info(f"Processing task: {task['id']} - {task['description']}")
        result = agent.process_task(task)
        results.append(result)
        
        # Print result
        logger.info(f"Task result: {json.dumps(result, indent=2)}")
        
        # Pause between tasks
        time.sleep(1)
    
    # Get capability report
    capability_report = agent.get_capability_report()
    logger.info(f"Capability Report: {json.dumps(capability_report, indent=2)}")
    
    # Get performance report
    performance_report = agent.get_performance_report()
    logger.info(f"Performance Report: {json.dumps(performance_report, indent=2)}")
    
    # Get learning report
    learning_report = agent.get_learning_report()
    logger.info(f"Learning Report: {json.dumps(learning_report, indent=2)}")
    
    logger.info("Autonomous Agent Example Completed")

if __name__ == "__main__":
    main()