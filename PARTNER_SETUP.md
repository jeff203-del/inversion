# Partner deployment and SMS setup

## RumptyCloud deployment

The GitHub workflow builds the Next.js static export, packages it with the FastAPI source, and uploads both services to one RumptyCloud VM using the Rumpty CLI. The VM needs Docker Engine and the Docker Compose plugin. The deployment starts the web and API containers on an internal Compose network; the web container proxies `/api/*` requests to FastAPI and serves the app on Rumpty's default public app port, 8080.

1. Create a RumptyCloud Linux VM and install Docker Engine with the Compose plugin.
2. Stop the default `rumpty-welcome.service` so the app container can use port 8080.
3. Add GitHub Actions secrets `RUMPTY_TOKEN` (a full, unmasked Rumpty personal API token) and `VM_SSH_KEY` (the private key whose public half is authorized on the VM). Never commit these values. The workflow currently targets VM `inverse` in workspace `qo-01a1b65d`; update those non-secret values in the workflow if you use another VM/workspace.
4. Run **Actions → Deploy to RumptyCloud → Run workflow**. The workflow builds the frontend, packages the API, uploads a tarball to the VM with the Rumpty CLI, then runs `docker compose up -d --build`.
5. Open the RumptyCloud VM app URL. Check `<your-app-url>/api/health` for the API response and try **Campaigns → Invite candidate**. With the default `SMS_MODE=console`, the API returns a message preview without sending a real SMS.

If the VM image lacks Docker, install it before the first workflow run. The build happens on GitHub Actions; the VM only runs the two containers.

## ThriveVas SMS API

The sender in `api/sms.py` follows the supplied ThriveVas Python example and full API screenshot:

- `POST https://sms.thrivevas.com/v1/message/send`
- `Content-Type: application/json`
- `x-api-key: <API token>`
- JSON fields: `message`, `msisdn`, `sender_id`, optional `callback_url`
- Success response includes `status`, `message` and `transaction_id`; transient errors are retried twice, after 5 and 30 seconds.

The API key previously pasted into chat is not in the source tree. Rotate it before using live sending, then add the replacement only to `/opt/defend-it/.env` on the VM (use `sudoedit`, never a command-line argument). Example configuration with placeholders:

```dotenv
SMS_MODE=console
THRIVEVAS_API_KEY=put-rotated-token-here
THRIVEVAS_SENDER_ID=ThriveVas
THRIVEVAS_API_BASE_URL=https://sms.thrivevas.com/v1
THRIVEVAS_CALLBACK_URL=https://your-real-host/api/webhooks/sms
SMS_ALLOWED_RECIPIENTS=2547xxxxxxxx
ALLOWED_ORIGINS=https://your-real-host
```

Keep `SMS_MODE=console` for the deployment preview. To enable live sends to the test recipient only, set `SMS_MODE=live` after the rotated token and `SMS_ALLOWED_RECIPIENTS` are present, then run `sudo docker compose --project-directory /opt/defend-it -f /opt/defend-it/docker-compose.yml up -d`. Live requests outside the allowlist are rejected. Do not configure a real token in GitHub Actions or the source repository.

The SMS form calls `POST /api/demo/invite`; API credentials stay on the server. Delivery reports can be posted to `/api/webhooks/sms`. The callback log is currently in memory only and is lost when the API restarts. Confirm sender ID registration and your account's SMS credits before testing a real message.

## What is still demo-only

- Dashboard campaigns and candidate records are sample data; there is no account system or database persistence yet.
- The candidate round UI sends its four round scores to `/api/score`, but round timing, answers and grading still run in the browser. Do not present this as tamper-proof production assessment.
- Delivery report records are process-local and the callback has no signature verification yet. Do not rely on it as a production audit trail.
- The validation workspace starts empty. Add only real, consented owner/stranger sessions.
- State these limits in the hackathon pitch. Do not present the seeded dashboard figures as experiment results.
