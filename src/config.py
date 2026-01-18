
# src/config.py
import os
from pathlib import Path
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class SystemConfig(BaseModel):
    global_cooldown: int = Field(default=30, ge=1)
    max_retries: int = Field(default=3, ge=1)
    input_char_limit: int = Field(default=10000, ge=1)

class PathsConfig(BaseModel):
    output_dir: str

class PromptsConfig(BaseModel):
    architect: str
    stripper: str
    worker: str
    judge: str

class AppConfig(BaseModel):
    system: SystemConfig
    paths: PathsConfig
    prompts: PromptsConfig

def load_config(config_path: str = "config/core.yaml") -> AppConfig:
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    return AppConfig(**config_data)

# Load the configuration once when the module is imported
CONFIG = load_config()