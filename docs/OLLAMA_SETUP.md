# Ollama Setup Guide

Use **Ollama** for free, local, offline vision AI instead of cloud APIs.

## Installation

### 1. Install Ollama

**macOS/Windows:**
```bash
# Download from https://ollama.ai
# Or via Homebrew (macOS):
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
# Or: 
# apt-get install ollama (Ubuntu)
# pacman -S ollama (Arch)
```

### 2. Start Ollama

```bash
ollama serve
```

Leave this running in a terminal. It will start a server on `http://localhost:11434`

### 3. Download a Model

In another terminal, pick one:

```bash
# Best for vision: Gemma 2 (fast, accurate)
ollama pull gemma2:2b

# Or try these alternatives:
ollama pull llama2          # Good for text
ollama pull mistral         # Fast inference
ollama pull neural-chat     # Conversational
```

**First download takes 5-10 minutes** (depends on model size and internet speed)

### 4. Test Ollama

```bash
curl http://localhost:11434/api/tags
```

You should see a list of installed models.

## Using with JaydeEcho

Once Ollama is running with a model installed, just run:

```bash
python3 src/main.py
```

The app will automatically:
1. ✅ Detect Ollama running
2. ✅ Load available model
3. ✅ Use it for all vision tasks

**No API keys needed!**

## Advantages

| Feature | Ollama | Gemini API |
|---------|--------|-----------|
| Cost | Free ✅ | Free tier (limited) |
| Offline | Yes ✅ | No |
| Privacy | Local only ✅ | Google servers |
| Speed | Depends on PC | Fast (cloud) |
| Setup | 5 min | Requires API key |

## Fallback

If Ollama isn't running, the app automatically falls back to Gemini API (if you have a valid key).

## Troubleshooting

### "Ollama not running"
```bash
# Make sure ollama serve is running in another terminal
ollama serve
```

### "Model taking too long"
Ollama is loading the model into memory. First request can take 30-60s. Subsequent requests are faster.

### "Out of memory"
Try a smaller model:
```bash
ollama pull tinyllama  # ~1GB
ollama pull mistral:7b-text  # smaller
```

## Model Recommendations

| Model | Size | Speed | Quality | Vision |
|-------|------|-------|---------|--------|
| `tinyllama` | 0.4GB | ⚡⚡⚡ | Poor | No |
| `mistral:7b` | 4GB | ⚡⚡ | Good | No |
| `gemma2:2b` | 1.6GB | ⚡⚡ | Good | Yes |
| `llama2:13b` | 7GB | ⚡ | Great | No |

For JaydeEcho, use **gemma2:2b** (best balance) or **mistral** (faster).
