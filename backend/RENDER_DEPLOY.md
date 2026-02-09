# Deploying Women Safety Backend on Render

This guide will help you deploy your FastAPI backend to Render.com.

## Prerequisites

1.  **Git Repository**: Ensure your code is pushed to GitHub.
2.  **Render Account**: Sign up at [dashboard.render.com](https://dashboard.render.com/).

## Step 1: Prepare your Repository (Already Done)

We have already:
1.  Created a `.gitignore` to exclude unnecessary files.
2.  Updated `core/config.py` to support dynamic CORS configurations.
3.  Verified `requirements.txt` and `app/main.py`.

You need to commit these changes:

```bash
git add .
git commit -m "Prepare backend for Render deployment"
git push origin main
```

*(Note: If you are in a subdirectory of a larger repo, push from the root)*

## Step 2: Create a Web Service on Render

1.  Log in to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  Give your service a name (e.g., `content-safety-backend`).

## Step 3: Configure the Service

Fill in the details as follows:

*   **Region**: Choose the one closest to your users (e.g., `Singapore` or `Frankfurt`).
*   **Branch**: `main` (or your working branch).
*   **Root Directory**: `backend` (IMPORTANT: Since your backend is in a folder).
*   **Runtime**: `Python 3`.
*   **Build Command**: `pip install -r requirements.txt`.
*   **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`.

## Step 4: Environment Variables

Scroll down to "Environment Variables" and add these:

| Key | Value | Description |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.0` | Ensures consistent Python version. |
| `ENVIRONMENT` | `production` | Sets app to production mode. |
| `SECRET_KEY` | *(Generate a random string)* | Used for security. |
| `DATABASE_URL` | *(See Step 5)* | Connection string for PostgreSQL. |
| `CORS_ORIGINS` | `https://your-frontend-app.onrender.com` | Allow your frontend to access the API. |
| `LOG_LEVEL` | `INFO` | Logging level. |

## Step 5: Database (PostgreSQL)

Your app requires a database.
1.  In Render Dashboard, click **New +** -> **PostgreSQL**.
2.  Create a database (e.g., `women-safety-db`).
3.  Copy the **Internal Database URL** from the database dashboard.
4.  Go back to your Web Service -> **Environment** and set `DATABASE_URL` to this value.

## Step 6: Deploy

Click **Create Web Service**. Render will start building your app. You can monitor the logs in the dashboard.

## Verification

Once deployed, visit your URL (e.g., `https://women-safety-backend.onrender.com/ping`) to verify it's running.
