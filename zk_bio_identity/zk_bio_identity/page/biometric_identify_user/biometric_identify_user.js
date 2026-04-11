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

frappe.pages['biometric_identify_user'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Identify User',
        single_column: true
    });

    const body = $(`
        <div>
            <div class="frappe-card" style="padding:16px;margin-bottom:16px;">
                <div class="form-group">
                    <label>Device</label>
                    <select id="device-select" class="form-control"></select>
                </div>
                <button class="btn btn-primary" id="start-identify">Start Identification</button>
                <div id="session-status" style="margin-top:12px;"></div>
            </div>
            <div id="profile-result"></div>
        </div>
    `);

    $(wrapper).find('.layout-main-section').html(body);

    function loadDevices() {
        frappe.call({
            method: "zk_bio_identity.api.list_devices",
            callback: function(r) {
                const rows = r.message || [];
                const select = body.find("#device-select");
                select.empty();
                rows.forEach(row => select.append(`<option value="${row.name}">${row.device_name || row.device_id}</option>`));
            }
        });
    }

    body.on("click", "#start-identify", function() {
        const device = body.find("#device-select").val() || null;
        body.find("#session-status").html('<div class="alert alert-info">Waiting for fingerprint...</div>');
        body.find("#profile-result").empty();

        frappe.call({
            method: "zk_bio_identity.api.create_identify_session",
            args: { device },
            callback: function(r) {
                const sessionName = r.message.session;
                zkbiPollSession(page, sessionName, function(data) {
                    if (data.status === "Completed") {
                        body.find("#session-status").html(`<div class="alert alert-success">${data.message || "Identification successful"}</div>`);
                        zkbiRenderProfile(body.find("#profile-result"), data.profile);
                    } else {
                        body.find("#session-status").html(`<div class="alert alert-warning">${data.message || "Utilisateur inexistant"}</div>`);
                        zkbiRenderProfile(body.find("#profile-result"), null, data.message || "Utilisateur inexistant");
                    }
                });
            }
        });
    });

    loadDevices();
};
