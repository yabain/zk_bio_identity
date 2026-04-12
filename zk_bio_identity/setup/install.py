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

import frappe

def ensure_workspace():
    name = "ZK Bio Identity"

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

    shortcuts = [
        {
            "label": "Connect Device",
            "link_to": "biometric_connect_device",
            "type": "Page",
            "color": "Blue",
            "doc_view": "List",
        },
        {
            "label": "Identify User",
            "link_to": "biometric_identify_user",
            "type": "Page",
            "color": "Blue",
            "doc_view": "List",
        },
        {
            "label": "Add Fingerprint",
            "link_to": "biometric_enroll_user",
            "type": "Page",
            "color": "Blue",
            "doc_view": "List",
        },
        {
            "label": "Attendance Dashboard",
            "link_to": "biometric_attendance_dashboard",
            "type": "Page",
            "color": "Blue",
            "doc_view": "List",
        },
        {
            "label": "Settings",
            "link_to": "ZK Bio Settings",
            "type": "DocType",
            "color": "Blue",
            "doc_view": "Form",
        },
    ]

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

    workspace.set("shortcuts", [])
    for row in shortcuts:
        workspace.append("shortcuts", row)

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
