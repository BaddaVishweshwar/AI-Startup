# Claude API Setup Guide

## Quick Start

### 1. Get Your Claude API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy your API key (starts with `sk-ant-`)

### 2. Configure Your Backend

Add to `backend/.env`:
```bash
# Claude/Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### 3. Restart Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🎯 Using Claude Provider: claude-sonnet-4-20250514
```

## Benefits

✅ **Best SQL Generation**: Claude excels at structured tasks  
✅ **Fast Responses**: 3-5 seconds (vs 30-60 with Ollama)  
✅ **Superior Accuracy**: Fewer hallucinations and errors  
✅ **Large Context**: 200K tokens for complex schemas  
✅ **CamelAI Quality**: Professional-grade analysis  

## Cost

- **Model**: Claude Sonnet 4
- **Pricing**: ~$3 per million input tokens
- **Average Query**: ~5K tokens = $0.015 per query
- **Very affordable** for development and production

## Provider Priority

The system automatically selects the best available provider:

1. **Claude** (if `ANTHROPIC_API_KEY` set) - Best quality ⭐
2. **OpenAI** (if `OPENAI_API_KEY` set) - Good quality
3. **Ollama** (fallback) - Slow but works offline

## Verification

Test that Claude is working:

```bash
# Check backend logs for:
🎯 Using Claude Provider: claude-sonnet-4-20250514
```

Then try a query in the frontend:
- "What are the top 10 products by revenue?"
- Should respond in 3-5 seconds with accurate SQL

## Troubleshooting

### "Claude service is not available"
- Check that `ANTHROPIC_API_KEY` is set in `.env`
- Verify the key starts with `sk-ant-`
- Restart the backend server

### "anthropic package not installed"
```bash
pip install 'anthropic>=0.18.0'
```

### Still using Ollama
- Check `.env` file has the API key
- Restart backend completely
- Check logs for provider selection

## Features Enabled with Claude

- ✅ Multi-turn iterative reasoning (2-3 exploratory queries)
- ✅ Enhanced prompts with rich context
- ✅ Executive-level insights with specific numbers
- ✅ Intelligent visualization selection
- ✅ "Thoughts" display showing AI reasoning
- ✅ CamelAI-style structured output

## Next Steps

Once Claude is working:
1. Test with complex queries
2. Verify response times (should be 3-5s)
3. Check SQL accuracy (should be 95%+)
4. Review insights quality (should have specific numbers)

Enjoy CamelAI-quality results! 🎯
