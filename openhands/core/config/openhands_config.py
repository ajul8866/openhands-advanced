import os
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from openhands.core import logger
from openhands.core.config.agent_config import AgentConfig
from openhands.core.config.cli_config import CLIConfig
from openhands.core.config.config_utils import (
    OH_DEFAULT_AGENT,
    OH_MAX_ITERATIONS,
    model_defaults_to_dict,
)
from openhands.core.config.extended_config import ExtendedConfig
from openhands.core.config.kubernetes_config import KubernetesConfig
from openhands.core.config.llm_config import LLMConfig
from openhands.core.config.mcp_config import MCPConfig
from openhands.core.config.sandbox_config import SandboxConfig
from openhands.core.config.security_config import SecurityConfig


class OpenHandsConfig(BaseModel):
    """Configuration for the advanced OpenHands AI agent platform.

    Attributes:
        llms: Dictionary mapping LLM names to their configurations.
            The default configuration is stored under the 'llm' key.
        agents: Dictionary mapping agent names to their configurations.
            The default configuration is stored under the 'agent' key.
        default_agent: Name of the default agent to use.
        sandbox: Sandbox configuration settings.
        runtime: Runtime environment identifier.
        file_store: Type of file store to use.
        file_store_path: Path to the file store.
        file_store_web_hook_url: Optional url for file store web hook
        file_store_web_hook_headers: Optional headers for file_store web hook
        save_trajectory_path: Either a folder path to store trajectories with auto-generated filenames, or a designated trajectory file path.
        save_screenshots_in_trajectory: Whether to save screenshots in trajectory (in encoded image format).
        replay_trajectory_path: Path to load trajectory and replay. If provided, trajectory would be replayed first before user's instruction.
        search_api_key: API key for Tavily search engine (https://tavily.com/).
        workspace_base (deprecated): Base path for the workspace. Defaults to `./workspace` as absolute path.
        workspace_mount_path (deprecated): Path to mount the workspace. Defaults to `workspace_base`.
        workspace_mount_path_in_sandbox (deprecated): Path to mount the workspace in sandbox. Defaults to `/workspace`.
        workspace_mount_rewrite (deprecated): Path to rewrite the workspace mount path.
        cache_dir: Path to cache directory. Defaults to `/tmp/cache`.
        run_as_openhands: Whether to run as openhands.
        max_iterations: Maximum number of iterations allowed.
        max_budget_per_task: Maximum budget per task, agent stops if exceeded.
        disable_color: Whether to disable terminal colors. For terminals that don't support color.
        debug: Whether to enable debugging mode.
        
        # Advanced features for commercial projects
        enable_advanced_reasoning: Whether to enable advanced reasoning capabilities.
        reasoning_effort: The effort to put into reasoning (low, medium, high, very_high).
        enable_multi_agent: Whether to enable multi-agent collaboration.
        max_collaborative_agents: Maximum number of collaborative agents (2-10).
        enable_continuous_learning: Whether to enable continuous learning from past experiences.
        enable_persistent_memory: Whether to enable project memory persistence across sessions.
        memory_retention_days: Number of days to retain memory.
        max_context_window: Maximum context window size (in tokens).
        enable_code_optimization: Whether to enable automatic code optimization.
        enable_model_fallback: Whether to enable model fallback chain.
        fallback_models: List of fallback models to try if primary fails.
        enable_chain_of_thought: Whether to enable chain of thought reasoning.
        enable_tree_of_thought: Whether to enable tree of thought reasoning.
        enable_context_compression: Whether to enable context compression.
        enable_semantic_chunking: Whether to enable semantic chunking.
        enable_advanced_browsing: Whether to enable advanced browsing capabilities.
        enable_visual_browsing: Whether to enable visual browsing.
        enable_browser_automation: Whether to enable browser automation.
        enable_planning: Whether to enable planning capabilities.
        enable_reflection: Whether to enable reflection capabilities.
        enable_self_correction: Whether to enable self-correction capabilities.
        enable_code_review: Whether to enable code review capabilities.
        enable_code_generation: Whether to enable advanced code generation.
        enable_test_generation: Whether to enable test generation.
        enable_documentation_generation: Whether to enable documentation generation.
        enable_project_management: Whether to enable project management capabilities.
        enable_task_tracking: Whether to enable task tracking.
        enable_progress_reporting: Whether to enable progress reporting.
        enable_distributed_computing: Whether to enable distributed computing.
        max_distributed_nodes: Maximum number of distributed computing nodes.
        enable_advanced_context_management: Whether to enable advanced context management.
        enable_semantic_memory: Whether to enable semantic memory.
        enable_hierarchical_memory: Whether to enable hierarchical memory organization.
        memory_prioritization: Memory prioritization strategy.
        enable_memory_compression: Whether to enable memory compression.
        enable_context_aware_retrieval: Whether to enable context-aware memory retrieval.
        enable_memory_indexing: Whether to enable memory indexing.
        enable_cross_session_memory: Whether to enable cross-session memory persistence.
        file_uploads_max_file_size_mb: Maximum file upload size in MB. `0` means unlimited.
        file_uploads_restrict_file_types: Whether to restrict upload file types.
        file_uploads_allowed_extensions: Allowed file extensions. `['.*']` allows all.
        cli_multiline_input: Whether to enable multiline input in CLI. When disabled,
            input is read line by line. When enabled, input continues until /exit command.
        mcp_host: Host for OpenHands' default MCP server
        mcp: MCP configuration settings.
    """

    llms: dict[str, LLMConfig] = Field(default_factory=dict)
    agents: dict[str, AgentConfig] = Field(default_factory=dict)
    default_agent: str = Field(default=OH_DEFAULT_AGENT)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    extended: ExtendedConfig = Field(default_factory=lambda: ExtendedConfig({}))
    runtime: str = Field(default='docker')
    file_store: str = Field(default='local')
    file_store_path: str = Field(default='~/.openhands')
    file_store_web_hook_url: str | None = Field(default=None)
    file_store_web_hook_headers: dict | None = Field(default=None)
    save_trajectory_path: str | None = Field(default=None)
    save_screenshots_in_trajectory: bool = Field(default=False)
    replay_trajectory_path: str | None = Field(default=None)
    search_api_key: SecretStr | None = Field(
        default=None,
        description='API key for Tavily search engine (https://tavily.com/). Required for search functionality.',
    )

    # Deprecated parameters - will be removed in a future version
    workspace_base: str | None = Field(default=None, deprecated=True)
    workspace_mount_path: str | None = Field(default=None, deprecated=True)
    workspace_mount_path_in_sandbox: str = Field(default='/workspace', deprecated=True)
    workspace_mount_rewrite: str | None = Field(default=None, deprecated=True)
    # End of deprecated parameters

    cache_dir: str = Field(default='/tmp/cache')
    run_as_openhands: bool = Field(default=True)
    max_iterations: int = Field(default=OH_MAX_ITERATIONS)
    max_budget_per_task: float | None = Field(default=None)

    disable_color: bool = Field(default=False)
    jwt_secret: SecretStr | None = Field(default=None)
    debug: bool = Field(default=False)
    file_uploads_max_file_size_mb: int = Field(default=0)
    file_uploads_restrict_file_types: bool = Field(default=False)
    file_uploads_allowed_extensions: list[str] = Field(default_factory=lambda: ['.*'])

    cli_multiline_input: bool = Field(default=False)
    conversation_max_age_seconds: int = Field(default=864000)  # 10 days in seconds
    enable_default_condenser: bool = Field(default=True)
    max_concurrent_conversations: int = Field(
        default=3
    )  # Maximum number of concurrent agent loops allowed per user
    mcp_host: str = Field(default=f'localhost:{os.getenv("port", 3000)}')
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    kubernetes: KubernetesConfig = Field(default_factory=KubernetesConfig)
    cli: CLIConfig = Field(default_factory=CLIConfig)
    
    # Advanced features for commercial projects
    enable_advanced_reasoning: bool = Field(default=True, description="Whether to enable advanced reasoning capabilities")
    reasoning_effort: str = Field(default="high", description="The effort to put into reasoning (low, medium, high, very_high)")
    enable_multi_agent: bool = Field(default=True, description="Whether to enable multi-agent collaboration")
    max_collaborative_agents: int = Field(default=4, description="Maximum number of collaborative agents (2-10)")
    enable_continuous_learning: bool = Field(default=True, description="Whether to enable continuous learning from past experiences")
    enable_persistent_memory: bool = Field(default=True, description="Whether to enable project memory persistence across sessions")
    memory_retention_days: int = Field(default=90, description="Number of days to retain memory")
    max_context_window: int = Field(default=128000, description="Maximum context window size (in tokens)")
    enable_code_optimization: bool = Field(default=True, description="Whether to enable automatic code optimization")
    enable_model_fallback: bool = Field(default=True, description="Whether to enable model fallback chain")
    fallback_models: list[str] = Field(default_factory=lambda: ["gpt-4o-2024", "claude-3-opus", "gemini-1.5-pro", "gpt-4-turbo"], description="List of fallback models to try if primary fails")
    enable_chain_of_thought: bool = Field(default=True, description="Whether to enable chain of thought reasoning")
    enable_tree_of_thought: bool = Field(default=True, description="Whether to enable tree of thought reasoning")
    enable_context_compression: bool = Field(default=True, description="Whether to enable context compression")
    enable_semantic_chunking: bool = Field(default=True, description="Whether to enable semantic chunking")
    enable_advanced_browsing: bool = Field(default=True, description="Whether to enable advanced browsing capabilities")
    enable_visual_browsing: bool = Field(default=True, description="Whether to enable visual browsing")
    enable_browser_automation: bool = Field(default=True, description="Whether to enable browser automation")
    enable_planning: bool = Field(default=True, description="Whether to enable planning capabilities")
    enable_reflection: bool = Field(default=True, description="Whether to enable reflection capabilities")
    enable_self_correction: bool = Field(default=True, description="Whether to enable self-correction capabilities")
    enable_code_review: bool = Field(default=True, description="Whether to enable code review capabilities")
    enable_code_generation: bool = Field(default=True, description="Whether to enable advanced code generation")
    enable_test_generation: bool = Field(default=True, description="Whether to enable test generation")
    enable_documentation_generation: bool = Field(default=True, description="Whether to enable documentation generation")
    enable_project_management: bool = Field(default=True, description="Whether to enable project management capabilities")
    enable_task_tracking: bool = Field(default=True, description="Whether to enable task tracking")
    enable_progress_reporting: bool = Field(default=True, description="Whether to enable progress reporting")
    enable_distributed_computing: bool = Field(default=True, description="Whether to enable distributed computing")
    max_distributed_nodes: int = Field(default=4, description="Maximum number of distributed computing nodes")
    enable_advanced_context_management: bool = Field(default=True, description="Whether to enable advanced context management")
    enable_semantic_memory: bool = Field(default=True, description="Whether to enable semantic memory")
    enable_hierarchical_memory: bool = Field(default=True, description="Whether to enable hierarchical memory organization")
    memory_prioritization: str = Field(default="hybrid", description="Memory prioritization strategy")
    enable_memory_compression: bool = Field(default=True, description="Whether to enable memory compression")
    enable_context_aware_retrieval: bool = Field(default=True, description="Whether to enable context-aware memory retrieval")
    enable_memory_indexing: bool = Field(default=True, description="Whether to enable memory indexing")
    enable_cross_session_memory: bool = Field(default=True, description="Whether to enable cross-session memory persistence")

    defaults_dict: ClassVar[dict] = {}

    model_config = ConfigDict(extra='forbid')

    def get_llm_config(self, name: str = 'llm') -> LLMConfig:
        """'llm' is the name for default config (for backward compatibility prior to 0.8)."""
        if name in self.llms:
            return self.llms[name]
        if name is not None and name != 'llm':
            logger.openhands_logger.warning(
                f'llm config group {name} not found, using default config'
            )
        if 'llm' not in self.llms:
            self.llms['llm'] = LLMConfig()
        return self.llms['llm']

    def set_llm_config(self, value: LLMConfig, name: str = 'llm') -> None:
        self.llms[name] = value

    def get_agent_config(self, name: str = 'agent') -> AgentConfig:
        """'agent' is the name for default config (for backward compatibility prior to 0.8)."""
        if name in self.agents:
            return self.agents[name]
        if 'agent' not in self.agents:
            self.agents['agent'] = AgentConfig()
        return self.agents['agent']

    def set_agent_config(self, value: AgentConfig, name: str = 'agent') -> None:
        self.agents[name] = value

    def get_agent_to_llm_config_map(self) -> dict[str, LLMConfig]:
        """Get a map of agent names to llm configs."""
        return {name: self.get_llm_config_from_agent(name) for name in self.agents}

    def get_llm_config_from_agent(self, name: str = 'agent') -> LLMConfig:
        agent_config: AgentConfig = self.get_agent_config(name)
        llm_config_name = (
            agent_config.llm_config if agent_config.llm_config is not None else 'llm'
        )
        return self.get_llm_config(llm_config_name)

    def get_agent_configs(self) -> dict[str, AgentConfig]:
        return self.agents

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook, called when the instance is created with only default values."""
        super().model_post_init(__context)

        if not OpenHandsConfig.defaults_dict:  # Only set defaults_dict if it's empty
            OpenHandsConfig.defaults_dict = model_defaults_to_dict(self)
