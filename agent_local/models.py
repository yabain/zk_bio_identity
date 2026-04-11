from dataclasses import dataclass
from typing import Optional


@dataclass
class DeviceStatus:
    connected: bool
    scanner_name: Optional[str] = None
    scanner_model: Optional[str] = None


@dataclass
class ProviderResult:
    success: bool
    biometric_id: Optional[str] = None
    template_data: Optional[str] = None
    template_format: str = "base64"
    quality_score: int = 0
    confidence: float = 0.0
    message: str = ""
    user: Optional[str] = None
