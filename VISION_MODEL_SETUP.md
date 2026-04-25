# Quick Fix: Install Vision Model for Ollama

Your app detected that **Gemma2 is a text-only model** and cannot process images.

## Solution: Install a Vision Model

### Option 1: LLaVA (Best, Recommended) 🌟

In a **new terminal**, run:

```bash
ollama pull llava
```

**Time:** ~15 minutes (first download)  
**Size:** ~5GB  
**Quality:** Excellent image understanding  
**Speed:** Good (handles complex images)

### Option 2: BakLLaVA (Faster)

```bash
ollama pull bakllava
```

**Time:** ~10 minutes  
**Size:** ~3GB  
**Quality:** Good  
**Speed:** Faster than LLaVA

---

## After Installation

1. **Keep `ollama serve` running** in terminal
2. **Restart the web app**: `python3 app.py`
3. **The app will auto-detect the vision model**
4. **Try "Describe Scene" again** - it will now work!

---

## What's Happening

| Model | Type | Can See Images? |
|-------|------|-----------------|
| Gemma2 | Text | ❌ No |
| LLaVA | Vision | ✅ Yes |
| BakLLaVA | Vision | ✅ Yes |

Your app was trying to show images to a text-only model - like asking a translator to describe a painting when they only speak words! 😄

---

## Verification

Once you install LLaVA, you should see in terminal:

```
✓ Ollama initialized with vision model: llava
```

Then the app will analyze images perfectly! 🎉
