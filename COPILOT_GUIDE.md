# GitHub Copilot Integration Guide

This document explains how to set up and use the GitHub Copilot AI features in the tg-gemini-bot.

## 🎯 Overview

The bot now integrates with GitHub Copilot SDK, providing advanced AI-powered programming assistance directly in your Telegram conversations. This feature allows you to ask coding questions, get code examples, debug issues, and more.

## 📋 Prerequisites

To use GitHub Copilot features, you need **one** of the following:

### Option 1: GitHub Copilot Subscription (Recommended)
1. A valid [GitHub Copilot subscription](https://github.com/features/copilot#pricing)
   - Individual: $10/month or $100/year
   - Business: $19/user/month
   - Free tier available with limited usage
2. GitHub Copilot CLI installed and authenticated

### Option 2: BYOK (Bring Your Own Key)
If you don't have a GitHub Copilot subscription, you can use your own API keys from:
- OpenAI (GPT-4, etc.)
- Azure OpenAI
- Anthropic (Claude)
- Local models via Ollama

## 🚀 Installation & Setup

### Step 1: Install GitHub Copilot CLI

Follow the [official installation guide](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli):

```bash
# For npm/npx users
npm install -g @github/copilot-cli

# Or use Homebrew (macOS/Linux)
brew install github-copilot-cli
```

### Step 2: Authenticate

```bash
# Login to GitHub Copilot CLI
copilot login

# Follow the prompts to authenticate with your GitHub account
```

### Step 3: Install Python SDK

The `github-copilot-sdk` package is already included in `requirements.txt`. Make sure to install all dependencies:

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check that copilot CLI is available
which copilot

# Test the CLI
copilot --version
```

## 💬 Using Copilot in Telegram

Once set up, you can use the following commands in your Telegram bot:

### Basic Usage

**Ask a question:**
```
/copilot How do I reverse a string in Python?
```

**Get code examples:**
```
/copilot Write a function to calculate factorial
```

**Debug help:**
```
/copilot What does "TypeError: 'NoneType' object is not subscriptable" mean?
```

**Explain concepts:**
```
/copilot Explain what is a REST API
```

### Session Management

**Start a new conversation:**
```
/copilot_new
```
This clears your conversation history and starts fresh.

**Get help:**
```
/copilot_help
```
Shows detailed information about Copilot features.

## 🔧 Advanced Configuration (BYOK)

If you want to use your own API keys instead of GitHub Copilot subscription, you can configure the Copilot SDK with custom providers.

### Using OpenAI

Edit `api/copilot_service.py` and modify the session creation:

```python
session = await self.client.create_session({
    "model": "gpt-4",
    "provider": {
        "type": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_key": os.environ.get("OPENAI_API_KEY"),
    },
})
```

### Using Azure OpenAI

```python
session = await self.client.create_session({
    "model": "gpt-4",
    "provider": {
        "type": "azure",
        "base_url": "https://your-resource.openai.azure.com",
        "api_key": os.environ.get("AZURE_OPENAI_KEY"),
        "azure": {
            "api_version": "2024-10-21",
        },
    },
})
```

### Using Ollama (Local Models)

```python
session = await self.client.create_session({
    "model": "deepseek-coder-v2:16b",
    "provider": {
        "type": "openai",
        "base_url": "http://localhost:11434/v1",
        # No API key needed for local Ollama
    },
})
```

## 🎨 Features & Capabilities

The GitHub Copilot integration provides:

### Programming Assistance
- Code examples in any language
- Syntax help and best practices
- Algorithm explanations
- Design pattern recommendations

### Debugging Help
- Error message explanations
- Stack trace analysis
- Bug fix suggestions
- Code review feedback

### Learning & Education
- Concept explanations
- Tutorial-style responses
- Step-by-step guides
- Resource recommendations

### Conversation Memory
- Each chat maintains its own conversation history
- Context is preserved across messages
- Use `/copilot_new` to start fresh

## 🔒 Privacy & Security

- Conversations are processed by GitHub Copilot's servers (or your configured provider)
- No conversation data is stored by the bot beyond the active session
- Each chat's history is isolated (private conversations stay private)
- Use `/copilot_new` to clear history at any time

## ⚠️ Limitations & Notes

1. **CLI Dependency**: The bot requires GitHub Copilot CLI to be installed and running
2. **Authentication**: You must be authenticated with GitHub Copilot or configure BYOK
3. **Rate Limits**: Subject to GitHub Copilot's usage limits and quotas
4. **Response Time**: May take a few seconds depending on query complexity
5. **Timeout**: Requests timeout after 60 seconds
6. **Model Selection**: Default is `gpt-4o`, can be customized in code

## 🐛 Troubleshooting

### Error: "GitHub Copilot SDK is not available"
- Install the SDK: `pip install github-copilot-sdk`
- Verify installation: `python3 -c "import copilot; print('OK')"`

### Error: "Permission denied" with Copilot binary
**This issue is now automatically fixed!** The bot will automatically detect and fix permission issues with the Copilot binary when it starts.

If you still encounter permission errors:
1. The fix is applied automatically on first use - try the command again
2. If it persists, manually fix permissions (replace `3.12` with your Python version):
   ```bash
   chmod +x ~/.local/lib/python3.12/site-packages/copilot/bin/copilot
   ```
3. Or reinstall: `pip install --force-reinstall github-copilot-sdk`

**Technical Details**: The `github-copilot-sdk` package includes a bundled binary that sometimes lacks execute permissions. The bot now automatically detects and fixes this during initialization.

### Error: "Failed to initialize Copilot SDK"
- Check that Copilot CLI is installed: `which copilot`
- Verify authentication: `copilot --version`
- Check CLI is in PATH

### Error: "Request timed out"
- The query was too complex or servers are slow
- Try breaking it into smaller questions
- Check your internet connection

### "No response received from Copilot"
- The model might have been overloaded
- Try again after a moment
- Check GitHub Copilot status page

## 📚 Additional Resources

- [GitHub Copilot SDK Documentation](https://github.com/github/copilot-sdk)
- [Copilot CLI Installation Guide](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)
- [GitHub Copilot Pricing](https://github.com/features/copilot#pricing)
- [Python SDK Examples](https://github.com/github/awesome-copilot/tree/main/cookbook/copilot-sdk/python)

## 💡 Example Conversations

### Example 1: Quick Code Snippet
```
You: /copilot Write a Python function to check if a number is prime

Bot: 🤖 GitHub Copilot:

Here's a function to check if a number is prime:

\`\`\`python
def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Check odd divisors up to sqrt(n)
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    
    return True

# Example usage
print(is_prime(17))  # True
print(is_prime(15))  # False
\`\`\`
...
```

### Example 2: Debugging Help
```
You: /copilot I'm getting "TypeError: list indices must be integers or slices, not str" in Python

Bot: 🤖 GitHub Copilot:

This error occurs when you try to access a list using a string as an index instead of an integer.

Common causes:
1. Using dictionary syntax on a list: `my_list['key']` instead of `my_list[0]`
2. Mixing up list and dictionary access
3. Using a variable that contains a string when you expected an integer

Example of the error:
\`\`\`python
my_list = [1, 2, 3]
print(my_list['0'])  # ERROR: '0' is a string, not integer
\`\`\`

Solution:
\`\`\`python
my_list = [1, 2, 3]
print(my_list[0])  # Correct: 0 is an integer
\`\`\`
...
```

### Example 3: Learning Concepts
```
You: /copilot What's the difference between async and sync programming in Python?

Bot: 🤖 GitHub Copilot:

Async vs Sync Programming in Python:

**Synchronous (Sync):**
- Code executes line by line, blocking until each operation completes
- One task must finish before the next begins
- Simple and straightforward
...
```

## 🤝 Contributing

If you want to enhance the Copilot integration, key areas to explore:
- Custom tool implementations
- Streaming responses for real-time output
- Image support for visual questions
- Custom system prompts for specific domains

---

**Questions or issues?** Open an issue on the GitHub repository!
