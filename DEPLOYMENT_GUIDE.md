# LLM Dashboard - Complete Deployment Guide

## 🎯 What You're Building

A powerful AI chat dashboard that lets you:
- Chat with 24 different Nebius AI models
- Open two chats side-by-side with different models
- Browse your GitHub repositories
- Attach files from repos to your conversations
- Have the AI automatically commit changes to your repos

## 📦 What You Need

1. **Nebius Account** - for AI model access
2. **GitHub Account** - for repository integration
3. **Render Account** - for hosting (free tier works!)

---

## 🚀 Deployment Steps

### Step 1: Get Your Nebius API Key

1. Go to [Nebius Studio](https://studio.nebius.ai)
2. Log in or create an account
3. Navigate to **API Settings** or **API Keys**
4. Copy your API key
5. **Save it somewhere safe** - you'll need it for Render

**API Endpoint:** `https://api.studio.nebius.ai/v1/chat/completions`

---

### Step 2: Create GitHub Personal Access Token

1. Go to GitHub: [https://github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token"** → Select **"Tokens (classic)"**
3. Give it a descriptive name: `LLM Dashboard`
4. Set expiration: Choose what works for you (I recommend "No expiration" for personal use)
5. **Select these scopes:**
   - ✅ `repo` (Full control of private repositories)
   - ✅ `user:email` (Access user email addresses - for commit attribution)
6. Scroll down and click **"Generate token"**
7. **COPY THE TOKEN IMMEDIATELY** - you won't be able to see it again!
8. Save it somewhere safe

---

### Step 3: Push Code to GitHub (if not already there)

If you haven't already, create a new repository on GitHub:

```bash
# In your project directory
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/llm-dashboard.git
git push -u origin main
```

---

### Step 4: Deploy to Render

#### 4.1 Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - If first time: Click **"Connect Account"** and authorize Render
   - Select your `llm-dashboard` repository

#### 4.2 Configure Service

Fill in these settings:

- **Name:** `llm-dashboard` (or your preferred name)
- **Region:** Choose closest to you
- **Branch:** `main` (or whatever your default branch is)
- **Root Directory:** Leave blank
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Instance Type:** 
  - **Free** - works but slower
  - **Starter ($7/month)** - recommended for better performance

#### 4.3 Add Environment Variables

Scroll to **"Environment Variables"** section and click **"Add Environment Variable"** for each:

```
Key: NEBIUS_API_KEY
Value: [paste your Nebius API key]

Key: NEBIUS_API_URL
Value: https://api.studio.nebius.ai/v1/chat/completions

Key: GITHUB_TOKEN
Value: [paste your GitHub Personal Access Token]

Key: GITHUB_EMAIL
Value: your-email@example.com

Key: GITHUB_NAME
Value: Your Name
```

**Important:** 
- Use the SAME email and name you use for GitHub commits
- Don't include brackets `[]` - just paste the values

#### 4.4 Deploy!

1. Click **"Create Web Service"**
2. Render will start building your app (takes 2-5 minutes)
3. Watch the logs - you'll see:
   - Dependencies installing
   - Build completing
   - Service starting
4. Once you see **"Service is live"**, you're done!

---

### Step 5: Access Your Dashboard

1. Render will give you a URL like: `https://llm-dashboard-xxxx.onrender.com`
2. Click it or copy/paste into your browser
3. You should see your LLM Dashboard!

---

## 🎮 Using Your Dashboard

### Basic Chat

1. **Select a model** from the dropdown (24 options!)
2. **Type your message** in the text area
3. **Click Send**
4. Watch the AI respond!

### Recommended Models for Different Tasks

- **Coding:** Qwen3-Coder-480B, Qwen3-Coder-30B
- **Fast responses:** DeepSeek-V3.2, Qwen3-32B (Fast)
- **Deep thinking:** Kimi-K2-Thinking, DeepSeek-R1-0528
- **General chat:** GLM-4.7, Hermes-4-70B
- **Budget-friendly:** gpt-oss-20b, Gemma-2-2b-it

### GitHub Integration

#### Loading Your Repositories

1. Click **"Load Repos"** in the left sidebar
2. All your repos will appear
3. Click on any repo to select it

#### Browsing Files

1. After selecting a repo, files will load automatically
2. If you have multiple branches, select one from the dropdown
3. Click on any file to attach it to your chat

#### Using Files in Chat

- Attached files are automatically included in your message context
- The AI can see the full content of attached files
- Files stay attached until you remove them (click the × on the file tag)

### Dual Chat Mode

#### Opening Second Chat

1. Click **"Open 2nd Chat"** button
2. A second chat panel appears on the right
3. Each chat is completely independent

#### Use Cases for Dual Chat

- **Compare models:** Same question to two different models
- **Iterative development:** One chat for planning, one for implementation
- **Multi-task:** Work on two different features simultaneously

#### Sharing Context

1. Click **"Share Context →"** button
2. Confirms before copying
3. Copies all:
   - Chat history from Chat 1
   - Attached files
   - Message context
4. Chat 2 now has everything from Chat 1

---

## 🔧 Advanced Configuration

### Changing Models

Models are configured in `app.py`. To add more Nebius models:

1. Edit `app.py`
2. Find the `MODELS` array
3. Add new entries in this format:
   ```python
   {"id": "provider/model-name", "name": "Display Name", "provider": "Provider"}
   ```
4. Push changes to GitHub
5. Render will auto-redeploy

### Connecting Your Domain

If you have a custom domain (like `windowwanker...`):

1. In Render, go to your service
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain
4. Update DNS records as Render instructs
5. Wait for DNS propagation (can take up to 48 hours)

### Using with Cloudflare (windowwanker.com setup)

Your domain uses three subdomains with two different routing methods:

```
api.windowwanker.com  → CNAME to Render  (site & API)
www.windowwanker.com  → CNAME to api.windowwanker.com  (redirects to site)
llm.windowwanker.com  → Cloudflare Tunnel → localhost:11434  (local Ollama)
```

#### Step A: DNS Records in Cloudflare Dashboard

Go to **Cloudflare Dashboard → windowwanker.com → DNS → Records** and set:

| Type  | Name | Content                               | Proxy status |
|-------|------|---------------------------------------|--------------|
| CNAME | api  | `<your-render-slug>.onrender.com`     | Proxied (orange cloud) |
| CNAME | www  | `api.windowwanker.com`                | Proxied (orange cloud) |
| CNAME | llm  | `<TUNNEL-ID>.cfargotunnel.com`        | Proxied (orange cloud) |

The `llm` record is created automatically in step B - don't add it manually.

#### Step B: Cloudflare Tunnel for Ollama (llm subdomain)

The tunnel connects `llm.windowwanker.com` → your local Ollama instance.

**Install cloudflared on your local machine:**
```bash
# Linux
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Mac
brew install cloudflared

# Windows
winget install --id Cloudflare.cloudflared
```

**Create and configure the tunnel:**
```bash
# Authenticate (opens browser)
cloudflared tunnel login

# Create tunnel (save the ID it prints)
cloudflared tunnel create my-tunnel

# Add DNS route for llm subdomain
cloudflared tunnel route dns my-tunnel llm.windowwanker.com

# Create config file
mkdir -p ~/.cloudflared
```

**Copy `cloudflared-config.example.yml` from this repo to `~/.cloudflared/config.yml`** and fill in your tunnel ID and user path.

**The critical part** - make sure the ingress points to Ollama's port (11434):
```yaml
ingress:
  - hostname: llm.windowwanker.com
    service: http://localhost:11434  # Ollama default port
  - service: http_status:404
```

**Start the tunnel:**
```bash
# Run manually (test it works first)
cloudflared tunnel run my-tunnel

# Install as system service (runs on boot)
sudo cloudflared service install
sudo systemctl start cloudflared
```

**Verify Ollama is running before starting the tunnel:**
```bash
# Check Ollama is up
curl http://localhost:11434/api/tags

# Should return JSON with your installed models
```

#### Step C: Common Mistakes

**`llm.windowwanker.com` returns 404:**
- Tunnel is pointing to the wrong port (not 11434)
- Check your `~/.cloudflared/config.yml` - the service line must be `http://localhost:11434`
- Make sure Ollama is actually running: `ollama serve` or `systemctl start ollama`

**`www.windowwanker.com` returns 503 "Connection Refused":**
- `www` should be a plain CNAME to `api.windowwanker.com`, NOT a tunnel entry
- If you have `www` in your tunnel ingress config, remove it
- In Cloudflare DNS, `www` CNAME → `api.windowwanker.com` (proxied)

**Free models not responding in the app:**
- The Render app calls `https://llm.windowwanker.com/v1/chat/completions`
- This only works if the tunnel is running AND Ollama is running on port 11434
- Test the chain: `curl https://llm.windowwanker.com/api/tags` should return your model list

#### Step D: SSL/TLS Setting

In Cloudflare Dashboard → **SSL/TLS → Overview**, set mode to **Full** (not Full Strict, since the tunnel handles its own encryption).

---

## 🐛 Troubleshooting

### "GitHub token not configured"

**Problem:** Environment variable not set properly

**Solution:**
1. Go to Render dashboard
2. Click your service → Environment
3. Verify `GITHUB_TOKEN` is present and correct
4. If not, add it and redeploy

### "Error loading models"

**Problem:** Nebius API key issue

**Solution:**
1. Verify `NEBIUS_API_KEY` in Render environment
2. Check if key is still valid in Nebius dashboard
3. Make sure `NEBIUS_API_URL` is exactly: `https://api.studio.nebius.ai/v1/chat/completions`

### Model not responding

**Possible causes:**
- Model might be temporarily unavailable
- API rate limits hit
- Network issues

**Solution:**
1. Try a different model
2. Wait a few minutes and retry
3. Check Render logs for specific error messages

### Repository not loading

**Problem:** GitHub token permissions

**Solution:**
1. Verify token has `repo` scope
2. For private repos, ensure full `repo` access
3. Token might be expired - create a new one

### Service keeps crashing

**Solution:**
1. Check Render logs
2. Common issues:
   - Missing environment variables
   - Python dependency conflicts
3. Verify all dependencies in `requirements.txt` are compatible

---

## 💰 Cost Breakdown

### Render Hosting
- **Free Tier:** $0 (limited performance, sleeps after inactivity)
- **Starter:** $7/month (recommended, always on, better performance)
- **Pro:** $25/month (if you need more resources)

### Nebius API
- **Pay per use** - check Nebius pricing
- Most models: $0.02 - $2.00 per 1M tokens
- Some expensive models: $2-6 per 1M tokens

### GitHub
- **Free** - Personal Access Tokens are free

### Total Estimate
- **Minimal:** $0 + Nebius usage (if using Render free tier)
- **Recommended:** $7/month + Nebius usage

---

## 🔐 Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use environment variables** for all secrets
3. **Rotate tokens** every 90 days
4. **Limit GitHub token scope** to only what you need
5. **Monitor Nebius usage** to avoid unexpected bills

---

## 📈 Next Steps

Once your dashboard is running:

1. **Test all models** - see which ones you like best
2. **Attach your project repos** - start getting AI help with your code
3. **Experiment with dual chat** - compare model outputs
4. **Set up custom domain** - if you want a cleaner URL

---

## 🆘 Getting Help

If you run into issues:

1. Check Render logs first
2. Verify all environment variables
3. Test GitHub token permissions
4. Confirm Nebius API key is active

---

## 🎉 You're Done!

You now have a powerful AI dashboard that:
- ✅ Connects to 24 different AI models
- ✅ Integrates with your GitHub repos
- ✅ Supports dual conversations
- ✅ Auto-commits changes
- ✅ Is accessible from anywhere

Happy chatting! 🚀
