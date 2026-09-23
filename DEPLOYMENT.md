# 🚀 Aarambh Institute ERP — Production Deployment Guide

This guide walks you through deploying **Aarambh Institute ERP** to production with:
- **Backend & Database** on **Render** (via Infrastructure-as-Code Blueprint `render.yaml`)
- **Frontend** on **Vercel** (Next.js 16 Web Application)

---

## 📋 Architecture Overview

| Component | Platform | Configuration File |
| :--- | :--- | :--- |
| **Database** | Neon Cloud PostgreSQL (Existing) | Configured in `DATABASE_URL` |
| **FastAPI Backend** | Render Web Service | Declared in `render.yaml` (`aarambh-erp-backend`) |
| **Next.js Frontend** | Vercel | `frontend/vercel.json` |

---

## Part 1: Deploy Backend on Render (Blueprint)

### Step 1: Push Changes to GitHub
Make sure all your code is committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "feat: configure Render blueprint for backend and existing Neon database"
git push origin main
```

### Step 2: Create Blueprint on Render
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click the **"New +"** button in the top navigation bar.
3. Select **"Blueprint"**.
4. Connect your GitHub repository (`Aarambh Institute`).
5. Render will automatically parse [render.yaml](file:///d:/Aarambh%20Intitute/render.yaml) and display:
   - **Service**: `aarambh-erp-backend` (FastAPI Web Service)
   *(Note: Database is connected to your existing Neon PostgreSQL database).*
6. Click **"Apply"**.

Render will now:
- Build the backend using `pip install -r requirements.txt`.
- Automatically run any pending migrations on Neon via `alembic upgrade head`.
- Start the server with `gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --timeout 120 app.main:app`.

---

### Step 3: Seed Initial Data (Admin Account & Academic Structure)
Once the backend service status is **"Live"**:
1. In Render Dashboard, click on **`aarambh-erp-backend`**.
2. Click on the **"Shell"** tab on the left menu.
3. Run the idempotent database seed script:
   ```bash
   python -m app.db.seed_aarambh
   ```
4. You should see output confirming:
   - Institute created: `Aarambh Institute`
   - Campus created: `Hawa Bangla Campus`
   - Academic boards, classes, courses created
   - Teachers profiles created (Password: `AarambhTeacher@2026`)
   - Admin account created: `admin@aarambhinstitute.com` (Password: `AarambhAdmin@2026`)
   - Demo Student created: `student@aarambhinstitute.com` (Password: `AarambhStudent@2026`)

---

### Step 4: Copy Backend URL
In the Render dashboard, copy your backend URL. It will look like:
```text
https://aarambh-erp-backend.onrender.com
```

Test that the backend is healthy by opening in your browser:
- `https://aarambh-erp-backend.onrender.com/health` (should return `{"status":"ok"}`)
- `https://aarambh-erp-backend.onrender.com/` (should return app name and status)

---

## Part 2: Deploy Frontend on Vercel

### Step 1: Import Project in Vercel
1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **"Add New..."** -> **"Project"**.
3. Import your GitHub repository.

### Step 2: Configure Project Settings
In the **Configure Project** screen:
1. **Framework Preset**: Ensure `Next.js` is selected.
2. **Root Directory**: Click **Edit** and set it to:
   ```text
   frontend
   ```
   *(Important: Since this is a monorepo containing both backend and frontend, Vercel must build from the `frontend` folder!)*

### Step 3: Set Environment Variables
Under **Environment Variables**, add:

| Key | Value | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://aarambh-erp-backend.onrender.com` | Your Render backend URL (no trailing slash) |
| `NEXT_PUBLIC_RAZORPAY_KEY_ID` | `rzp_test_...` *(optional)* | Your Razorpay Key ID for student fee collection |

### Step 4: Click Deploy
Click **"Deploy"**. Vercel will install dependencies, build the Next.js application, and assign a production URL:
```text
https://aarambh-institute.vercel.app
```

---

## Part 3: Automated CI/CD Sync (Main Repo ➔ Vercel Repo)

Every time you push to `main` on your main repository (`VedanshTrivedi04/Aarambh-institue`), GitHub Actions automatically extracts the `frontend/` directory and pushes it to `VedanshTrivedi04/aarambhinstituevercel`.

### 🔑 One-Time Secret Setup
1. Go to your GitHub profile: **Settings ➔ Developer settings ➔ Personal access tokens ➔ Tokens (classic)** (or [click here](https://github.com/settings/tokens)).
2. Click **Generate new token (classic)**.
3. Note: `Vercel Repo Sync`
4. Select scope: **`repo`** (Full control of private repositories).
5. Click **Generate token** and copy it.
6. Now go to your **main repository** on GitHub (`VedanshTrivedi04/Aarambh-institue`):
   - Click **Settings ➔ Secrets and variables ➔ Actions**.
   - Click **New repository secret**.
   - Name: `VERCEL_REPO_SYNC_TOKEN`
   - Secret: Paste the token you copied.
   - Click **Add secret**.

Now, whenever you push any code to `main`, GitHub Actions will automatically sync `frontend/` to `aarambhinstituevercel`, triggering an instant Vercel build!

---

## Part 4: Verify Cross-Origin Resource Sharing (CORS)

The backend is pre-configured with:
- `CORS_ORIGIN_REGEX=https://.*\.vercel\.app`
  *(All Vercel preview and production deployments are automatically allowed!)*
- If you use a custom domain (e.g. `https://aarambhinstitute.com`):
  1. Open Render Dashboard -> `aarambh-erp-backend` -> **Environment**.
  2. Edit `CORS_ORIGINS` to include your custom domain:
     ```text
     https://aarambhinstitute.com,https://www.aarambhinstitute.com
     ```
  3. Render will redeploy with the updated origins.

---

## Part 5: Production Checklist & Smoke Test

- [ ] **Liveness & Readiness**:
  - Visit `https://<YOUR_RENDER_BACKEND>.onrender.com/health` -> `{"status":"ok"}`
  - Visit `https://<YOUR_RENDER_BACKEND>.onrender.com/api/v1/ready` -> `{"status":"ready", "checks":{"database":"ok"}}`
- [ ] **Public Website & Inquiries**:
  - Open your Vercel URL.
  - Fill out the "Book Free Counseling" or "Enroll Now" form.
  - Verify that the submission returns success (stored in PostgreSQL).
- [ ] **Admin Portal Login**:
  - Go to `/login`.
  - Log in with `admin@aarambhinstitute.com` / `AarambhAdmin@2026`.
  - Verify redirection to `/admin/dashboard`.
  - **Important**: Change the default admin password in production!
- [ ] **Razorpay Payment Gateway (Optional)**:
  - If accepting online fee payments, add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in Render Environment variables, and `NEXT_PUBLIC_RAZORPAY_KEY_ID` in Vercel.
