# Deployment Guide

## ✅ Pre-deployment Checklist

Your AOG Family Devotional app is now ready for deployment! Here's what has been configured:

### Files Created/Updated:
- ✅ `Procfile` - Railway startup command
- ✅ `runtime.txt` - Python 3.12 specification
- ✅ `railway.toml` - Railway configuration
- ✅ `requirements.txt` - Dependencies with gunicorn
- ✅ `.env.example` - Environment variables template
- ✅ `.gitignore` - Git ignore file
- ✅ Updated `main.py` - Static file serving
- ✅ Updated `script.js` - Production URLs
- ✅ Updated `README.md` - Deployment instructions

## 🚀 Quick Deploy to Railway

### Option 1: GitHub Integration (Recommended)
```bash
# 1. Initialize git and push to GitHub
git init
git add .
git commit -m "Ready for Railway deployment"
git remote add origin https://github.com/yourusername/aog-devo.git
git push -u origin main
```

### Option 2: Railway CLI
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway deploy
```

## 🔧 Environment Variables to Set

In Railway Dashboard → Variables tab, add:

```
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

## 🌐 Alternative: Render Deployment

1. Visit [render.com](https://render.com)
2. "New" → "Web Service" 
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables in dashboard

## 📋 Post-Deployment Testing

Once deployed, test these URLs:
- `https://your-app.up.railway.app/` - Frontend
- `https://your-app.up.railway.app/api` - API health
- `https://your-app.up.railway.app/health` - Health check

## 🎯 What's Included

Your deployed app will have:
- ✅ Combined frontend + backend (single URL)
- ✅ Official AOG devotional format
- ✅ Age-appropriate content generation
- ✅ Mobile-responsive design
- ✅ HTTPS security
- ✅ Environment variable configuration

## 💡 Tips

- Railway provides $5 free credits monthly
- App sleeps on Render free tier after 15min inactivity
- Both platforms provide automatic HTTPS
- Monitor usage through their dashboards

## 📞 Need Help?

If you encounter issues:
1. Check deployment logs in Railway/Render dashboard
2. Verify environment variables are set correctly
3. Ensure your GitHub repo is public or properly connected

Happy deploying! 🚀