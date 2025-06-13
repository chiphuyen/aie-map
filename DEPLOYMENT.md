# Deployment Guide for AIE Map

## Deploying to Render.com (Actually Free!)

### Why Render?
- ✅ Actually has a free tier (unlike Railway)
- ✅ No credit card required
- ✅ Includes persistent storage
- ⚠️ Free apps sleep after 15 min inactivity (wake up in ~30 seconds)

### Deploy Steps:

#### Step 1: Prepare Your Code
1. **Generate your admin password hash** (keep this safe!):
   ```bash
   python generate_password_hash.py
   ```
   Save the output in your password manager - you'll need it later.

2. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push
   ```

#### Step 2: Deploy on Render (Dashboard Method)
1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repo** (make sure it's public)
   - If repos don't show: paste your GitHub URL directly
   - Format: `https://github.com/YOUR_USERNAME/aie-map`
4. **Render will auto-detect the configuration from `render.yaml`**
5. **Click "Create Web Service"**

#### Step 3: Add Admin Password (AFTER Deployment)
1. **Wait for deployment to complete** (5-10 minutes)
2. **In Render dashboard**, click on your service
3. **Go to "Environment" tab**
4. **Add your secret**:
   - Key: `ADMIN_PASSWORD_HASH`
   - Value: (paste your hash from Step 1)
5. **Click "Save Changes"** - Render will redeploy automatically

Your app will be live at `https://your-app.onrender.com`!

### Using Render CLI (Limited Use)

The Render CLI is **only for managing existing services**, not creating new ones:

```bash
# Install (if needed)
brew install render

# Login
render login

# After your service is created, you can:
render logs --tail              # View logs
render services                 # List services
render restart                  # Restart service
render deploys                  # View deployments
```

**Note**: You CANNOT create new services via CLI. Use the dashboard!

## 🔐 Security Best Practices

### Password Hash Management

**NEVER put your password hash in:**
- ❌ Any source code file
- ❌ Git commits  
- ❌ Shell scripts
- ❌ Documentation

**ALWAYS put your password hash in:**
- ✅ Environment variables (via platform dashboard)
- ✅ .env file (that's gitignored) for local development only
- ✅ Your password manager

### What NOT to do:
```bash
# NEVER do this:
echo "ADMIN_PASSWORD_HASH=xyz" >> deploy.sh  # ❌ WRONG
git commit -m "Add password"                  # ❌ WRONG
```

### What TO do:
1. Generate hash locally with `python generate_password_hash.py`
2. Store in password manager
3. Deploy app first
4. Add hash via platform dashboard
5. Never commit sensitive data

### If You Accidentally Exposed Your Hash:
1. Generate a new password hash immediately
2. Update it on your deployed service
3. Remove from git history if needed:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```

**Remember**: The app works without admin features until you add the hash, so deploy first, configure secrets later!

### Note about Free Tier:
- Your app will "sleep" after 15 minutes of no traffic
- First request after sleeping takes ~30 seconds to wake up
- Perfect for personal projects or demos
- Upgrade anytime if you need 24/7 uptime

## Troubleshooting

### If GitHub repos don't appear:
1. **Make sure your repo is PUBLIC** (Render free tier only sees public repos)
2. **Re-authorize Render** in GitHub settings
3. **Try a different browser** or incognito mode
4. **Alternative**: Use Git URL directly in Render

### If deployment fails:
- Check the build logs in Render dashboard
- Common issues:
  - Missing `chmod +x build.sh` (we already did this)
  - Tesseract installation issues (rare)
  - Port binding issues (we handle this)

### If admin login doesn't work:
- Make sure you added `ADMIN_PASSWORD_HASH` in Environment tab
- Check it's the exact hash from `generate_password_hash.py`
- Wait for Render to redeploy after adding the variable

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract (for OCR)
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr

# Create .env file
cp .env.example .env
# Edit .env and add your ADMIN_PASSWORD_HASH

# Run locally
python app.py
```

## Security Reminders

### ⚠️ What NOT to do:
```bash
# NEVER do this:
echo "ADMIN_PASSWORD_HASH=xyz" >> deploy.sh  # ❌ WRONG
git commit -m "Add password"                  # ❌ WRONG
```

### ✅ What TO do:
1. Generate hash locally
2. Store in password manager
3. Deploy app first
4. Add hash via platform dashboard
5. Never commit sensitive data

## Alternative Platforms

If Render doesn't work for you:

### Glitch.com (Easiest, no GitHub needed)
1. Go to [glitch.com](https://glitch.com)
2. New Project → Import from GitHub (or upload files)
3. It auto-runs your app

### PythonAnywhere.com
1. Free Python hosting
2. Manual file upload
3. Good for simple apps

### Replit.com
1. Online IDE + hosting
2. Import from GitHub
3. Automatic deployment