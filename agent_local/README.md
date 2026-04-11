# Local agent

This service polls your Frappe site for pending biometric sessions.

## Run

```bash
python main.py --config config.yaml
```

## Providers

- `mock`: simulation mode for end-to-end testing
- `zkteco_sdk`: scaffold for real ZKTeco SDK integration

## Notes

The service is intentionally simple:
- register/update device on startup
- send heartbeat periodically
- refresh active templates periodically
- execute identify/enroll sessions
- post results back to Frappe
