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

## Installation and Usage Manual

## 1. Prerequisites

### Frappe / ERPNext side
- Frappe or ERPNext site v15+
- HR module enabled if you need `Employee`, `Employee Checkin`, `Attendance`, `Shift Type`, `Auto Attendance`
- administrator access to the site
- ability to install a custom app from GitHub on Frappe Cloud

### Local machine side
- Windows recommended for ZKTeco USB scanner
- Python 3.10+
- outbound internet access to your Frappe Cloud site
- official ZKTeco SDK / driver matching your device model

## 2. Installing the app on Frappe Cloud

1. Push this repository to GitHub.
2. In Frappe Cloud, open the Bench hosting your site.
3. Add the custom app from the GitHub repository.
4. Install the app on the site.
5. Run site migration if required.

Once installed, the app automatically creates:
- roles `Biometric Manager` and `Biometric Operator`
- biometric fields added to `User`
- public Workspace `ZK Bio Identity`
- document `ZK Bio Settings` if it does not exist

## 3. Initial site configuration

### 3.1 Assign roles
Assign at least one of the following roles to operators:
- `Biometric Manager`
- `Biometric Operator`

### 3.2 Open settings
Go to:
- `ZK Bio Identity` → `ZK Bio Settings`

Fill in:
- `default_device`: default device
- `auto_create_employee_checkin`: enable to automatically create checkins after successful identification
- `checkin_mode`: `Alternating`, `Always IN`, or `Always OUT`
- `heartbeat_timeout_seconds`: time after which a device is considered offline

## 4. Creating a dedicated API user for the agent

Create a technical user, for example:
- `biometric.agent@yourdomain.com`

Assign:
- `Biometric Manager`

Generate:
- API Key
- API Secret

These values will be used in `agent_local/config.yaml`.

## 5. Installing the ZKTeco driver / SDK

### 5.1 Windows
1. Download the official ZKFinger SDK for Windows from the ZKTeco download center.
2. Extract the archive.
3. Install the provided driver.
4. Plug in the USB scanner.
5. Verify that Windows detects the device correctly.
6. Locate the main DLL path used by the SDK.

Example path (adjust as needed):
- `C:\ZKTeco\ZKFingerSDK\lib\zkfp.dll`

### 5.2 macOS
Native macOS support is not recommended for this V1.

Recommended approach:
1. create a Linux VM on your Mac
2. pass through the USB scanner to the VM
3. install the ZKTeco Linux SDK inside the VM
4. run the agent inside the VM instead of macOS

## 6. Installing the local agent

### 6.1 Prepare the environment
Inside `agent_local/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Stay in touch

- Author -  [GIC Promote Ltd ](https://gic.cm/) & [Yaba-In](https://yaba-in.com/)
- Website GIC Promote Ltd- [https://gic.cm/](https://gic.cm/)
- Website Yaba-In- [https://yaba-in.com/](https://yaba-in.com/)


**Your software solution compagny.**