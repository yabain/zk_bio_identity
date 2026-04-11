import json
import logging
from typing import Any, Dict, Optional

import requests

log = logging.getLogger(__name__)


class FrappeClient:
    def __init__(self, site_url: str, api_key: str, api_secret: str, timeout: int = 20):
        self.site_url = site_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def call(self, method: str, **kwargs) -> Any:
        url = f"{self.site_url}/api/method/{method}"
        resp = self.session.post(url, data=json.dumps(kwargs), timeout=self.timeout)
        resp.raise_for_status()
        payload = resp.json()
        if "message" in payload:
            return payload["message"]
        return payload

    def register_device(self, **kwargs):
        return self.call("zk_bio_identity.api.register_or_update_device", **kwargs)

    def heartbeat(self, **kwargs):
        return self.call("zk_bio_identity.api.heartbeat", **kwargs)

    def get_pending_session(self, device_id: str):
        return self.call("zk_bio_identity.api.get_pending_session", device_id=device_id)

    def get_active_templates(self, device_id: Optional[str] = None):
        return self.call("zk_bio_identity.api.get_active_templates", device_id=device_id)

    def submit_session_result(self, device_id: str, session_id: str, result: Dict[str, Any]):
        return self.call(
            "zk_bio_identity.api.submit_session_result",
            device_id=device_id,
            session_id=session_id,
            result=json.dumps(result),
        )
