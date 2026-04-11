<h1 align="center">ZK Bio Identity</h1>

<p align="center">
  <br>
  <img src="https://png.pngtree.com/png-clipart/20250416/original/pngtree-modern-blue-biometric-fingerprint-scanner-icon-with-digital-circuit-png-image_20693221.png" alt="logo" width="30%" />
  <br><br>
  <i>A Frappe app plus a local agent
    <br>...</i>

  <br>
</p>

<p align="center">
  <img src="https://payments.digikuntz.com/assets/img/resources/logo_gic_0.png" alt="logo Yaba-In" width="10%" />
  <img src="https://payments.digikuntz.com/assets/img/resources/logo_yaba-in.png" alt="logo Yaba-In" width="20%" />
</p>
<p align="center">By:
  <a href="https://gic.cm"><strong>GIC Promote Ltd</strong></a> & <a href="https://yaba-in.com"><strong>Yaba-In</strong></a>
  <br>
</p>


<hr>

## Documentation

Get started with ERPNext, learn the fundamentals and explore advanced topics on documentation website.

- [Getting started](https://school.frappe.io/lms/courses/introduction-to-erpnext/learn/1-1)
- [ERPNext Essentials: A Complete Training Program](https://school.frappe.io/lms/courses/erpnext-training)




# ZK Bio Identity

A Frappe app plus a local agent for:

- USB fingerprint scanner status tracking
- fingerprint enrollment against `User`
- fingerprint identification with profile display
- automatic creation of `Employee Checkin`
- attendance-oriented dashboards on top of Frappe HR / ERPNext

## What is in this repository

- `zk_bio_identity/` → installable Frappe app
- `agent_local/` → local polling agent that sits between the USB fingerprint kit and your Frappe Cloud site
- `docs/` → architecture and API notes
- `MANUAL_INSTALLATION.md` → installation and usage guide

## Recommended production topology

- Frappe Cloud hosts the Frappe app.
- A local Windows PC hosts the USB ZKTeco scanner and the agent.
- The agent authenticates to your Frappe site using API key / secret.
- The agent reads scanner status, enrollment, and identify requests from Frappe.
- Frappe stores biometric metadata and attendance events.
- Frappe HR / ERPNext handles `Employee Checkin`, `Attendance`, `Shift Type`, and `Auto Attendance`.

## Important constraint

The Frappe app is complete and installable as delivered.

The local agent is complete for:
- end-to-end simulation mode
- the REST bridge with Frappe
- template cache management
- enroll / identify session orchestration

The only hardware-specific file you may still need to adapt to your exact scanner SDK package is:

- `agent_local/providers/zkteco_sdk_provider.py`

That is because the exact exported DLL / SO symbols can vary by SDK build and scanner family.

## Frappe Cloud installation

See `MANUAL_INSTALLATION.md`.

## Local development

```bash
bench get-app https://github.com/YOUR_ORG/zk-bio-identity.git
bench --site yoursite.local install-app zk_bio_identity
bench --site yoursite.local migrate
```

## Default Desk routes

After installation, the app exposes:

- `/app/zk_bio_identity`
- `/app/biometric_connect_device`
- `/app/biometric_identify_user`
- `/app/biometric_enroll_user`
- `/app/biometric_attendance_dashboard`

## Roles created by the app

- `Biometric Manager`
- `Biometric Operator`

## Core server-side DocTypes

- `ZK Bio Settings` (Single)
- `Biometric Device`
- `Biometric Credential`
- `Biometric Scan Session`
- `Biometric Event Log`

## License note
This project is delivered as an original app inspired by the public structure and feature ideas of the referenced M-Pesa app.
You should still perform your own legal review before distributing commercially.


## Stay in touch

- Author -  [GIC Promote Ltd ](https://gic.cm/) & [Yaba-In](https://yaba-in.com/)
- Website GIC Promote Ltd- [https://gic.cm/](https://gic.cm/)
- Website Yaba-In- [https://yaba-in.com/](https://yaba-in.com/)


**Your software solution compagny.**