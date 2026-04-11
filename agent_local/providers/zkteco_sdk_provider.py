import ctypes
import logging
import os
import platform
from typing import Dict, List

from config import AgentConfig
from models import DeviceStatus, ProviderResult
from providers.base import BaseFingerprintProvider

log = logging.getLogger(__name__)


class ZKTecoSDKProvider(BaseFingerprintProvider):
    """
    IMPORTANT

    This class is the only part you may need to adapt against the exact ZKTeco SDK package
    you downloaded for your scanner model.

    Why adaptation may still be required:
    - DLL / SO filenames vary by package
    - exported function names can vary by SDK build
    - scanner families can have different initialization flows

    The rest of the agent is complete. Once this adapter is aligned with your real SDK,
    the full end-to-end flow works with the Frappe app already provided.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.templates = {}
        self.lib = None

    def initialize(self) -> None:
        lib_path = self.config.sdk_library_path
        if not lib_path:
            raise RuntimeError("sdk_library_path is required for provider=zkteco_sdk")
        if not os.path.exists(lib_path):
            raise RuntimeError(f"SDK library not found: {lib_path}")

        system_name = platform.system().lower()
        if "windows" in system_name:
            self.lib = ctypes.WinDLL(lib_path)
        else:
            self.lib = ctypes.CDLL(lib_path)

        log.info("Loaded ZKTeco SDK library: %s", lib_path)

        # NOTE:
        # Insert the exact SDK initialization calls here according to the vendor sample.
        # Typical responsibilities:
        # - initialize SDK runtime
        # - enumerate readers
        # - open default reader
        # - set capture parameters

    def get_device_status(self) -> DeviceStatus:
        # Replace this with the real SDK device enumeration logic.
        connected = self.lib is not None
        return DeviceStatus(
            connected=connected,
            scanner_name="ZKTeco Scanner (adapter placeholder)",
            scanner_model="Detected via SDK wrapper",
        )

    def sync_templates(self, templates: List[Dict]) -> None:
        # Cache templates locally for identify operations.
        self.templates = {t["biometric_id"]: t for t in templates}
        log.info("Templates synced from server: %s", len(self.templates))

        # NOTE:
        # If your SDK supports loading templates into a native matcher DB,
        # do it here.

    def identify(self) -> ProviderResult:
        # NOTE:
        # Replace the block below with the real SDK capture + match sequence.
        #
        # Expected flow:
        # 1. capture fingerprint image/template from scanner
        # 2. compare against self.templates using SDK matcher
        # 3. return matched biometric_id with confidence
        #
        # The placeholder below intentionally fails loudly so that production
        # use does not silently pretend hardware is working.
        return ProviderResult(
            success=False,
            confidence=0.0,
            message="zkteco_sdk provider loaded, but identify() must be mapped to your exact SDK sample functions",
        )

    def enroll(self, target_user: str) -> ProviderResult:
        # NOTE:
        # Replace with real SDK enroll sequence:
        # 1. capture enough impressions
        # 2. merge into a final template
        # 3. serialize to base64
        #
        # Return value must contain template_data and biometric_id.
        return ProviderResult(
            success=False,
            confidence=0.0,
            message="zkteco_sdk provider loaded, but enroll() must be mapped to your exact SDK sample functions",
        )
