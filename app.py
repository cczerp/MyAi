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

# Available models (first 24 from Nebius) with correct IDs from their API docs
MODELS = [
    {"id": "MiniMaxAI/MiniMax-M2.1", "name": "MiniMax-M2.1", "provider": "Minimax"},
    {"id": "zai-org/GLM-4.7-FP8", "name": "GLM-4.7", "provider": "Z.ai"},
    {"id": "deepseek-ai/DeepSeek-V3.2", "name": "DeepSeek-V3.2", "provider": "DeepSeek"},
    {"id": "openai/gpt-oss-120b", "name": "gpt-oss-120b", "provider": "OpenAI"},
    {"id": "moonshotai/Kimi-K2-Instruct", "name": "Kimi-K2-Instruct", "provider": "Moonshot AI"},
    {"id": "moonshotai/Kimi-K2-Thinking", "name": "Kimi-K2-Thinking", "provider": "Moonshot AI"},
    {"id": "Qwen/Qwen3-Coder-480B-A35B-Instruct", "name": "Qwen3-Coder-480B-A35B-Instruct", "provider": "Qwen"},
    {"id": "NousResearch/Hermes-4-405B", "name": "Hermes-4-405B", "provider": "NousResearch"},
    {"id": "NousResearch/Hermes-4-70B", "name": "Hermes-4-70B", "provider": "NousResearch"},
    {"id": "openai/gpt-oss-20b", "name": "gpt-oss-20b", "provider": "OpenAI"},
    {"id": "zai-org/GLM-4.5", "name": "GLM-4.5", "provider": "Z.ai"},
    {"id": "zai-org/GLM-4.5-Air", "name": "GLM-4.5-Air", "provider": "Z.ai"},
    {"id": "PrimeIntellect/INTELLECT-3", "name": "INTELLECT-3", "provider": "Prime Intellect"},
    {"id": "Qwen/Qwen3-Next-80B-A3B-Thinking", "name": "Qwen3-Next-80B-A3B-Thinking", "provider": "Qwen"},
    {"id": "deepseek-ai/DeepSeek-R1-0528", "name": "DeepSeek-R1-0528", "provider": "DeepSeek"},
    {"id": "deepseek-ai/DeepSeek-R1-0528-fast", "name": "DeepSeek-R1-0528 (Fast)", "provider": "DeepSeek"},
    {"id": "Qwen/Qwen3-235B-A22B-Thinking-2507", "name": "Qwen3-235B-A22B-Thinking-2507", "provider": "Qwen"},
    {"id": "Qwen/Qwen3-235B-A22B-Instruct-2507", "name": "Qwen3-235B-A22B-Instruct-2507", "provider": "Qwen"},
    {"id": "Qwen/Qwen3-30B-A3B-Thinking-2507", "name": "Qwen3-30B-A3B-Thinking-2507", "provider": "Qwen"},
    {"id": "Qwen/Qwen3-30B-A3B-Instruct-2507", "name": "Qwen3-30B-A3B-Instruct-2507", "provider": "Qwen"},
    {"id": "Qwen/Qwen3-Coder-30B-A3B-Instruct", "name": "Qwen3-Coder-30B-A3B-Instruct", "provider": "Qwen"},
    {"id": "Qwen/Qwen3-32B", "name": "Qwen3-32B", "provider": "Qwen"},
    {"id": "Qwen/Qwen3-32B-fast", "name": "Qwen3-32B (Fast)", "provider": "Qwen"},
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
    repo_context = data.get('repo_context')  # {repo, branch}

    if not model or not messages:
        return jsonify({"error": "Model and messages are required"}), 400

    try:
        headers = {
            'Authorization': f'Bearer {NEBIUS_API_KEY}',
            'Content-Type': 'application/json'
        }

        # Add system prompt for efficient tool usage when repo is connected
        if repo_context:
            system_prompt = """You are a helpful coding assistant with access to a GitHub repository. You can read and edit files.

EFFICIENCY GUIDELINES - Follow these to avoid running out of steps:
1. READ files only ONCE. Don't re-read files you've already seen.
2. Use edit_file with replace_all=true for bulk changes (e.g., changing all occurrences of a color).
3. PLAN your edits first, then execute them efficiently.
4. For color scheme changes: identify all unique colors, then use edit_file with replace_all=true for each color.
5. Combine related changes - don't make separate calls for the same type of change.
6. You have a maximum of 25 tool calls, so be efficient!

TOOL TIPS:
- edit_file: Best for targeted changes. Use old_text/new_text with replace_all=true for global find-replace.
- write_file: Only use for new files or complete rewrites. Avoid for small edits.
- list_files: Use to discover available files before reading."""

            # Prepend system message if not already present
            if not messages or messages[0].get('role') != 'system':
                messages = [{'role': 'system', 'content': system_prompt}] + messages

        # Define tools for GitHub file operations
        tools = []
        if repo_context:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "description": f"Read the contents of any file from the repository {repo_context['repo']} on branch {repo_context['branch']}",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file in the repository (e.g., 'src/app.py', 'README.md')"
                                }
                            },
                            "required": ["file_path"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "write_file",
                        "description": f"Write or update a file in the repository {repo_context['repo']} on branch {repo_context['branch']}. Changes are automatically committed. Use this for creating new files or complete rewrites.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file in the repository"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The complete content to write to the file"
                                },
                                "commit_message": {
                                    "type": "string",
                                    "description": "Commit message describing the changes"
                                }
                            },
                            "required": ["file_path", "content", "commit_message"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "edit_file",
                        "description": f"Edit a file by replacing specific text. Use this for making targeted changes to existing files - much more efficient than rewriting the whole file. You can call this multiple times to make multiple changes.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file in the repository"
                                },
                                "old_text": {
                                    "type": "string",
                                    "description": "The exact text to find and replace (must match exactly)"
                                },
                                "new_text": {
                                    "type": "string",
                                    "description": "The new text to replace it with"
                                },
                                "replace_all": {
                                    "type": "boolean",
                                    "description": "If true, replace ALL occurrences. If false (default), replace only the first occurrence."
                                },
                                "commit_message": {
                                    "type": "string",
                                    "description": "Commit message describing the change"
                                }
                            },
                            "required": ["file_path", "old_text", "new_text", "commit_message"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_files",
                        "description": f"List all files in the repository {repo_context['repo']} on branch {repo_context['branch']}",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            ]
        
        payload = {
            'model': model,
            'messages': messages,
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 4000)
        }
        
        if tools:
            payload['tools'] = tools
            payload['tool_choice'] = 'auto'
        
        response = requests.post(NEBIUS_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()

        # Ensure the response has the expected OpenAI format
        if 'choices' not in result or not result['choices']:
            return jsonify({"error": f"Unexpected API response format - no choices: {result}"}), 500

        # Validate that the first choice has a message
        first_choice = result['choices'][0]
        if 'message' not in first_choice:
            return jsonify({"error": f"Unexpected API response format - no message in choice: {first_choice}"}), 500

        return jsonify(result)
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
        return jsonify({"error": error_msg}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/execute_tool', methods=['POST'])
def execute_tool():
    """Execute a tool call from the LLM"""
    data = request.json
    tool_name = data.get('tool_name')
    arguments = data.get('arguments', {})
    repo_context = data.get('repo_context')
    
    if not tool_name:
        return jsonify({"error": "tool_name is required"}), 400
    
    try:
        if tool_name == 'read_file':
            file_path = arguments.get('file_path')
            if not file_path or not repo_context:
                return jsonify({"error": "file_path and repo_context required"}), 400
            
            repo = github_client.get_repo(repo_context['repo'])
            file_content = repo.get_contents(file_path, ref=repo_context['branch'])
            content = base64.b64decode(file_content.content).decode('utf-8')
            
            return jsonify({
                "success": True,
                "content": content,
                "path": file_path
            })
        
        elif tool_name == 'write_file':
            file_path = arguments.get('file_path')
            content = arguments.get('content')
            commit_message = arguments.get('commit_message', f'Update {file_path}')
            
            if not all([file_path, content, repo_context]):
                return jsonify({"error": "file_path, content, and repo_context required"}), 400
            
            repo = github_client.get_repo(repo_context['repo'])
            branch = repo_context['branch']
            
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
                "message": f"Committed changes to {file_path}"
            })

        elif tool_name == 'edit_file':
            file_path = arguments.get('file_path')
            old_text = arguments.get('old_text')
            new_text = arguments.get('new_text')
            replace_all = arguments.get('replace_all', False)
            commit_message = arguments.get('commit_message', f'Edit {file_path}')

            if not all([file_path, old_text is not None, new_text is not None, repo_context]):
                return jsonify({"error": "file_path, old_text, new_text, and repo_context required"}), 400

            repo = github_client.get_repo(repo_context['repo'])
            branch = repo_context['branch']

            # Get existing file
            try:
                file = repo.get_contents(file_path, ref=branch)
                current_content = base64.b64decode(file.content).decode('utf-8')
            except Exception as e:
                return jsonify({"error": f"Could not read file: {str(e)}"}), 400

            # Check if old_text exists in the file
            if old_text not in current_content:
                return jsonify({
                    "success": False,
                    "error": f"Could not find the specified text in {file_path}. Make sure old_text matches exactly."
                })

            # Count occurrences
            count = current_content.count(old_text)

            # Replace the text
            if replace_all:
                new_content = current_content.replace(old_text, new_text)
            else:
                new_content = current_content.replace(old_text, new_text, 1)

            # Update the file
            result = repo.update_file(
                path=file_path,
                message=commit_message,
                content=new_content,
                sha=file.sha,
                branch=branch,
                committer={
                    'name': GITHUB_NAME,
                    'email': GITHUB_EMAIL
                }
            )

            replaced_msg = f"all {count} occurrences" if replace_all else "1 occurrence"
            return jsonify({
                "success": True,
                "commit": result['commit'].sha,
                "message": f"Edited {file_path}: replaced {replaced_msg} successfully"
            })

        elif tool_name == 'list_files':
            if not repo_context:
                return jsonify({"error": "repo_context required"}), 400
            
            repo = github_client.get_repo(repo_context['repo'])
            tree = repo.get_git_tree(repo_context['branch'], recursive=True)
            files = [item.path for item in tree.tree if item.type == 'blob']
            
            return jsonify({
                "success": True,
                "files": files
            })
        
        else:
            return jsonify({"error": f"Unknown tool: {tool_name}"}), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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

@app.route('/api/github/repo/select', methods=['POST'])
def select_repo():
    if not github_client:
        return jsonify({"error": "GitHub token not configured"}), 500
    
    data = request.json
    repo_name = data.get('repo')
    base_branch = data.get('base_branch')
    
    if not repo_name:
        return jsonify({"error": "repo is required"}), 400
    
    try:
        repo = github_client.get_repo(repo_name)
        
        # Get base branch if not specified
        if not base_branch:
            base_branch = repo.default_branch
        
        # Create a new branch name with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        new_branch_name = f"chat-{timestamp}"
        
        # Get the base branch reference
        base_ref = repo.get_git_ref(f"heads/{base_branch}")
        base_sha = base_ref.object.sha
        
        # Create new branch from base
        repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_sha)
        
        # Get all files in the repo
        tree = repo.get_git_tree(new_branch_name, recursive=True)
        files = []
        for item in tree.tree:
            if item.type == 'blob':  # Only files
                files.append({
                    'path': item.path,
                    'sha': item.sha,
                    'size': item.size
                })
        
        return jsonify({
            "success": True,
            "branch": new_branch_name,
            "base_branch": base_branch,
            "repo": repo_name,
            "files": files,
            "message": f"Created branch '{new_branch_name}' from '{base_branch}'"
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
