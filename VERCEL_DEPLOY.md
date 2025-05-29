# JewelryBox AI - Vercel Deployment Guide

## Prerequisites
- Vercel account
- GitHub repository connected to Vercel
- OpenAI API key

## Deployment Steps

### 1. Environment Variables
Set up these environment variables in your Vercel dashboard:

```
OPENAI_API_KEY=your_openai_api_key_here
ALLOWED_ORIGINS=*
```

### 2. Deploy to Vercel

**Option A: Automatic Deployment**
1. Connect your GitHub repository to Vercel
2. Vercel will automatically detect the `vercel.json` configuration
3. Deploy will trigger on every push to main branch

**Option B: Vercel CLI**
```bash
npm i -g vercel
vercel --prod
```

### 3. Verify Deployment

Once deployed, test these endpoints:
- `/api/health` - Health check
- `/` - Redirects to widget
- `/widget` - Chat interface
- `/chat` - API endpoint

### 4. Custom Domain (Optional)
1. Go to your Vercel project settings
2. Add your custom domain
3. Update CORS settings in production

## Project Structure for Vercel

```
.
├── api/
│   └── index.py          # Vercel entry point
├── src/
│   ├── app.py            # Main FastAPI application
│   ├── memory_manager.py # FAISS memory management
│   ├── prompts/          # JSON configurations
│   ├── images/           # Avatar images
│   └── templates/        # HTML templates
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md
```

## Key Differences from Docker Deployment

1. **Serverless Functions**: Each request runs in a separate container
2. **Cold Starts**: First request may be slower (~1-3 seconds)
3. **Memory Limitations**: 1GB RAM limit per function
4. **Timeout**: 30-second maximum execution time
5. **File System**: Read-only after deployment

## Performance Optimizations

1. **FAISS Index**: Consider using cloud storage for large indexes
2. **Caching**: Implement Redis or similar for session management
3. **CDN**: Static assets served via Vercel's edge network

## Troubleshooting

### Common Issues:
1. **Import Errors**: Check `sys.path` configuration in `api/index.py`
2. **Environment Variables**: Verify they're set in Vercel dashboard
3. **Cold Starts**: Consider serverless warming strategies
4. **Memory Limits**: Optimize FAISS index size

### Debug Commands:
```bash
vercel logs
vercel dev  # Local development
```

## Production Considerations

1. Replace `allow_origins=["*"]` with your domain
2. Implement rate limiting
3. Add authentication if needed
4. Monitor function usage and costs
5. Set up error tracking (Sentry, etc.) 