from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import json
import os

class LanguageConfig(BaseModel):
    """Base configuration for language servers."""
    enabled: bool = True
    server_path: str
    server_args: list[str]
    timeout: int = 30
    max_memory: int = 512  # MB
    max_cpu_percent: int = 80
    format_on_save: bool = True
    diagnostics_on_save: bool = True
    completion_on_type: bool = True

class PythonConfig(LanguageConfig):
    """Python language server configuration."""
    type_checking_mode: str = "basic"
    python_version: str = "3.9"
    stub_directories: list[str] = []
    extra_paths: list[str] = []
    use_pyright: bool = True
    use_pylance: bool = False
    strict_mode: bool = True
    report_missing_imports: bool = True
    report_missing_type_stubs: bool = True

class TypeScriptConfig(LanguageConfig):
    """TypeScript/JavaScript language server configuration."""
    target_version: str = "ES2020"
    module_resolution: str = "node"
    strict_mode: bool = True
    path_mappings: Dict[str, str] = {}
    jsx_support: bool = True
    jsx_mode: str = "react"
    experimental_decorators: bool = True
    use_workspace_tsdk: bool = True

class JavaConfig(LanguageConfig):
    """Java language server configuration."""
    jdk_version: str = "17"
    classpath: list[str] = []
    source_paths: list[str] = []
    annotation_processing: bool = True
    lombok_support: bool = True
    gradle_support: bool = True
    maven_support: bool = True
    project_references: list[str] = []

class GoConfig(LanguageConfig):
    """Go language server configuration."""
    gopath: str = os.getenv("GOPATH", "")
    build_tags: list[str] = []
    format_settings: Dict[str, Any] = {
        "tabSize": 4,
        "insertSpaces": False
    }
    analysis_settings: Dict[str, bool] = {
        "unusedparams": True,
        "shadow": True,
        "staticcheck": True
    }
    use_gopls: bool = True
    go_version: str = "1.21"

class RustConfig(LanguageConfig):
    """Rust language server configuration."""
    edition: str = "2021"
    target: str = "debug"
    cargo_features: list[str] = []
    analysis_settings: Dict[str, bool] = {
        "clippy": True,
        "rustfmt": True,
        "inlay_hints": True
    }
    rustup_toolchain: str = "stable"
    use_rust_analyzer: bool = True

class CppConfig(LanguageConfig):
    """C++ language server configuration."""
    compilation_database: Optional[str] = None
    format_style: str = "Google"
    include_paths: list[str] = []
    compiler_flags: list[str] = []
    cpp_standard: str = "c++17"
    use_clangd: bool = True
    background_index: bool = True
    index_headers: bool = True

class PHPConfig(LanguageConfig):
    """PHP language server configuration."""
    php_version: str = "8.1"
    include_paths: list[str] = []
    format_settings: Dict[str, Any] = {
        "tabSize": 4,
        "insertSpaces": True
    }
    analysis_settings: Dict[str, bool] = {
        "diagnostics": True,
        "completion": True,
        "hover": True
    }
    use_intelephense: bool = True
    stubs: list[str] = ["apache", "php", "wordpress"]

class LanguageConfigManager:
    """Manages language server configurations."""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".ade" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs: Dict[str, LanguageConfig] = {}
        self._load_configs()

    def _load_configs(self):
        """Load configurations from disk."""
        config_file = self.config_dir / "language_config.json"
        if config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)
                self._parse_configs(config_data)
        else:
            self._create_default_configs()

    def _parse_configs(self, config_data: Dict[str, Any]):
        """Parse configuration data into LanguageConfig objects."""
        config_classes = {
            "python": PythonConfig,
            "typescript": TypeScriptConfig,
            "javascript": TypeScriptConfig,
            "java": JavaConfig,
            "go": GoConfig,
            "rust": RustConfig,
            "cpp": CppConfig,
            "php": PHPConfig
        }
        
        for lang, data in config_data.items():
            if lang in config_classes:
                self.configs[lang] = config_classes[lang](**data)

    def _create_default_configs(self):
        """Create default configurations for all supported languages."""
        self.configs = {
            "python": PythonConfig(),
            "typescript": TypeScriptConfig(),
            "javascript": TypeScriptConfig(),
            "java": JavaConfig(),
            "go": GoConfig(),
            "rust": RustConfig(),
            "cpp": CppConfig(),
            "php": PHPConfig()
        }
        self.save_configs()

    def get_config(self, language: str) -> Optional[LanguageConfig]:
        """Get configuration for a specific language."""
        return self.configs.get(language.lower())

    def update_config(self, language: str, config: Dict[str, Any]):
        """Update configuration for a specific language."""
        lang = language.lower()
        if lang in self.configs:
            current_config = self.configs[lang]
            updated_config = current_config.copy(update=config)
            self.configs[lang] = updated_config
            self.save_configs()
            return True
        return False

    def save_configs(self):
        """Save all configurations to disk."""
        config_data = {
            lang: config.dict()
            for lang, config in self.configs.items()
        }
        config_file = self.config_dir / "language_config.json"
        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=2)

    def reset_config(self, language: str):
        """Reset configuration for a specific language to defaults."""
        lang = language.lower()
        if lang in self.configs:
            default_configs = {
                "python": PythonConfig(),
                "typescript": TypeScriptConfig(),
                "javascript": TypeScriptConfig(),
                "java": JavaConfig(),
                "go": GoConfig(),
                "rust": RustConfig(),
                "cpp": CppConfig(),
                "php": PHPConfig()
            }
            if lang in default_configs:
                self.configs[lang] = default_configs[lang]
                self.save_configs()
                return True
        return False

    def reset_all_configs(self):
        """Reset all configurations to defaults."""
        self._create_default_configs() 