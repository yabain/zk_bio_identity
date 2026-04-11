app_name = "zk_bio_identity"
app_title = "ZK Bio Identity"
app_publisher = "OpenAI"
app_description = "Biometric identification, enrollment, and attendance bridge for Frappe/ERPNext."
app_email = "support@example.com"
app_license = "MIT"
app_color = "blue"
app_icon = "fingerprint"

after_install = "zk_bio_identity.setup.install.after_install"
after_migrate = "zk_bio_identity.setup.install.after_migrate"

add_to_apps_screen = [
    {
        "name": "zk_bio_identity",
        "logo": "/assets/zk_bio_identity/logo.svg",
        "title": "ZK Bio Identity",
        "route": "/app/zk_bio_identity",
        "has_permission": "zk_bio_identity.api.check_app_permission",
    }
]
