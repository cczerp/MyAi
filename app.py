from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from github import Github
import base64
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

# Environment variables
NEBIUS_API_KEY = os.environ.get('NEBIUS_API_KEY')
NEBIUS_API_URL = os.environ.get('NEBIUS_API_URL', 'https://api.studio.nebius.ai/v1/chat/completions')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_EMAIL = os.environ.get('GITHUB_EMAIL', 'your-email@example.com')
GITHUB_NAME = os.environ.get('GITHUB_NAME', 'Your Name')

# Initialize GitHub client
github_client = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None

# Available models (first 24 from Nebius)
MODELS = [
    {"id": "minimax/MiniMax-M2.1", "name": "MiniMax-M2.1", "provider": "Minimax"},
    {"id": "z.ai/GLM-4.7", "name": "GLM-4.7", "provider": "Z.ai"},
    {"id": "deepseek-ai/DeepSeek-V3.2", "name": "DeepSeek-V3.2", "provider": "DeepSeek"},
    {"id": "openai/gpt-oss-120b", "name": "gpt-oss-120b", "provider": "OpenAI"},
    {"id": "moonshot-ai/Kimi-K2-Instruct", "name": "Kimi-K2-Instruct", "provider": "Moonshot AI"},
    {"id": "moonshot-ai/Kimi-K2-Thinking", "name": "Kimi-K2-Thinking", "provider": "Moonshot AI"},
    {"id": "qwen/Qwen3-Coder-480B-A35B-Instruct", "name": "Qwen3-Coder-480B-A35B-Instruct", "provider": "Qwen"},
    {"id": "nous-research/Hermes-4-405B", "name": "Hermes-4-405B", "provider": "NousResearch"},
    {"id": "nous-research/Hermes-4-70B", "name": "Hermes-4-70B", "provider": "NousResearch"},
    {"id": "openai/gpt-oss-20b", "name": "gpt-oss-20b", "provider": "OpenAI"},
    {"id": "z.ai/GLM-4.5", "name": "GLM-4.5", "provider": "Z.ai"},
    {"id": "z.ai/GLM-4.5-Air", "name": "GLM-4.5-Air", "provider": "Z.ai"},
    {"id": "prime-intellect/INTELLECT-3", "name": "INTELLECT-3", "provider": "Prime Intellect"},
    {"id": "qwen/Qwen3-Next-80B-A3B-Thinking", "name": "Qwen3-Next-80B-A3B-Thinking", "provider": "Qwen"},
    {"id": "deepseek-ai/DeepSeek-R1-0528", "name": "DeepSeek-R1-0528", "provider": "DeepSeek"},
    {"id": "deepseek-ai/DeepSeek-R1-0528-fast", "name": "DeepSeek-R1-0528 (Fast)", "provider": "DeepSeek"},
    {"id": "qwen/Qwen3-235B-A22B-Thinking-2507", "name": "Qwen3-235B-A22B-Thinking-2507", "provider": "Qwen"},
    {"id": "qwen/Qwen3-235B-A22B-Instruct-2507", "name": "Qwen3-235B-A22B-Instruct-2507", "provider": "Qwen"},
    {"id": "qwen/Qwen3-30B-A3B-Thinking-2507", "name": "Qwen3-30B-A3B-Thinking-2507", "provider": "Qwen"},
    {"id": "qwen/Qwen3-30B-A3B-Instruct-2507", "name": "Qwen3-30B-A3B-Instruct-2507", "provider": "Qwen"},
    {"id": "qwen/Qwen3-Coder-30B-A3B-Instruct", "name": "Qwen3-Coder-30B-A3B-Instruct", "provider": "Qwen"},
    {"id": "qwen/Qwen3-32B", "name": "Qwen3-32B", "provider": "Qwen"},
    {"id": "qwen/Qwen3-32B-fast", "name": "Qwen3-32B (Fast)", "provider": "Qwen"},
    {"id": "nvidia/Llama-3.1-Nemotron-Ultra-253B-v1", "name": "Llama-3.1-Nemotron-Ultra-253B-v1", "provider": "NVIDIA"}
]

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/models', methods=['GET'])
def get_models():
    return jsonify({"models": MODELS})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    model = data.get('model')
    messages = data.get('messages', [])
    
    if not model or not messages:
        return jsonify({"error": "Model and messages are required"}), 400
    
    try:
        headers = {
            'Authorization': f'Bearer {NEBIUS_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'messages': messages,
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 4000)
        }
        
        response = requests.post(NEBIUS_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        return jsonify(response.json())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/github/repos', methods=['GET'])
def list_repos():
    if not github_client:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    try:
        user = github_client.get_user()
        repos = []
        for repo in user.get_repos():
            repos.append({
                'name': repo.name,
                'full_name': repo.full_name,
                'private': repo.private,
                'default_branch': repo.default_branch
            })
        return jsonify({"repos": repos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/github/repo/<path:repo_name>/tree', methods=['GET'])
def get_repo_tree(repo_name):
    if not github_client:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    branch = request.args.get('branch', None)
    
    try:
        repo = github_client.get_repo(repo_name)
        if not branch:
            branch = repo.default_branch
        
        tree = repo.get_git_tree(branch, recursive=True)
        files = []
        for item in tree.tree:
            if item.type == 'blob':  # Only files, not directories
                files.append({
                    'path': item.path,
                    'sha': item.sha,
                    'size': item.size
                })
        
        return jsonify({
            "files": files,
            "branch": branch,
            "repo": repo_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/github/file', methods=['GET'])
def get_file():
    if not github_client:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    repo_name = request.args.get('repo')
    file_path = request.args.get('path')
    branch = request.args.get('branch', None)
    
    if not repo_name or not file_path:
        return jsonify({"error": "repo and path are required"}), 400
    
    try:
        repo = github_client.get_repo(repo_name)
        if not branch:
            branch = repo.default_branch
        
        file_content = repo.get_contents(file_path, ref=branch)
        content = base64.b64decode(file_content.content).decode('utf-8')
        
        return jsonify({
            "content": content,
            "path": file_path,
            "sha": file_content.sha,
            "branch": branch
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/github/file', methods=['POST'])
def update_file():
    if not github_client:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    data = request.json
    repo_name = data.get('repo')
    file_path = data.get('path')
    content = data.get('content')
    branch = data.get('branch')
    commit_message = data.get('message', f'Update {file_path}')
    
    if not all([repo_name, file_path, content, branch]):
        return jsonify({"error": "repo, path, content, and branch are required"}), 400
    
    try:
        repo = github_client.get_repo(repo_name)
        
        # Try to get existing file
        try:
            file = repo.get_contents(file_path, ref=branch)
            # Update existing file
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=file.sha,
                branch=branch,
                committer={
                    'name': GITHUB_NAME,
                    'email': GITHUB_EMAIL
                }
            )
        except:
            # Create new file
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch,
                committer={
                    'name': GITHUB_NAME,
                    'email': GITHUB_EMAIL
                }
            )
        
        return jsonify({
            "success": True,
            "commit": result['commit'].sha,
            "message": "File updated successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/github/branches', methods=['GET'])
def get_branches():
    if not github_client:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    repo_name = request.args.get('repo')
    if not repo_name:
        return jsonify({"error": "repo is required"}), 400
    
    try:
        repo = github_client.get_repo(repo_name)
        branches = [branch.name for branch in repo.get_branches()]
        
        return jsonify({
            "branches": branches,
            "default_branch": repo.default_branch
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
