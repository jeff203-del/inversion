# Defend It

**Anyone can generate a repo. Defend It shows who can defend one.**

Defend It is a candidate ownership assessment for Kenyan recruiters, bootcamps and lecturers. It asks candidates to recognise code patterns, explain a decision, locate a bug and make a small change. The score is decision support; it never calls someone a cheater or makes a hiring decision.

## Demo

Open `index.html` for the zero-install browser demo, or run the Next.js app as described below. Choose **Try candidate demo**. The recruiter overview, campaign list, leaderboard, evidence board, four rounds, timer, paste-block notice, scoring, validation workspace and finish screen work without an account. Dashboard records are clearly marked sample data. Candidate round questions and code are illustrative fixtures, not generated from a candidate repository.

## What is implemented

- Four-round browser demonstration: Spot the Impostor, Explain It, Bug Hunt and Extend It.
- Ownership score weighted 15%, 35%, 30% and 20%, with deterministic checks for recognition, bug location and the sample extension.
- Recruiter campaign overview, leaderboard filters, evidence board, score breakdown, confidence display, Build Story context and integrity events.
- Fairness language: English fluency is not graded, integrity events are shown without score deductions, and a person reviews the evidence.
- FastAPI service for browser-driven invite previews, server-side score calculation, delivery reports and console or ThriveVas live SMS modes.
- Next.js, TypeScript and Tailwind web scaffold with a static export for hosting.
- Docker Compose for the static site and API.
- RumptyCloud GitHub Actions deployment workflow for a combined web and API bundle.

## Run locally

### Browser demo

Open `index.html`. No build step is required.

### Next.js web app

Install Node.js 22 or later, then run:

```sh
cd web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). `npm run build` creates the static site in `web/out` for RumptyCloud.

### API and containers

Install Docker Desktop, then run:

```sh
docker compose up --build
```

Open [http://localhost:8080](http://localhost:8080) for the demo and [http://localhost:8000/health](http://localhost:8000/health) for the API health response. **Campaigns → Invite candidate** calls FastAPI; the finish screen posts round scores to `/api/score`. `SMS_MODE=console` is the default and records outbound message previews without sending a real text.

## Partner services

### RumptyCloud

The repository includes `.github/workflows/rumpty-deploy.yml`. Create a RumptyCloud VM with Docker/Compose and nginx HTTPS configured to proxy to port 8080. Add `RUMPTY_TOKEN` and `RUMPTY_VM_ID` as GitHub Actions secrets, then run **Actions → Deploy to RumptyCloud → Run workflow**. It packages the static export and API together. See [PARTNER_SETUP.md](PARTNER_SETUP.md) for the exact steps.

### ThriveVas SMS

The API uses `POST https://sms.thrivevas.com/v1/message/send` with the `x-api-key` header and documented JSON body. It defaults to console mode. Live mode requires a server-side token and an allowlisted test number; see [PARTNER_SETUP.md](PARTNER_SETUP.md). Do not commit credentials.

## Environment configuration

Copy `.env.example` to `.env` for local container configuration. Never put real keys in Git. The API is connected for invitation previews and scoring, but candidate timing, answers and round grading remain browser-side; dashboard campaigns and records remain sample data.

## Limitations to state during the pitch

- This submission is a working product demonstration, not the complete multi-tenant platform in the build plan.
- Demo repositories, scores and recruiter events are sample data. Real candidate defences must use validated questions grounded in a candidate's public repository.
- The current browser sample simulates its timers and round grading. Production timing, answer keys and scoring must be enforced by the API.
- Live ThriveVas SMS and RumptyCloud deployment require the team's private credentials and VM setup.
- A score can be wrong. Recruiters should inspect the evidence and talk with candidates, especially when team ownership or commit history is ambiguous.
- Any real deployment needs explicit consent, a retention policy and a review against Kenya's Data Protection Act, 2019.

## Rubric evidence

The demo addresses a concrete hiring and coursework verification problem. It shows a complete candidate flow and recruiter review surface, explains the scoring and fairness rules, includes a health endpoint and container setup, and states the current evidence and limits openly. The validation page and real owner-versus-stranger study remain follow-up work; sample dashboard values are not experimental results.
