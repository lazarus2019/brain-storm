# Stage 1 – Lesson 4: GitLab for DevOps (Build, Secure, Deploy, Operate, Monitor, Settings)

⏱️ Time: ~45–60 minutes
💰 Cost: $0 (no AWS in this lesson; uses GitLab.com free compute minutes)
🎯 Goal: Know which parts of GitLab's DevOps tabs actually matter, what they do, and run your first real pipeline.

> You already know Code, Merge Requests, Issues, etc. This lesson **only** covers the tabs you haven't used, and **skips** anything a DevOps-aware developer rarely touches.
>
> ⚠️ GitLab moves menu items around between versions, and many features depend on your plan (Free / Premium / Ultimate). I label features as **(Free)** or **(Paid)** where it matters, but verify on [docs.gitlab.com](https://docs.gitlab.com) if something is missing in your UI.

---

## 1. What problem do these tabs solve?

Code and Merge Requests answer **"what changed?"**. The DevOps tabs answer:

| Tab | Question it answers |
|-----|---------------------|
| **Build** | Did my code build and pass tests automatically? |
| **Secure** | Did I leak a secret or add a vulnerable library? |
| **Deploy** | Where are my built packages / Docker images / releases stored? |
| **Operate** | What version is running in staging and production right now? |
| **Monitor** | Is something broken in production? (lightly used — see below) |
| **Settings** | Where do secrets, runners, and branch protection rules live? |

### 🏭 Analogy: a factory

- **Code** = the blueprint room
- **Build** = the assembly line (pipelines) and the workers (runners)
- **Secure** = the quality/safety inspector
- **Deploy** = the warehouse where finished products are stored
- **Operate** = the delivery map: which shop (environment) has which product version
- **Settings** = the security office holding the keys (secrets) and the rules about who can enter

### 🗺️ Where it fits in a web architecture

```mermaid
flowchart LR
    Dev[You: git push] --> GL[GitLab repo]
    GL --> P[Build: Pipeline]
    P --> R[Runner executes jobs]
    R --> SEC[Secure: scans]
    R --> ART[Artifacts: dist/ folder]
    R --> REG[Deploy: Container Registry]
    ART --> ENV[Operate: Environments<br/>staging / production]
    REG --> ENV
    ENV -.later stages.-> AWS[(AWS: S3, EC2, EKS)]
    S[Settings: CI/CD variables, runners, protected branches] -.feeds.-> P
```

---

## 2. Priority map — what to learn vs. skip

| Tab | ⭐ Must know | 👀 Know it exists | ⏭️ Skip for now |
|-----|------------|------------------|-----------------|
| Build | Pipelines, Jobs, Pipeline editor, Artifacts | Pipeline schedules | — |
| Secure | Secret Detection, SAST, Dependency Scanning (as CI jobs) | Vulnerability report, Security dashboard (Paid) | Compliance center, Audit events |
| Deploy | Container Registry | Releases, Feature flags, Package Registry | Model registry, Pages |
| Operate | Environments | Kubernetes clusters (Stage 16), Terraform states (later) | Google Cloud integration |
| Monitor | — | Alerts, Incidents | Error tracking, Service Desk |
| Settings → CI/CD | **Variables**, **Runners** | Token access, General pipelines | — |
| Settings → Repository | **Protected branches/tags** | Deploy tokens, Deploy keys | Mirroring |
| Settings (other) | Merge request rules, Usage quotas | Webhooks, Integrations (Slack), Access tokens | — |

---

## 3. Core terms (defined once)

- **CI (Continuous Integration)**: automatically building and testing every change.
- **CD (Continuous Delivery/Deployment)**: automatically preparing (Delivery) or pushing (Deployment) every passing change to an environment.
- **`.gitlab-ci.yml`**: a YAML file at the repo root that defines your pipeline. No file = no pipeline.
- **Pipeline**: one full run of all jobs, triggered by a push, MR, schedule, or button.
- **Stage**: a group of jobs that run in order (`test` → `build` → `deploy`). Jobs in the **same** stage run **in parallel**.
- **Job**: one task (e.g., "run unit tests"). Each job runs in a **fresh, clean environment**.
- **Runner**: the machine/agent that actually executes jobs. GitLab.com gives you shared ("instance") runners.
- **Executor**: how a runner runs a job — `docker` (inside a container, most common), `shell` (directly on the machine), `kubernetes` (as a pod).
- **Artifact**: files a job produces and **passes to later jobs** or lets you download (e.g., `dist/`).
- **Cache**: files reused **between pipelines** to go faster (e.g., npm cache). Not guaranteed to exist.
- **Environment**: a named deployment target (`staging`, `production`) that GitLab tracks.
- **Compute minutes**: the quota of shared-runner time you get per month on GitLab.com.

🇻🇳 Giải thích: **Artifact** là "sản phẩm" của một job (ví dụ thư mục `dist/` sau khi build) — được chuyển sang các job sau và có thể tải về. **Cache** chỉ là "đồ dùng lại" để chạy nhanh hơn (ví dụ thư mục npm cache) — có thể bị mất bất cứ lúc nào, nên đừng dựa vào cache để truyền kết quả giữa các job.

---

## 4. ⭐ Build tab

### 4.1 Pipelines
List of every pipeline run with status: ✅ passed, ❌ failed, ⏸️ manual/blocked, 🔄 running, ⏳ pending.
Click a pipeline → you see stages as columns and jobs as boxes.

### 4.2 Jobs
Every job's **log** (terminal output). This is where 90% of CI debugging happens. Useful buttons: **Retry**, **Cancel**, **Download artifacts**, **Debug** (on some runners).

### 4.3 Pipeline editor
Edit `.gitlab-ci.yml` in the browser with:
- **Validate** tab → syntax check (a "lint")
- **Visualize** tab → diagram of stages/jobs
- **Full configuration** → shows the final YAML after `include:` templates are merged

👉 Always validate here before pushing a big CI change.

### 4.4 Pipeline schedules
Cron-like triggers (e.g., "run nightly security scan at 02:00"). Know it exists.

### 4.5 Artifacts
Lists all stored artifacts and their size. Artifacts consume **storage quota** — use `expire_in`.

### 4.6 Your first real pipeline (NestJS example)

Put this in `.gitlab-ci.yml` at the root of a NestJS project (created with `npx @nestjs/cli new notes-api`, which already has `lint`, `test`, `build` scripts):

```yaml
stages:            # 1
  - test
  - build
  - deploy

default:           # 2
  image: node:22-alpine
  cache:           # 3
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
  before_script:   # 4
    - npm ci --cache .npm --prefer-offline

lint:              # 5
  stage: test
  script:
    - npm run lint

unit-test:         # 6
  stage: test
  script:
    - npm test

build:             # 7
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

fake-deploy:       # 8
  stage: deploy
  before_script: []
  script:
    - echo "Deploying commit $CI_COMMIT_SHORT_SHA to staging"
    - ls -la dist/
  environment:
    name: staging
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

Line by line:

1. **`stages`** – the order. All `test` jobs must pass before `build` starts.
2. **`default`** – settings every job inherits. `image` = the Docker image the job runs in (Node 22 on Alpine Linux, small and fast).
3. **`cache`** – keep the npm download cache between pipelines. `key.files: package-lock.json` means "make a new cache only when dependencies change".
4. **`before_script`** – runs before each job's `script`. `npm ci` = clean, exact install from `package-lock.json` (preferred over `npm install` in CI).
5. **`lint`** – job in stage `test`, runs ESLint.
6. **`unit-test`** – also stage `test`, so it runs **in parallel** with `lint`.
7. **`build`** – compiles TypeScript to `dist/` and saves it as an **artifact** for 1 week.
8. **`fake-deploy`** – pretends to deploy.
   - `before_script: []` overrides the default (no need to install packages).
   - It receives `dist/` automatically because artifacts from earlier stages are downloaded by later jobs.
   - `environment: staging` makes GitLab record this deployment in **Operate → Environments**.
   - `rules` → only run on the default branch (`main`), not on feature branches.

`$CI_COMMIT_SHORT_SHA` and `$CI_DEFAULT_BRANCH` are **predefined variables** GitLab injects into every job. Others you'll use a lot: `$CI_COMMIT_BRANCH`, `$CI_PIPELINE_ID`, `$CI_REGISTRY_IMAGE`, `$CI_JOB_TOKEN`.

> **React (Vite) version:** identical, just replace `lint`/`unit-test` with your scripts. Vite outputs to `dist/`; Create React App outputs to `build/` — change the artifact path accordingly. We'll deploy this to S3 for real in Stages 3 and 7.

---

## 5. ⭐ Secure tab

### What DevOps must know
Security scanning in GitLab is mostly **CI jobs you add with templates**. The concept teams call **"shift left"** = find security problems early (in the MR), not in production.

| Scanner | What it finds | Tier |
|---------|--------------|------|
| **Secret Detection** | API keys, passwords, AWS keys committed to Git | Scanner: Free |
| **SAST** (Static Application Security Testing) | Dangerous code patterns (e.g., SQL injection) | Scanner: Free |
| **Dependency Scanning** | npm packages with known CVEs | Paid |
| **Container Scanning** | Vulnerabilities inside your Docker image | Scanner: Free |
| **DAST** (Dynamic) | Attacks a running app from outside | Paid |

- **CVE** (Common Vulnerabilities and Exposures): a public ID for a known security bug, e.g., `CVE-2024-12345`.

On the **Free** tier, scanners run and produce a JSON **report artifact** you can download from the job. The nice UI (**Vulnerability report**, **Security dashboard**, MR security widget) is mostly **Ultimate**. Many companies pay for it — or use alternatives like Snyk, Trivy, SonarQube, GitHub-independent tools, or `npm audit`.

Add scanners to your pipeline:

```yaml
include:
  - template: Jobs/Secret-Detection.gitlab-ci.yml
  - template: Jobs/SAST.gitlab-ci.yml
```

These jobs run in the `test` stage (which you already have). Free alternative for dependencies:

```yaml
npm-audit:
  stage: test
  script:
    - npm audit --audit-level=high
  allow_failure: true   # report only, don't block the pipeline (yet)
```

🇻🇳 Giải thích: **Secret Detection** quét code để tìm mật khẩu hoặc access key bị commit nhầm. Lưu ý: nếu bạn đã lỡ push một secret lên GitLab, **xoá commit là chưa đủ** — phải **thu hồi (revoke) và tạo key mới** ngay, vì lịch sử Git và các bản fork/clone vẫn còn giữ nó.

---

## 6. ⭐ Deploy tab

### 6.1 Container Registry ⭐
A private Docker image storage **built into every project**. Image names look like:

```
registry.gitlab.com/<your-namespace>/<project>:<tag>
```

In CI this is available as `$CI_REGISTRY_IMAGE`, and you log in with the auto-provided `$CI_REGISTRY_USER` / `$CI_REGISTRY_PASSWORD` — **no personal password needed**. You'll use this in Lesson 5 (Docker) and heavily in Stage 16 (Kubernetes). AWS's equivalent is **ECR** (Elastic Container Registry).

⚠️ Images take storage. Set a **cleanup policy**: *Settings → Packages and registries → Container Registry cleanup policies* (e.g., keep last 10 tags).

### 6.2 Releases (know it exists)
A named version (e.g., `v1.2.0`) tied to a Git tag, with release notes and downloadable assets. Teams use it for versioned products/APIs.

### 6.3 Feature flags (know the concept)
Turn a feature on/off **without redeploying** (e.g., show the new upload UI to 10% of users). The concept is important; GitLab's own implementation is less common — teams often use LaunchDarkly, Unleash, or a config service.

- **Deploy vs. Release**: *deploy* = code is on the server; *release* = users can see it. Feature flags separate the two.

### 6.4 Package Registry (skip for now)
Private npm packages. Useful if your company shares internal libraries.

---

## 7. ⭐ Operate tab

### 7.1 Environments ⭐
After your `fake-deploy` job runs, open **Operate → Environments**. You'll see:
- Which commit is currently deployed to `staging`
- Full deployment history (who, when, which pipeline)
- **Re-deploy / Rollback** button to redeploy a previous successful deployment
- **Stop** environment (useful for temporary "review apps")

Common patterns:

```yaml
deploy-production:
  stage: deploy
  script:
    - echo "deploy to prod"
  environment:
    name: production
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual        # a human must click ▶️ — a "manual gate"
```

- **Review app**: a temporary environment per MR (e.g., `review/feature-login`) so reviewers can click and test.
- **Protected environments** (Paid): only certain people can deploy to `production`.

🇻🇳 Giải thích: **Environment** giống như "bảng theo dõi" cho biết phiên bản code nào đang chạy ở staging và production. Khi production bị lỗi sau khi deploy, đội DevOps thường vào đây để **rollback** (quay lại bản deploy trước đó) chỉ với một cú bấm.

### 7.2 Kubernetes clusters (Stage 16)
Connects GitLab to a cluster via the **GitLab agent for Kubernetes**. Skip until then.

### 7.3 Terraform states (later)
GitLab can store **Terraform state** (the file that remembers what infrastructure exists). Some teams use this instead of S3. We'll revisit when we start Terraform.

---

## 8. 👀 Monitor tab

Honestly: most companies **don't** use GitLab's Monitor tab for production monitoring. They use CloudWatch, Grafana, Datadog, Sentry, PagerDuty/Opsgenie (Stage 14).

Know these words though:
- **Alert**: an automatic signal that something crossed a threshold (e.g., error rate > 5%).
- **Incident**: a real problem affecting users, tracked until resolved, usually followed by a **postmortem** (a written review of what happened and how to prevent it).
- **Error tracking**: collecting app exceptions (GitLab's version is Sentry-compatible).

⏭️ Skip the rest.

---

## 9. ⭐ Settings (the most important tab for DevOps)

### 9.1 Settings → CI/CD → Variables ⭐⭐⭐
Where secrets and config for pipelines live. **This is the secure alternative to putting keys in code.**

| Option | Meaning | When to use |
|--------|---------|-------------|
| **Masked** | Value replaced by `[MASKED]` in job logs | All secrets |
| **Masked and hidden** | Also can't be viewed in the UI after saving | Very sensitive secrets |
| **Protected** | Only available in pipelines on **protected** branches/tags | Production credentials |
| **Expand variable reference** | `$OTHER_VAR` inside the value gets expanded | Turn **off** for passwords containing `$` |
| **Environment scope** | Only for `production`, `staging`, etc. | Different DB URLs per env |
| **Type: File** | Value is written to a temp file; variable holds the path | Certificates, kubeconfig |

🚨 **Classic beginner bug**: you mark a variable **Protected**, then run a pipeline on a feature branch → the variable is **empty**, and the job fails mysteriously. Protected variables only exist on protected branches.

🚨 Masking is a safety net, not a guarantee — `echo $SECRET | base64` would still leak it. Never print secrets.

🔐 **For AWS later (Stage 7):** the best practice is **OIDC** (OpenID Connect) — GitLab gives each job a short-lived identity token (`id_tokens:`), and AWS trades it for temporary credentials via an **IAM role**. **No long-lived AWS access keys stored anywhere.** Remember this term; it's what good DevOps teams use.

🇻🇳 Giải thích: **OIDC** cho phép GitLab "chứng minh danh tính" với AWS mỗi lần job chạy, và AWS cấp quyền tạm thời (hết hạn sau vài phút/giờ). Nhờ vậy bạn **không cần lưu AWS access key** trong GitLab — nếu bị lộ thì cũng không có key lâu dài nào để kẻ xấu dùng.

### 9.2 Settings → CI/CD → Runners ⭐
- **Instance (shared) runners**: provided by GitLab.com, use your compute minutes.
- **Group / project runners**: runners you install yourself (e.g., on an EC2 instance or in Kubernetes). Companies use self-hosted runners for speed, cost, private network access, and security.
- **Tags**: jobs can pick a runner with `tags: [docker, aws]`.

🚨 Job stuck in **pending** forever? Usually: no runner matches the job's tags, shared runners are disabled, or (on new GitLab.com accounts) identity/credit-card verification is required to use shared runners.

### 9.3 Settings → Repository → Protected branches / tags ⭐
- Protect `main`: **Allowed to push: No one**, **Allowed to merge: Maintainers**. Forces all changes through MRs.
- Protected tags (e.g., `v*`) so only maintainers can create releases.
- Remember: protection also controls access to **protected variables**.

### 9.4 Settings → Merge requests ⭐
- ✅ **Pipelines must succeed** — can't merge a red pipeline (Free).
- ✅ **All threads must be resolved**.
- Approval rules / required approvers — mostly Paid.

### 9.5 Tokens (know the differences)

| Token | Who/what it represents | Typical use |
|-------|----------------------|-------------|
| Personal access token | **You** | Scripts/API calls as yourself (avoid in CI) |
| Project/group access token | A bot user for the project | Automation; availability depends on plan |
| Deploy token | Read-only access to repo/registry | A server pulling Docker images |
| Deploy key | SSH key, repo access | A server doing `git pull` |
| `CI_JOB_TOKEN` | The current job, auto-expires | Accessing registry/APIs inside CI |

Rule: always use the **least-powerful, shortest-lived** token that works.

### 9.6 Other Settings (know they exist)
- **Webhooks / Integrations**: send pipeline events to Slack, Jira, etc.
- **Usage quotas**: compute minutes and storage used — check monthly.
- **General → Visibility**: private vs. public project; make sure your portfolio project doesn't expose secrets if public.

---

## 10. 🏢 How teams use this

**In real companies:**
- A **platform/DevOps team** maintains shared CI **templates** (`include:` from a central repo) so every service's pipeline looks the same.
- They run **self-hosted runners** (often on Kubernetes or EC2 autoscaling) to control cost and access private networks.
- Production deploys are behind a **manual gate** or protected environment, with rollback via Environments.
- Secrets live in CI/CD variables, or better, in an external secret manager (AWS Secrets Manager, HashiCorp Vault), with OIDC for cloud access.

**Jargon you'll hear:**
- "The pipeline is **red/green**." (failed/passed)
- "That test is **flaky**." (fails randomly)
- "Job is **stuck in pending** — no runner picked it up."
- "**Retry** the job." / "It's a **cache miss**."
- "Is that variable **protected**? You're on a feature branch."
- "Promote to prod." / "Hit the **manual gate**."
- "**Shift left** on security." / "Secret got **leaked, rotate it**."
- "**Merge train**" (Paid: queued MRs tested together before merging)

**Good questions to ask your DevOps team:**
1. "Do we use shared templates for `.gitlab-ci.yml`? Where are they?"
2. "Are our runners shared or self-hosted? What executor do they use?"
3. "How does CI authenticate to AWS — access keys in variables or OIDC roles?"
4. "How do we roll back a bad production deploy?"
5. "Which security scanners block a merge, and which only report?"

---

## 11. 📝 Summary

- **Build** = pipelines, jobs, logs, artifacts. `.gitlab-ci.yml` defines stages → jobs; runners execute them in fresh containers.
- **Secure** = scanners added as CI templates; Free gives reports, Ultimate gives dashboards. Leaked secret → rotate it.
- **Deploy** = Container Registry is the key feature; Releases and Feature flags are good to understand.
- **Operate** = Environments track what's deployed where and let you roll back.
- **Monitor** = mostly replaced by dedicated tools in real companies.
- **Settings** = CI/CD variables (masked/protected/scoped), runners, protected branches, MR rules. Protected variables only exist on protected branches.

---

## 12. 🛠️ Hands-on exercises

### Exercise 1 — First pipeline (25 min)
1. Create a new GitLab project `notes-api` and push a fresh NestJS app.
2. Open **Build → Pipeline editor**, paste the YAML from section 4.6, click **Validate**, then commit to `main`.
3. Watch the pipeline. Confirm `lint` and `unit-test` run **in parallel**.
4. Download the `build` job's artifact and check `dist/` is inside.
5. Open **Operate → Environments** and find `staging` with your commit SHA.
6. Break a test on purpose (e.g., change an expected value), push to a new branch, open an MR, and watch the pipeline go red.

### Exercise 2 — Secrets & protection (15 min)
1. **Settings → Repository → Protected branches**: protect `main` (push: No one, merge: Maintainers).
2. **Settings → Merge requests**: enable **Pipelines must succeed**.
3. **Settings → CI/CD → Variables**: add `DEMO_SECRET` = `super-secret-12345`, **Masked** + **Protected**.
4. Add a job:
   ```yaml
   check-secret:
     stage: test
     before_script: []
     script:
       - echo "Secret is $DEMO_SECRET"
       - '[ -n "$DEMO_SECRET" ] && echo "Variable exists" || echo "Variable is EMPTY"'
   ```
5. Run it on `main` → log shows `[MASKED]` and "Variable exists".
   Run it on a feature branch → "Variable is EMPTY". Now you understand the classic bug.
6. Bonus: add the Secret Detection template, commit a fake key like `AKIAIOSFODNN7EXAMPLE` (AWS's official example key) in a test branch, and look at the job's report. Delete the branch afterward.

> 💡 Compute minutes: these exercises use only a few minutes of your monthly quota. Check **Settings → Usage quotas** afterward.

---

## 13. ❓ Quiz (3 questions)

Reply in chat with your answers before opening the answers.

**Q1.** Your `build` job creates `dist/`. Your `deploy` job in the next stage says `dist/: No such file or directory`. You used `cache:` for `dist/`. What's wrong and how do you fix it?

**Q2.** A teammate's pipeline on branch `feature/upload` fails because `$AWS_ROLE_ARN` is empty, but it works on `main`. What's the most likely cause?

**Q3.** Someone accidentally committed a real API key and then pushed another commit deleting it. The Secret Detection job flagged it. Is the problem solved? What should they do?

<details>
<summary>👉 Click to reveal answers (only after replying!)</summary>

**A1.** Cache is only a speed optimization and isn't guaranteed to be restored (different runner, cache miss, etc.). To pass build output between jobs, use **`artifacts:`** with `paths: [dist/]`. Later-stage jobs download artifacts automatically.

**A2.** The variable is marked **Protected**, so it's only injected into pipelines running on **protected branches/tags** (like `main`). Feature branches don't get it. Fix: unprotect it (not recommended for production credentials), scope it differently, or only run that job on protected branches.

**A3.** **No.** The key is still in Git history (and possibly in clones, forks, CI logs). They must **revoke/rotate** the key immediately at the provider, create a new one, and store it in a masked CI/CD variable (or better, use OIDC/secret manager). Rewriting history is optional cleanup; rotating is mandatory.

</details>

---

## 14. 📋 Update your progress.md

- **Header**: `Current lesson: Lesson 4 – GitLab for DevOps` (next: Lesson 5 – Docker basics)
- **Completed lessons** table: add a row → `| <date> | S1-L4 GitLab for DevOps | x/3 | Pipelines, artifacts vs cache, protected vars, environments |`
- **AWS resources**: no changes (none created).
- **Weak topics**: add any quiz question you got wrong (e.g., "artifacts vs cache", "protected variables").
- **Questions to ask my DevOps team**: copy 1–2 questions from section 10.
- **Personal notes**: "Learn OIDC for GitLab → AWS in Stage 7 (no access keys)."
