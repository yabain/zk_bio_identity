import json

import frappe
from frappe import _


ROLE_NAMES = ["Biometric Manager", "Biometric Operator"]


USER_CUSTOM_FIELDS = [
    {
        "fieldname": "custom_biometric_id",
        "label": "Biometric ID",
        "fieldtype": "Data",
        "insert_after": "user_image",
        "read_only": 1,
        "unique": 1,
    },
    {
        "fieldname": "custom_biometric_status",
        "label": "Biometric Status",
        "fieldtype": "Select",
        "options": "\nNot Enrolled\nEnrolled\nDisabled",
        "insert_after": "custom_biometric_id",
        "default": "Not Enrolled",
        "read_only": 1,
    },
    {
        "fieldname": "custom_last_biometric_enrollment_on",
        "label": "Last Biometric Enrollment On",
        "fieldtype": "Datetime",
        "insert_after": "custom_biometric_status",
        "read_only": 1,
    },
    {
        "fieldname": "custom_default_biometric_device",
        "label": "Default Biometric Device",
        "fieldtype": "Link",
        "options": "Biometric Device",
        "insert_after": "custom_last_biometric_enrollment_on",
    },
]


def after_install():
    ensure_roles()
    ensure_user_custom_fields()
    ensure_workspace()
    ensure_settings()


def after_migrate():
    ensure_roles()
    ensure_user_custom_fields()
    ensure_workspace()
    ensure_settings()


def ensure_roles():
    for role_name in ROLE_NAMES:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({"doctype": "Role", "role_name": role_name})
            role.flags.ignore_permissions = True
            role.insert(ignore_permissions=True)


def ensure_user_custom_fields():
    for field in USER_CUSTOM_FIELDS:
        field_name = field["fieldname"]
        if frappe.db.exists("Custom Field", {"dt": "User", "fieldname": field_name}):
            continue

        doc = frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "User",
                "module": "ZK Bio Identity",
                **field,
            }
        )
        doc.flags.ignore_permissions = True
        doc.insert(ignore_permissions=True)


def _ensure_workspace_shortcut(label, link_to, type_, color="Blue", doc_view="List"):
    shortcut_name = label
    if frappe.db.exists("Workspace Shortcut", shortcut_name):
        shortcut = frappe.get_doc("Workspace Shortcut", shortcut_name)
    else:
        shortcut = frappe.new_doc("Workspace Shortcut")
        shortcut.name = shortcut_name
        shortcut.label = label

    shortcut.type = type_
    shortcut.link_to = link_to
    shortcut.color = color
    shortcut.doc_view = doc_view
    shortcut.flags.ignore_permissions = True
    if shortcut.is_new():
        shortcut.insert(ignore_permissions=True)
    else:
        shortcut.save(ignore_permissions=True)
    return shortcut_name


def ensure_workspace():
    # Shortcuts used in workspace content
    _ensure_workspace_shortcut("Connect Device", "biometric_connect_device", "Page")
    _ensure_workspace_shortcut("Identify User", "biometric_identify_user", "Page")
    _ensure_workspace_shortcut("Add Fingerprint", "biometric_enroll_user", "Page")
    _ensure_workspace_shortcut("Attendance Dashboard", "biometric_attendance_dashboard", "Page")
    _ensure_workspace_shortcut("Settings", "ZK Bio Settings", "DocType", doc_view="Form")

    content = [
        {"type": "header", "data": {"text": "Biometric Operations", "level": 4, "col": 12}},
        {"type": "shortcut", "data": {"shortcut_name": "Connect Device", "col": 3}},
        {"type": "shortcut", "data": {"shortcut_name": "Identify User", "col": 3}},
        {"type": "shortcut", "data": {"shortcut_name": "Add Fingerprint", "col": 3}},
        {"type": "shortcut", "data": {"shortcut_name": "Attendance Dashboard", "col": 3}},
        {"type": "spacer", "data": {"col": 12}},
        {"type": "header", "data": {"text": "Configuration", "level": 4, "col": 12}},
        {"type": "shortcut", "data": {"shortcut_name": "Settings", "col": 3}},
    ]

    name = "ZK Bio Identity"
    if frappe.db.exists("Workspace", name):
        workspace = frappe.get_doc("Workspace", name)
    else:
        workspace = frappe.new_doc("Workspace")
        workspace.name = name
        workspace.title = name
        workspace.label = name
        workspace.module = "ZK Bio Identity"
        workspace.public = 1

    workspace.icon = "fingerprint"
    workspace.sequence_id = 90
    workspace.content = frappe.as_json(content)
    workspace.is_hidden = 0
    workspace.for_user = ""
    workspace.parent_page = ""
    workspace.restrict_to_domain = ""
    workspace.flags.ignore_permissions = True
    if workspace.is_new():
        workspace.insert(ignore_permissions=True)
    else:
        workspace.save(ignore_permissions=True)


def ensure_settings():
    if not frappe.db.exists("ZK Bio Settings", "ZK Bio Settings"):
        settings = frappe.get_doc({"doctype": "ZK Bio Settings"})
        settings.flags.ignore_permissions = True
        settings.insert(ignore_permissions=True)
