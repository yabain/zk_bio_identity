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

frappe.pages['biometric_enroll_user'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Add Fingerprint',
        single_column: true
    });

    const body = $(`
        <div>
            <div class="frappe-card" style="padding:16px;margin-bottom:16px;">
                <div class="form-group">
                    <label>User</label>
                    <input type="text" id="user-search" class="form-control" placeholder="Type a name and click Search">
                </div>
                <button class="btn btn-default" id="search-users">Search</button>
                <div id="users-results" style="margin-top:12px;"></div>
                <hr>
                <div class="form-group">
                    <label>Device</label>
                    <select id="device-select" class="form-control"></select>
                </div>
                <button class="btn btn-primary" id="start-enroll" disabled>Start Enrollment</button>
                <div id="enroll-status" style="margin-top:12px;"></div>
            </div>
            <div id="profile-result"></div>
        </div>
    `);

    let selectedUser = null;
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

    body.on("click", "#search-users", function() {
        const txt = body.find("#user-search").val();
        frappe.call({
            method: "zk_bio_identity.api.search_users",
            args: { txt },
            callback: function(r) {
                const rows = r.message || [];
                if (!rows.length) {
                    body.find("#users-results").html('<div class="alert alert-warning">No user found.</div>');
                    return;
                }
                const html = rows.map(row => `
                    <label style="display:block;padding:8px;border:1px solid #ddd;margin-bottom:8px;border-radius:6px;">
                        <input type="radio" name="selected_user" value="${row.name}">
                        <strong>${row.full_name || row.name}</strong> — ${row.name} — biometric: ${row.custom_biometric_status || "Not Enrolled"}
                    </label>
                `).join("");
                body.find("#users-results").html(html);
            }
        });
    });

    body.on("change", "input[name='selected_user']", function() {
        selectedUser = $(this).val();
        body.find("#start-enroll").prop("disabled", !selectedUser);
        frappe.call({
            method: "zk_bio_identity.api.get_user_profile",
            args: { user: selectedUser },
            callback: function(r) {
                zkbiRenderProfile(body.find("#profile-result"), r.message);
            }
        });
    });

    body.on("click", "#start-enroll", function() {
        if (!selectedUser) {
            frappe.msgprint("Select a user first.");
            return;
        }
        const device = body.find("#device-select").val() || null;
        body.find("#enroll-status").html('<div class="alert alert-info">Waiting for fingerprint enrollment...</div>');

        frappe.call({
            method: "zk_bio_identity.api.create_enroll_session",
            args: { user: selectedUser, device },
            callback: function(r) {
                const sessionName = r.message.session;
                zkbiPollSession(page, sessionName, function(data) {
                    if (data.status === "Completed") {
                        body.find("#enroll-status").html(`<div class="alert alert-success">${data.message || "Enrollment completed"}</div>`);
                        zkbiRenderProfile(body.find("#profile-result"), data.profile);
                    } else {
                        body.find("#enroll-status").html(`<div class="alert alert-warning">${data.message || "Enrollment failed"}</div>`);
                    }
                });
            }
        });
    });

    loadDevices();
};
