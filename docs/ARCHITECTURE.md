# Architecture

## Components

### 1. Frappe app
Responsible for:
- user-facing pages
- enrollment requests
- identification requests
- biometric metadata
- audit trail
- attendance event creation

### 2. Local agent
Responsible for:
- reading the scanner SDK locally
- polling Frappe for pending sessions
- performing enroll / identify operations
- keeping a local cache of active templates
- posting results back to Frappe

## Install hook responsibilities

The app install hook:
- creates the custom fields on `User`
- creates roles
- creates the public workspace
- ensures `ZK Bio Settings` exists

## Why templates are stored server-side

The server keeps biometric templates so that:
- enrollment done on one station can be used on another station
- the agent can refresh local cache on startup
- operators keep a history and audit trail

## Attendance flow

1. Fingerprint identify
2. matched `biometric_id`
3. matched `User`
4. linked `Employee`
5. create `Employee Checkin`
6. let Auto Attendance create the final attendance record
