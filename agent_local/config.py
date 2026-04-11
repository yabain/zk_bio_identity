from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class AgentConfig:
    site_url: str
    api_key: str
    api_secret: str
    device_id: str
    device_name: str
    provider: str = "mock"
    sdk_library_path: str = ""
    poll_interval_seconds: int = 3
    heartbeat_interval_seconds: int = 15
    templates_refresh_seconds: int = 60
    request_timeout_seconds: int = 20
    mock_identify_biometric_id: str = ""
    mock_enroll_prefix: str = "MOCK-"


def load_config(path: str) -> AgentConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return AgentConfig(**raw)
