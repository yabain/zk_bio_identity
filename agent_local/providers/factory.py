from config import AgentConfig
from providers.mock_provider import MockFingerprintProvider
from providers.zkteco_sdk_provider import ZKTecoSDKProvider


def build_provider(config: AgentConfig):
    if config.provider == "mock":
        return MockFingerprintProvider(config)
    if config.provider == "zkteco_sdk":
        return ZKTecoSDKProvider(config)
    raise ValueError(f"Unsupported provider: {config.provider}")
