# Partner deployment and SMS setup

## RumptyCloud deployment

The GitHub workflow builds the Next.js static export, packages it with the FastAPI source, and uploads both services to one RumptyCloud VM. The VM needs Docker Engine and the Docker Compose plugin. The deployment starts the web and API containers on an internal Compose network; the web container proxies `/api/*` requests to FastAPI.

1. Create a RumptyCloud Linux VM. Install Docker Engine and the Compose plugin if they are not part of its image.
2. Configure the RumptyCloud nginx HTTPS site to proxy to `http://127.0.0.1:8080`. The location block is in `deploy/rumpty-nginx-location.conf`; merge it into the HTTPS server block generated for your real hostname.
3. In the VM deployment's **Deploy** tab, get `RUMPTY_TOKEN` and `RUMPTY_VM_ID`.
4. Push the project to a GitHub repository's `main` branch. Add those two values under **Settings → Secrets and variables → Actions**. Do not put them in the repo or chat.
5. Run **Actions → Deploy to RumptyCloud → Deploy to RumptyCloud → Run workflow**. The workflow uploads the web and API bundle to `/opt/defend-it`, runs `docker compose up -d --build`, and reloads nginx.
6. Open the RumptyCloud app URL. Check `<your-app-url>/api/health` for the API response and try **Campaigns → Invite candidate**. With the default `SMS_MODE=console`, the API returns a message preview without sending a real SMS.

The provider's Deploy tab must use a VM that supports Docker. The action copies build artifacts; this workflow uses its `after-deploy` command to start the two containers. If the VM image lacks Docker, install it before the first workflow run.

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
