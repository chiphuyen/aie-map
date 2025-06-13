# Deployment Guide for AIE Map

## Deploying to Render.com (Actually Free!)

### Why Render?
- ✅ Actually has a free tier (unlike Railway)
- ✅ No credit card required
- ✅ Includes persistent storage
- ⚠️ Free apps sleep after 15 min inactivity (wake up in ~30 seconds)

### Deploy Steps:
1. **Push your code to GitHub**
2. **Go to [render.com](https://render.com)** and sign up
3. **Click "New +" → "Web Service"**
4. **Connect your GitHub repo**
5. **Render will auto-detect the configuration**
6. **Add environment variable**: 
   - `ADMIN_PASSWORD_HASH` = your bcrypt hash
7. **Click "Create Web Service"**

Your app will be live at `https://your-app.onrender.com`!

### Note about Free Tier:
- Your app will "sleep" after 15 minutes of no traffic
- First request after sleeping takes ~30 seconds to wake up
- Perfect for personal projects or demos
- Upgrade anytime if you need 24/7 uptime


## Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ADMIN_PASSWORD_HASH

# Run locally
python app.py
```

## Troubleshooting
- If OCR isn't working, ensure Tesseract is installed
- Database is stored in `data/aie_map.db`
- Uploads are stored in `data/uploads/`
- Check Railway logs for any deployment errors