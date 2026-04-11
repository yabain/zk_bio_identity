from abc import ABC, abstractmethod
from typing import Dict, List

from models import DeviceStatus, ProviderResult


class BaseFingerprintProvider(ABC):
    @abstractmethod
    def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_device_status(self) -> DeviceStatus:
        raise NotImplementedError

    @abstractmethod
    def sync_templates(self, templates: List[Dict]) -> None:
        raise NotImplementedError

    @abstractmethod
    def identify(self) -> ProviderResult:
        raise NotImplementedError

    @abstractmethod
    def enroll(self, target_user: str) -> ProviderResult:
        raise NotImplementedError
