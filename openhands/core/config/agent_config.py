from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from openhands.core.config.condenser_config import CondenserConfig, NoOpCondenserConfig
from openhands.core.config.extended_config import ExtendedConfig
from openhands.core.logger import openhands_logger as logger
from openhands.utils.import_utils import get_impl


class AgentConfig(BaseModel):
    # Basic configuration
    llm_config: str | None = Field(default=None)
    """The name of the llm config to use. If specified, this will override global llm config."""
    classpath: str | None = Field(default=None)
    """The classpath of the agent to use. To be used for custom agents that are not defined in the openhands.agenthub package."""
    system_prompt_filename: str = Field(default='system_prompt.j2')
    """Filename of the system prompt template file within the agent's prompt directory. Defaults to 'system_prompt.j2'."""
    
    # Agent type and specialization
    agent_type: str = Field(default="advanced")
    """Agent type - options: "advanced", "expert", "specialist", "collaborative" """
    agent_specialization: str = Field(default="code")
    """Agent specialization - for specialist agents. Options: "code", "design", "architecture", "testing", "devops", "security", "data" """
    
    # Tool enablement
    enable_browsing: bool = Field(default=True)
    """Whether to enable browsing tool.
    Note: If using CLIRuntime, browsing is not implemented and should be disabled."""
    enable_llm_editor: bool = Field(default=True)
    """Whether to enable LLM editor tool"""
    enable_editor: bool = Field(default=True)
    """Whether to enable the standard editor tool (str_replace_editor), only has an effect if enable_llm_editor is False."""
    enable_jupyter: bool = Field(default=True)
    """Whether to enable Jupyter tool.
    Note: If using CLIRuntime, Jupyter use is not implemented and should be disabled."""
    enable_cmd: bool = Field(default=True)
    """Whether to enable bash tool"""
    enable_think: bool = Field(default=True)
    """Whether to enable think tool"""
    enable_finish: bool = Field(default=True)
    """Whether to enable finish tool"""
    enable_condensation_request: bool = Field(default=False)
    """Whether to enable condensation request tool"""
    enable_prompt_extensions: bool = Field(default=True)
    """Whether to enable prompt extensions"""
    enable_mcp: bool = Field(default=True)
    """Whether to enable MCP tools"""
    
    # Advanced browsing capabilities
    enable_advanced_browsing: bool = Field(default=True)
    """Whether to enable advanced browsing capabilities"""
    enable_visual_browsing: bool = Field(default=True)
    """Whether to enable visual browsing"""
    enable_browser_automation: bool = Field(default=True)
    """Whether to enable browser automation"""
    enable_som_visual_browsing: bool = Field(default=True)
    """Whether to enable SoM (Set of Marks) visual browsing."""
    
    # Advanced reasoning tools
    enable_planning: bool = Field(default=True)
    """Whether to enable planning capabilities"""
    enable_reflection: bool = Field(default=True)
    """Whether to enable reflection capabilities"""
    enable_self_correction: bool = Field(default=True)
    """Whether to enable self-correction capabilities"""
    enable_code_review: bool = Field(default=True)
    """Whether to enable code review capabilities"""
    
    # Multi-agent collaboration
    enable_multi_agent: bool = Field(default=True)
    """Whether to enable multi-agent collaboration"""
    max_collaborative_agents: int = Field(default=4)
    """Maximum number of collaborative agents (2-10)"""
    
    # Learning and memory
    enable_continuous_learning: bool = Field(default=True)
    """Whether to enable continuous learning from past experiences"""
    enable_persistent_memory: bool = Field(default=True)
    """Whether to enable project memory persistence across sessions"""
    memory_retention_days: int = Field(default=90)
    """Number of days to retain memory"""
    enable_history_truncation: bool = Field(default=True)
    """Whether history should be truncated to continue the session when hitting LLM context length limit."""
    
    # Code generation capabilities
    enable_code_generation: bool = Field(default=True)
    """Whether to enable advanced code generation"""
    enable_test_generation: bool = Field(default=True)
    """Whether to enable test generation"""
    enable_documentation_generation: bool = Field(default=True)
    """Whether to enable documentation generation"""
    
    # Project management
    enable_project_management: bool = Field(default=True)
    """Whether to enable project management capabilities"""
    enable_task_tracking: bool = Field(default=True)
    """Whether to enable task tracking"""
    enable_progress_reporting: bool = Field(default=True)
    """Whether to enable progress reporting"""
    
    # Microagents
    enable_all_microagents: bool = Field(default=True)
    """Whether to enable all microagents by default"""
    disabled_microagents: list[str] = Field(default_factory=list)
    """A list of microagents to disable (by name, without .py extension, e.g. ["github", "lint"]). Default is empty list."""
    condenser: CondenserConfig = Field(
        default_factory=lambda: NoOpCondenserConfig(type='noop')
    )
    extended: ExtendedConfig = Field(default_factory=lambda: ExtendedConfig({}))
    """Extended configuration for the agent."""

    model_config = ConfigDict(extra='forbid')

    @classmethod
    def from_toml_section(cls, data: dict) -> dict[str, AgentConfig]:
        """Create a mapping of AgentConfig instances from a toml dictionary representing the [agent] section.

        The default configuration is built from all non-dict keys in data.
        Then, each key with a dict value is treated as a custom agent configuration, and its values override
        the default configuration.

        Example:
        Apply generic agent config with custom agent overrides, e.g.
            [agent]
            enable_prompt_extensions = false
            [agent.BrowsingAgent]
            enable_prompt_extensions = true
        results in prompt_extensions being true for BrowsingAgent but false for others.

        Returns:
            dict[str, AgentConfig]: A mapping where the key "agent" corresponds to the default configuration
            and additional keys represent custom configurations.
        """
        # Initialize the result mapping
        agent_mapping: dict[str, AgentConfig] = {}

        # Extract base config data (non-dict values)
        base_data = {}
        custom_sections: dict[str, dict] = {}
        for key, value in data.items():
            if isinstance(value, dict):
                custom_sections[key] = value
            else:
                base_data[key] = value

        # Try to create the base config
        try:
            base_config = cls.model_validate(base_data)
            agent_mapping['agent'] = base_config
        except ValidationError as e:
            logger.warning(f'Invalid base agent configuration: {e}. Using defaults.')
            # If base config fails, create a default one
            base_config = cls()
            # Still add it to the mapping
            agent_mapping['agent'] = base_config

        # Process each custom section independently
        for name, overrides in custom_sections.items():
            try:
                # Merge base config with overrides
                merged = {**base_config.model_dump(), **overrides}
                if merged.get('classpath'):
                    # if an explicit classpath is given, try to load it and look up its config model class
                    from openhands.controller.agent import Agent

                    try:
                        agent_cls = get_impl(Agent, merged.get('classpath'))
                        custom_config = agent_cls.config_model.model_validate(merged)
                    except Exception as e:
                        logger.warning(
                            f'Failed to load custom agent class [{merged.get("classpath")}]: {e}. Using default config model.'
                        )
                        custom_config = cls.model_validate(merged)
                else:
                    # otherwise, try to look up the agent class by name (i.e. if it's a built-in)
                    # if that fails, just use the default AgentConfig class.
                    try:
                        agent_cls = Agent.get_cls(name)
                        custom_config = agent_cls.config_model.model_validate(merged)
                    except Exception:
                        # otherwise, just fall back to the default config model
                        custom_config = cls.model_validate(merged)
                agent_mapping[name] = custom_config
            except ValidationError as e:
                logger.warning(
                    f'Invalid agent configuration for [{name}]: {e}. This section will be skipped.'
                )
                # Skip this custom section but continue with others
                continue

        return agent_mapping
