import json
from typing import Any, Dict, List, Optional

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime
from frappe.utils.password import get_decrypted_password


ALLOWED_DESK_ROLES = {"System Manager", "Biometric Manager", "Biometric Operator"}


def check_app_permission():
    return frappe.session.user != "Guest"


def _require_operator():
    roles = set(frappe.get_roles())
    if not roles.intersection(ALLOWED_DESK_ROLES):
        frappe.throw(_("You are not allowed to use the biometric app."), frappe.PermissionError)


def _safe_json_loads(value: Any, default: Any):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return default
    return default


def _get_settings_doc():
    return frappe.get_single("ZK Bio Settings")


def _get_employee_for_user(user: Optional[str]) -> Optional[str]:
    if not user:
        return None
    if frappe.db.exists("DocType", "Employee"):
        return frappe.db.get_value("Employee", {"user_id": user}, "name")
    return None


def _update_user_biometric_fields(user: str, biometric_id: str, status: str, device: Optional[str] = None):
    values = {
        "custom_biometric_id": biometric_id,
        "custom_biometric_status": status,
        "custom_last_biometric_enrollment_on": now_datetime(),
    }
    if device:
        values["custom_default_biometric_device"] = device
    frappe.db.set_value("User", user, values, update_modified=True)


def _resolve_log_type(employee: str) -> Optional[str]:
    settings = _get_settings_doc()
    mode = settings.checkin_mode or "Alternating"

    if mode == "Always IN":
        return "IN"
    if mode == "Always OUT":
        return "OUT"

    if not frappe.db.exists("DocType", "Employee Checkin"):
        return None

    last_log = frappe.db.get_value(
        "Employee Checkin",
        {"employee": employee},
        ["name", "log_type"],
        order_by="time desc",
        as_dict=True,
    )
    if not last_log or not last_log.log_type or last_log.log_type == "OUT":
        return "IN"
    return "OUT"


def _create_employee_checkin(user: str, biometric_id: str, session_name: Optional[str] = None) -> Optional[str]:
    if not frappe.db.exists("DocType", "Employee Checkin"):
        return None

    employee = _get_employee_for_user(user)
    if not employee:
        return None

    log_type = _resolve_log_type(employee)
    device_id = frappe.db.get_value("User", user, "custom_default_biometric_device")
    doc = frappe.get_doc(
        {
            "doctype": "Employee Checkin",
            "employee": employee,
            "time": now_datetime(),
            "device_id": biometric_id,
            "log_type": log_type,
            "skip_auto_attendance": 0,
        }
    )
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)

    _insert_event_log(
        event_type="checkin",
        device=device_id,
        user=user,
        employee=employee,
        biometric_id=biometric_id,
        matched=1,
        confidence=None,
        payload={"source_session": session_name, "employee_checkin": doc.name, "log_type": log_type},
        status="success",
    )
    return doc.name


def _insert_event_log(
    event_type: str,
    device: Optional[str] = None,
    user: Optional[str] = None,
    employee: Optional[str] = None,
    biometric_id: Optional[str] = None,
    matched: int = 0,
    confidence: Optional[float] = None,
    payload: Optional[dict] = None,
    status: str = "success",
):
    if not frappe.db.exists("DocType", "Biometric Event Log"):
        return

    doc = frappe.get_doc(
        {
            "doctype": "Biometric Event Log",
            "event_type": event_type,
            "device": device,
            "user": user,
            "employee": employee,
            "biometric_id": biometric_id,
            "matched": matched,
            "confidence": confidence,
            "event_time": now_datetime(),
            "status": status,
            "payload": frappe.as_json(payload or {}),
        }
    )
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_settings():
    _require_operator()
    settings = _get_settings_doc()
    return {
        "default_device": settings.default_device,
        "auto_create_employee_checkin": cint(settings.auto_create_employee_checkin),
        "checkin_mode": settings.checkin_mode,
        "heartbeat_timeout_seconds": cint(settings.heartbeat_timeout_seconds or 60),
        "result_poll_interval_ms": cint(settings.result_poll_interval_ms or 2000),
    }


@frappe.whitelist()
def list_devices():
    _require_operator()
    docs = frappe.get_all(
        "Biometric Device",
        fields=[
            "name",
            "device_id",
            "device_name",
            "provider",
            "scanner_model",
            "os_type",
            "agent_version",
            "last_seen_at",
            "last_status",
            "scanner_connected",
            "scanner_detected_name",
        ],
        order_by="modified desc",
    )
    return docs


@frappe.whitelist()
def search_users(txt: str = ""):
    _require_operator()
    filters = [["enabled", "=", 1], ["name", "not in", ["Guest", "Administrator"]]]
    if txt:
        filters.append(["full_name", "like", f"%{txt}%"])
    docs = frappe.get_all(
        "User",
        filters=filters,
        fields=["name", "full_name", "user_image", "custom_biometric_id", "custom_biometric_status"],
        limit=20,
        order_by="full_name asc",
    )
    return docs


@frappe.whitelist()
def get_user_profile(user: str):
    _require_operator()
    doc = frappe.get_doc("User", user)
    employee = _get_employee_for_user(user)
    employee_doc = frappe.get_doc("Employee", employee) if employee else None
    return {
        "user": doc.name,
        "full_name": doc.full_name,
        "email": doc.email,
        "enabled": doc.enabled,
        "user_image": doc.user_image,
        "biometric_id": getattr(doc, "custom_biometric_id", None),
        "biometric_status": getattr(doc, "custom_biometric_status", None),
        "employee": employee,
        "employee_name": employee_doc.employee_name if employee_doc else None,
        "designation": employee_doc.designation if employee_doc else None,
        "department": employee_doc.department if employee_doc else None,
        "company": employee_doc.company if employee_doc else None,
    }


def _new_session(session_type: str, device: Optional[str] = None, requested_for_user: Optional[str] = None):
    session = frappe.get_doc(
        {
            "doctype": "Biometric Scan Session",
            "session_type": session_type,
            "requested_by": frappe.session.user,
            "requested_for_user": requested_for_user,
            "device": device or _get_settings_doc().default_device,
            "status": "Pending",
            "started_on": now_datetime(),
        }
    )
    session.insert(ignore_permissions=True)
    return session


@frappe.whitelist()
def create_identify_session(device: Optional[str] = None):
    _require_operator()
    session = _new_session("Identify", device=device)
    return {"session": session.name, "device": session.device, "status": session.status}


@frappe.whitelist()
def create_enroll_session(user: str, device: Optional[str] = None):
    _require_operator()
    if not frappe.db.exists("User", user):
        frappe.throw(_("User not found."))
    session = _new_session("Enroll", device=device, requested_for_user=user)
    return {"session": session.name, "device": session.device, "status": session.status}


@frappe.whitelist()
def get_session(session: str):
    _require_operator()
    doc = frappe.get_doc("Biometric Scan Session", session)
    profile = None
    if doc.result_user:
        profile = get_user_profile(doc.result_user)
    return {
        "name": doc.name,
        "session_type": doc.session_type,
        "status": doc.status,
        "device": doc.device,
        "requested_for_user": doc.requested_for_user,
        "result_user": doc.result_user,
        "result_employee": doc.result_employee,
        "biometric_id": doc.biometric_id,
        "message": doc.message,
        "result_confidence": doc.result_confidence,
        "checkin_name": doc.checkin_name,
        "profile": profile,
    }


@frappe.whitelist()
def get_dashboard_stats():
    _require_operator()
    today_count = 0
    if frappe.db.exists("DocType", "Employee Checkin"):
        today_count = frappe.db.count("Employee Checkin", {"creation": [">=", now_datetime().date()]})

    devices = frappe.db.count("Biometric Device")
    active_credentials = frappe.db.count("Biometric Credential", {"is_active": 1})
    pending_sessions = frappe.db.count("Biometric Scan Session", {"status": "Pending"})
    success_events = frappe.db.count("Biometric Event Log", {"status": "success"})

    return {
        "devices": devices,
        "active_credentials": active_credentials,
        "pending_sessions": pending_sessions,
        "employee_checkins_today": today_count,
        "success_events": success_events,
    }


@frappe.whitelist()
def get_recent_event_logs(limit: int = 20):
    _require_operator()
    limit = cint(limit or 20)
    return frappe.get_all(
        "Biometric Event Log",
        fields=[
            "name",
            "event_type",
            "device",
            "user",
            "employee",
            "biometric_id",
            "matched",
            "confidence",
            "event_time",
            "status",
        ],
        order_by="event_time desc",
        limit=limit,
    )


@frappe.whitelist()
def register_or_update_device(
    device_id: str,
    device_name: Optional[str] = None,
    provider: str = "mock",
    scanner_model: Optional[str] = None,
    serial_no: Optional[str] = None,
    os_type: Optional[str] = None,
    agent_version: Optional[str] = None,
):
    if not device_id:
        frappe.throw(_("device_id is required"))

    name = device_id
    doc = frappe.get_doc("Biometric Device", name) if frappe.db.exists("Biometric Device", name) else frappe.new_doc("Biometric Device")
    doc.device_id = device_id
    doc.device_name = device_name or device_id
    doc.provider = provider
    doc.scanner_model = scanner_model
    doc.serial_no = serial_no
    doc.os_type = os_type
    doc.agent_version = agent_version
    doc.last_seen_at = now_datetime()
    doc.last_status = "Online"
    doc.flags.ignore_permissions = True
    if doc.is_new():
        doc.insert(ignore_permissions=True)
    else:
        doc.save(ignore_permissions=True)
    return {"name": doc.name, "status": doc.last_status}


@frappe.whitelist()
def heartbeat(
    device_id: str,
    scanner_connected: int = 0,
    scanner_detected_name: Optional[str] = None,
    scanner_model: Optional[str] = None,
    meta: Optional[str] = None,
):
    if not frappe.db.exists("Biometric Device", device_id):
        register_or_update_device(device_id=device_id, device_name=device_id)

    doc = frappe.get_doc("Biometric Device", device_id)
    doc.last_seen_at = now_datetime()
    doc.last_status = "Online"
    doc.scanner_connected = cint(scanner_connected)
    doc.scanner_detected_name = scanner_detected_name
    if scanner_model:
        doc.scanner_model = scanner_model
    doc.flags.ignore_permissions = True
    doc.save(ignore_permissions=True)

    _insert_event_log(
        event_type="heartbeat",
        device=device_id,
        matched=0,
        payload={"meta": _safe_json_loads(meta, {}), "scanner_connected": cint(scanner_connected)},
        status="success",
    )
    return {"ok": True, "device": device_id}


@frappe.whitelist()
def get_pending_session(device_id: str):
    filters = [["status", "=", "Pending"]]
    if device_id:
        filters.append(["device", "in", [device_id, "", None]])
    docs = frappe.get_all(
        "Biometric Scan Session",
        filters=filters,
        fields=["name", "session_type", "requested_for_user", "device", "status"],
        order_by="creation asc",
        limit=1,
    )
    if not docs:
        return None
    doc = docs[0]
    frappe.db.set_value("Biometric Scan Session", doc["name"], "status", "In Progress", update_modified=True)
    return doc


@frappe.whitelist()
def get_active_templates(device_id: Optional[str] = None):
    templates = []
    for row in frappe.get_all(
        "Biometric Credential",
        filters={"is_active": 1},
        fields=["name", "user", "employee", "biometric_id", "template_format", "device"],
        order_by="modified desc",
    ):
        row["template_data"] = get_decrypted_password("Biometric Credential", row["name"], "template_data")
        templates.append(row)
    return templates


@frappe.whitelist()
def submit_session_result(device_id: str, session_id: str, result: Any):
    payload = _safe_json_loads(result, {})
    session = frappe.get_doc("Biometric Scan Session", session_id)
    session.device = session.device or device_id
    session.finished_on = now_datetime()
    session.raw_payload = frappe.as_json(payload)

    if session.session_type == "Enroll":
        if not payload.get("success"):
            session.status = "Failed"
            session.message = payload.get("message") or "Enrollment failed"
            session.save(ignore_permissions=True)
            _insert_event_log(
                event_type="enroll",
                device=device_id,
                matched=0,
                payload=payload,
                status="failed",
            )
            return {"ok": False, "status": session.status}

        user = session.requested_for_user
        biometric_id = payload.get("biometric_id") or frappe.generate_hash(length=12)
        employee = _get_employee_for_user(user)

        # deactivate old credentials for this user
        old_docs = frappe.get_all("Biometric Credential", filters={"user": user, "is_active": 1}, pluck="name")
        for old_name in old_docs:
            frappe.db.set_value("Biometric Credential", old_name, "is_active", 0, update_modified=True)

        credential = frappe.get_doc(
            {
                "doctype": "Biometric Credential",
                "user": user,
                "employee": employee,
                "biometric_id": biometric_id,
                "template_data": payload.get("template_data"),
                "template_format": payload.get("template_format") or "base64",
                "quality_score": cint(payload.get("quality_score") or 0),
                "enrolled_on": now_datetime(),
                "is_active": 1,
                "device": device_id,
            }
        )
        credential.insert(ignore_permissions=True)
        _update_user_biometric_fields(user, biometric_id, "Enrolled", device=device_id)

        session.status = "Completed"
        session.result_user = user
        session.result_employee = employee
        session.biometric_id = biometric_id
        session.message = payload.get("message") or "Enrollment completed"
        session.result_confidence = flt(payload.get("confidence") or 0)
        session.save(ignore_permissions=True)

        _insert_event_log(
            event_type="enroll",
            device=device_id,
            user=user,
            employee=employee,
            biometric_id=biometric_id,
            matched=1,
            confidence=flt(payload.get("confidence") or 0),
            payload=payload,
            status="success",
        )
        return {"ok": True, "status": session.status, "user": user}

    # Identify / Test branch
    biometric_id = payload.get("biometric_id")
    user = payload.get("user")
    confidence = flt(payload.get("confidence") or 0)

    if not user and biometric_id:
        user = frappe.db.get_value("Biometric Credential", {"biometric_id": biometric_id, "is_active": 1}, "user")

    employee = _get_employee_for_user(user) if user else None

    if payload.get("success") and user:
        session.status = "Completed"
        session.result_user = user
        session.result_employee = employee
        session.biometric_id = biometric_id
        session.message = payload.get("message") or "Identification successful"
        session.result_confidence = confidence

        checkin_name = None
        settings = _get_settings_doc()
        if cint(settings.auto_create_employee_checkin) and user:
            checkin_name = _create_employee_checkin(user, biometric_id or "", session_name=session.name)
            session.checkin_name = checkin_name

        session.save(ignore_permissions=True)

        _insert_event_log(
            event_type="identify",
            device=device_id,
            user=user,
            employee=employee,
            biometric_id=biometric_id,
            matched=1,
            confidence=confidence,
            payload=payload,
            status="success",
        )
        return {"ok": True, "status": session.status, "user": user, "employee": employee, "checkin_name": checkin_name}

    session.status = "Failed"
    session.message = payload.get("message") or "Unknown fingerprint"
    session.biometric_id = biometric_id
    session.result_confidence = confidence
    session.save(ignore_permissions=True)

    _insert_event_log(
        event_type="identify",
        device=device_id,
        biometric_id=biometric_id,
        matched=0,
        confidence=confidence,
        payload=payload,
        status="failed",
    )
    return {"ok": False, "status": session.status}
