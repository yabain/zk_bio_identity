import base64
import hashlib
import logging
from typing import Dict, List

from config import AgentConfig
from models import DeviceStatus, ProviderResult
from providers.base import BaseFingerprintProvider

log = logging.getLogger(__name__)


class MockFingerprintProvider(BaseFingerprintProvider):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.templates = {}

    def initialize(self) -> None:
        log.info("Mock provider initialized.")

    def get_device_status(self) -> DeviceStatus:
        return DeviceStatus(connected=True, scanner_name="Mock Scanner", scanner_model="MOCK-1")

    def sync_templates(self, templates: List[Dict]) -> None:
        self.templates = {t["biometric_id"]: t for t in templates}
        log.info("Mock templates synced: %s", len(self.templates))

    def identify(self) -> ProviderResult:
        biometric_id = self.config.mock_identify_biometric_id
        if biometric_id:
            if biometric_id in self.templates:
                return ProviderResult(
                    success=True,
                    biometric_id=biometric_id,
                    confidence=0.99,
                    message="Mock identify matched configured biometric_id",
                )
            return ProviderResult(
                success=False,
                biometric_id=biometric_id,
                confidence=0.1,
                message="Mock identify: configured biometric_id not found",
            )

        if len(self.templates) == 1:
            biometric_id = list(self.templates.keys())[0]
            return ProviderResult(success=True, biometric_id=biometric_id, confidence=0.95, message="Mock identify matched single template")

        return ProviderResult(success=False, confidence=0.0, message="Mock identify requires mock_identify_biometric_id or exactly one enrolled template")

    def enroll(self, target_user: str) -> ProviderResult:
        raw = f"{self.config.mock_enroll_prefix}{target_user}".encode("utf-8")
        biometric_id = hashlib.sha1(raw).hexdigest()[:12].upper()
        template_data = base64.b64encode(raw).decode("ascii")
        return ProviderResult(
            success=True,
            biometric_id=biometric_id,
            template_data=template_data,
            template_format="base64",
            quality_score=90,
            confidence=1.0,
            message="Mock enrollment completed",
        )
