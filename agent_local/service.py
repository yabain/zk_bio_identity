import logging
import time

from config import AgentConfig
from frappe_client import FrappeClient
from providers.factory import build_provider

log = logging.getLogger(__name__)
AGENT_VERSION = "0.1.0"


class AgentService:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = FrappeClient(
            site_url=config.site_url,
            api_key=config.api_key,
            api_secret=config.api_secret,
            timeout=config.request_timeout_seconds,
        )
        self.provider = build_provider(config)
        self.last_heartbeat = 0.0
        self.last_template_refresh = 0.0

    def bootstrap(self):
        self.provider.initialize()
        status = self.provider.get_device_status()
        self.client.register_device(
            device_id=self.config.device_id,
            device_name=self.config.device_name,
            provider=self.config.provider,
            scanner_model=status.scanner_model,
            os_type="local-agent",
            agent_version=AGENT_VERSION,
        )
        self.refresh_templates(force=True)
        self.send_heartbeat(force=True)
        log.info("Agent bootstrap completed.")

    def send_heartbeat(self, force: bool = False):
        now = time.time()
        if not force and (now - self.last_heartbeat) < self.config.heartbeat_interval_seconds:
            return
        status = self.provider.get_device_status()
        self.client.heartbeat(
            device_id=self.config.device_id,
            scanner_connected=1 if status.connected else 0,
            scanner_detected_name=status.scanner_name,
            scanner_model=status.scanner_model,
            meta='{"agent_version":"%s"}' % AGENT_VERSION,
        )
        self.last_heartbeat = now
        log.info("Heartbeat sent. connected=%s", status.connected)

    def refresh_templates(self, force: bool = False):
        now = time.time()
        if not force and (now - self.last_template_refresh) < self.config.templates_refresh_seconds:
            return
        templates = self.client.get_active_templates(device_id=self.config.device_id) or []
        self.provider.sync_templates(templates)
        self.last_template_refresh = now
        log.info("Templates refreshed: %s", len(templates))

    def handle_pending_session(self):
        session = self.client.get_pending_session(device_id=self.config.device_id)
        if not session:
            return
        log.info("Handling session %s (%s)", session["name"], session["session_type"])

        if session["session_type"] == "Enroll":
            result = self.provider.enroll(session.get("requested_for_user"))
        else:
            result = self.provider.identify()

        payload = {
            "success": result.success,
            "biometric_id": result.biometric_id,
            "template_data": result.template_data,
            "template_format": result.template_format,
            "quality_score": result.quality_score,
            "confidence": result.confidence,
            "message": result.message,
            "user": result.user,
        }

        response = self.client.submit_session_result(
            device_id=self.config.device_id,
            session_id=session["name"],
            result=payload,
        )
        log.info("Session submitted: %s", response)

        if session["session_type"] == "Enroll" and result.success:
            self.refresh_templates(force=True)

    def run_forever(self):
        self.bootstrap()
        while True:
            try:
                self.send_heartbeat()
                self.refresh_templates()
                self.handle_pending_session()
            except Exception as exc:
                log.exception("Agent loop error: %s", exc)
            time.sleep(self.config.poll_interval_seconds)
