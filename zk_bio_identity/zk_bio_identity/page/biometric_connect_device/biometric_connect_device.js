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

frappe.pages['biometric_connect_device'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Connect Device',
        single_column: true
    });

    const body = $(`
        <div>
            <div class="frappe-card" style="padding:16px;margin-bottom:16px;">
                <p>This page shows the devices known by the local agents and whether the scanner is detected.</p>
                <button class="btn btn-primary" id="refresh-devices">Refresh</button>
            </div>
            <div id="devices-list"></div>
        </div>
    `);

    $(wrapper).find('.layout-main-section').html(body);

    function loadDevices() {
        frappe.call({
            method: "zk_bio_identity.api.list_devices",
            callback: function(r) {
                const rows = r.message || [];
                if (!rows.length) {
                    body.find("#devices-list").html('<div class="alert alert-warning">No device registered yet.</div>');
                    return;
                }
                const html = rows.map(d => `
                    <div class="frappe-card" style="padding:16px;margin-bottom:12px;">
                        <h4 style="margin-top:0;">${d.device_name || d.device_id}</h4>
                        <div><strong>Device ID:</strong> ${d.device_id}</div>
                        <div><strong>Provider:</strong> ${d.provider || '-'}</div>
                        <div><strong>Status:</strong> ${d.last_status || '-'}</div>
                        <div><strong>Scanner connected:</strong> ${d.scanner_connected ? 'Yes' : 'No'}</div>
                        <div><strong>Detected scanner:</strong> ${d.scanner_detected_name || '-'}</div>
                        <div><strong>Model:</strong> ${d.scanner_model || '-'}</div>
                        <div><strong>OS:</strong> ${d.os_type || '-'}</div>
                        <div><strong>Agent version:</strong> ${d.agent_version || '-'}</div>
                        <div><strong>Last seen:</strong> ${d.last_seen_at || '-'}</div>
                    </div>
                `).join("");
                body.find("#devices-list").html(html);
            }
        });
    }

    body.on("click", "#refresh-devices", loadDevices);
    loadDevices();
};
