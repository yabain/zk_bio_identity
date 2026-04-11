function zkbiRenderProfile(target, profile, message) {
    if (!profile) {
        target.html(`<div class="alert alert-warning">${message || "Utilisateur inexistant"}</div>`);
        return;
    }

    const img = profile.user_image ? `<img src="${profile.user_image}" style="width:72px;height:72px;border-radius:50%;object-fit:cover;margin-right:16px;">` : "";
    target.html(`
        <div class="frappe-card" style="padding:16px;">
            <div style="display:flex;align-items:center;">
                ${img}
                <div>
                    <h4 style="margin:0 0 6px 0;">${profile.full_name || profile.user}</h4>
                    <div><strong>User:</strong> ${profile.user}</div>
                    <div><strong>Email:</strong> ${profile.email || ""}</div>
                    <div><strong>Biometric ID:</strong> ${profile.biometric_id || "-"}</div>
                    <div><strong>Employee:</strong> ${profile.employee || "-"}</div>
                    <div><strong>Designation:</strong> ${profile.designation || "-"}</div>
                    <div><strong>Department:</strong> ${profile.department || "-"}</div>
                    <div><strong>Company:</strong> ${profile.company || "-"}</div>
                </div>
            </div>
        </div>
    `);
}

function zkbiPollSession(page, sessionName, callback) {
    frappe.call({
        method: "zk_bio_identity.api.get_session",
        args: { session: sessionName },
        freeze: false,
        callback: function(r) {
            const data = r.message;
            if (!data) {
                callback({ status: "Failed", message: "Session not found" });
                return;
            }

            if (["Completed", "Failed", "Cancelled"].includes(data.status)) {
                callback(data);
                return;
            }

            setTimeout(() => zkbiPollSession(page, sessionName, callback), 2000);
        }
    });
}

frappe.pages['zk_bio_identity'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'ZK Bio Identity',
        single_column: true
    });

    $(wrapper).find('.layout-main-section').html(`
        <div class="row">
            <div class="col-md-12">
                <div class="frappe-card" style="padding:24px;">
                    <h3>ZK Bio Identity</h3>
                    <p>Use the shortcuts below to manage device connectivity, biometric enrollment, identification, and attendance analytics.</p>
                    <div style="display:flex;gap:12px;flex-wrap:wrap;">
                        <a class="btn btn-primary" href="/app/biometric_connect_device">Connect Device</a>
                        <a class="btn btn-primary" href="/app/biometric_identify_user">Identify User</a>
                        <a class="btn btn-primary" href="/app/biometric_enroll_user">Add Fingerprint</a>
                        <a class="btn btn-primary" href="/app/biometric_attendance_dashboard">Attendance Dashboard</a>
                        <a class="btn btn-default" href="/app/zk-bio-settings/ZK%20Bio%20Settings">Settings</a>
                    </div>
                </div>
            </div>
        </div>
    `);
};
