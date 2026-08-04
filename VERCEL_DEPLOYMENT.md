# Vercel deployment

This repository is deployed as two Vercel projects connected to the same Git
repository. Vercel builds each application from its own root directory; the
Docker Compose and Dockerfiles remain available for local development only.

## 1. Prepare PostgreSQL

Create a hosted PostgreSQL database and use its pooled connection URL when the
provider offers one. Run the migration before deploying the backend:

```bash
psql "$DATABASE_URL" -f uwa-backend/migrations/001_saved_course_uniqueness.sql
```

The migration creates the constraint required by the saved-course endpoint's
`ON CONFLICT` clause. If duplicate `(user_id, course, section)` rows already
exist, clean them up before running the migration.

## 2. Backend project

Create a Vercel project with these settings:

- Root Directory: `uwa-backend`
- Framework Preset: Other (Vercel detects `app/index.py` as FastAPI)
- Python version: read from `.python-version`

Configure these Production environment variables:

```dotenv
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
FRONTEND_ORIGIN=https://your-frontend.vercel.app
CORS_ORIGINS=https://your-frontend.vercel.app
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
BOT_EMAIL=your-address@example.com
BOT_EMAIL_APP_PASSWORD=your-app-password
```

`FIREBASE_SERVICE_ACCOUNT_JSON` is the complete, single-line Firebase Admin
service-account JSON. It is a backend secret and must never use a `VITE_`
prefix.

Deploy the backend first and note its `https://...vercel.app` URL.

## 3. Frontend project

Create a second Vercel project from the same repository:

- Root Directory: `uwa-frontend`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`

Configure this Production environment variable using the backend deployment
URL, without a trailing slash:

```dotenv
VITE_BACKEND_URL=https://your-backend.vercel.app
```

The frontend's `vercel.json` sends deep links such as `/dashboard/courses` to
React Router.

## 4. Complete the cross-project configuration

After the frontend receives its final domain:

1. Set the backend's `FRONTEND_ORIGIN` and `CORS_ORIGINS` to that exact HTTPS
   origin, then redeploy the backend.
2. Add the frontend domain under Firebase Authentication > Settings >
   Authorized domains.
3. Redeploy a Vercel project whenever one of its environment variables changes.

For local development, copy each `.env.example` to `.env` and supply real local
values. The backend also supports the existing local `serviceAccountKey.json`
file when `FIREBASE_SERVICE_ACCOUNT_JSON` is not set.

## 5. Smoke tests

After both deployments finish, verify:

- `GET https://your-backend.vercel.app/`
- `https://your-backend.vercel.app/docs`
- course search through `/umd-api`
- signup and the verification-email redirect
- login and a saved course/section
- a hard refresh at `/dashboard/courses`

The saved-course endpoint now requires `Authorization: Bearer <Firebase ID
token>`. The frontend obtains that token from the currently signed-in Firebase
user; the request body contains only `course` and `section`.
