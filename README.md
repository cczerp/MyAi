# LLM Dashboard

A multi-model LLM chat interface with GitHub integration and dual-chat support.

## Features

- 🤖 **24 Nebius Models** - Access to top Nebius AI models
- 💬 **Dual Chat** - Run two conversations side-by-side with different models
- 📁 **GitHub Integration** - Browse repos, read/write files, auto-commit changes
- 🔄 **Context Sharing** - Share conversation history between chats
- 🎯 **Simple & Fast** - Streamlined UI focused on getting things done

## Setup Instructions for Render

### 1. Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "LLM Dashboard"
4. Select these scopes:
   - `repo` (full control of private repositories)
   - `user:email` (for commit attribution)
5. Generate token and **copy it** (you won't see it again!)

### 2. Get Your Nebius API Key

1. Log into your Nebius account
2. Navigate to API settings
3. Copy your API key

### 3. Deploy to Render

1. **Create a new Web Service** on Render
2. **Connect this repository** (or upload these files to a GitHub repo first)
3. **Configure the service:**
   - **Name:** `llm-dashboard` (or whatever you prefer)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free or Starter (recommended: Starter for better performance)

4. **Add Environment Variables:**
   Click "Environment" and add these:
   
   ```
   NEBIUS_API_KEY=your_nebius_api_key_here
   NEBIUS_API_URL=https://api.studio.nebius.ai/v1/chat/completions
   GITHUB_TOKEN=your_github_personal_access_token_here
   GITHUB_EMAIL=your-email@example.com
   GITHUB_NAME=Your Name
   ```

5. **Deploy!** - Render will automatically build and deploy your app

### 4. Access Your Dashboard

Once deployed, Render will give you a URL like: `https://llm-dashboard-xxxx.onrender.com`

Visit that URL and you're ready to go!

## Usage Guide

### Basic Chat

1. Select a model from the dropdown
2. Type your message
3. Hit Send

### Using GitHub Files

1. Click "Load Repos" in the sidebar
2. Click on a repository to select it
3. Choose a branch if needed
4. Click on any file to attach it to your chat
5. Files are automatically included in your message context

### Dual Chat Mode

1. Click "Open 2nd Chat" to show a second chat panel
2. Each chat can use a different model
3. Click "Share Context →" to copy Chat 1's history to Chat 2
4. Each chat maintains its own conversation independently

### File Writes

When the LLM suggests code changes or file modifications:
- The changes are automatically committed to the current branch
- Commits are attributed to your GitHub name/email
- Branch is whatever you selected in the dropdown

## Model List

The dashboard includes these 24 Nebius models:

1. MiniMax-M2.1
2. GLM-4.7
3. DeepSeek-V3.2
4. gpt-oss-120b
5. Kimi-K2-Instruct
6. Kimi-K2-Thinking
7. Qwen3-Coder-480B-A35B-Instruct
8. Hermes-4-405B
9. Hermes-4-70B
10. gpt-oss-20b
11. GLM-4.5
12. GLM-4.5-Air
13. INTELLECT-3
14. Qwen3-Next-80B-A3B-Thinking
15. DeepSeek-R1-0528
16. DeepSeek-R1-0528 (Fast)
17. Qwen3-235B-A22B-Thinking-2507
18. Qwen3-235B-A22B-Instruct-2507
19. Qwen3-30B-A3B-Thinking-2507
20. Qwen3-30B-A3B-Instruct-2507
21. Qwen3-Coder-30B-A3B-Instruct
22. Qwen3-32B
23. Qwen3-32B (Fast)
24. Llama-3.1-Nemotron-Ultra-253B-v1

## Architecture

- **Backend:** Flask (Python)
- **Frontend:** Vanilla HTML/CSS/JS
- **GitHub API:** PyGithub
- **LLM API:** Nebius via OpenAI-compatible endpoint
- **Hosting:** Render

## Troubleshooting

### "GitHub token not configured"
- Make sure `GITHUB_TOKEN` is set in Render environment variables
- Verify the token has correct permissions

### "Model not responding"
- Check that `NEBIUS_API_KEY` is correct
- Verify Nebius API is accessible from Render
- Check Render logs for API errors

### "Repository not loading"
- Ensure your GitHub token has access to the repos you want
- Private repos require full `repo` scope

## Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export NEBIUS_API_KEY=your_key
export GITHUB_TOKEN=your_token
export GITHUB_EMAIL=your-email@example.com
export GITHUB_NAME="Your Name"

# Run
python app.py
```

Visit `http://localhost:5000`

## Future Enhancements

- [ ] Better file write parsing from LLM responses
- [ ] Support for creating new branches
- [ ] File search functionality
- [ ] Export chat history
- [ ] Custom system prompts
- [ ] Temperature/max tokens controls
- [ ] More LLM providers (OpenAI, Anthropic, etc.)

## License

MIT
