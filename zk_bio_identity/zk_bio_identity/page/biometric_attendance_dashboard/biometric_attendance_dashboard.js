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

frappe.pages['biometric_attendance_dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Attendance Dashboard',
        single_column: true
    });

    const body = $(`
        <div>
            <div class="frappe-card" style="padding:16px;margin-bottom:16px;">
                <button class="btn btn-primary" id="refresh-dashboard">Refresh</button>
                <a class="btn btn-default" href="/app/employee-checkin">Employee Checkin</a>
                <a class="btn btn-default" href="/app/attendance">Attendance</a>
                <a class="btn btn-default" href="/app/shift-type">Shift Type</a>
            </div>
            <div id="stats-grid" class="row"></div>
            <div class="frappe-card" style="padding:16px;margin-top:16px;">
                <h4>Recent events</h4>
                <div id="recent-events"></div>
            </div>
        </div>
    `);

    $(wrapper).find('.layout-main-section').html(body);

    function statCard(label, value) {
        return `
            <div class="col-md-3">
                <div class="frappe-card" style="padding:16px;margin-bottom:12px;">
                    <div style="font-size:12px;color:#666;">${label}</div>
                    <div style="font-size:28px;font-weight:700;">${value}</div>
                </div>
            </div>
        `;
    }

    function loadDashboard() {
        frappe.call({
            method: "zk_bio_identity.api.get_dashboard_stats",
            callback: function(r) {
                const d = r.message || {};
                body.find("#stats-grid").html(
                    statCard("Devices", d.devices || 0) +
                    statCard("Active credentials", d.active_credentials || 0) +
                    statCard("Pending sessions", d.pending_sessions || 0) +
                    statCard("Employee checkins today", d.employee_checkins_today || 0) +
                    statCard("Success events", d.success_events || 0)
                );
            }
        });

        frappe.call({
            method: "zk_bio_identity.api.get_recent_event_logs",
            callback: function(r) {
                const rows = r.message || [];
                if (!rows.length) {
                    body.find("#recent-events").html('<div class="text-muted">No event yet.</div>');
                    return;
                }
                const html = `
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Event</th>
                                <th>Device</th>
                                <th>User</th>
                                <th>Employee</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rows.map(row => `
                                <tr>
                                    <td>${row.event_time || ""}</td>
                                    <td>${row.event_type || ""}</td>
                                    <td>${row.device || ""}</td>
                                    <td>${row.user || ""}</td>
                                    <td>${row.employee || ""}</td>
                                    <td>${row.status || ""}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                `;
                body.find("#recent-events").html(html);
            }
        });
    }

    body.on("click", "#refresh-dashboard", loadDashboard);
    loadDashboard();
};
