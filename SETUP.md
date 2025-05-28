# JewelryBoxAI Setup Guide

## Prerequisites

1. **Docker Desktop** - Download and install from [docker.com](https://www.docker.com/products/docker-desktop/)
2. **OpenAI API Key** - Get one from [platform.openai.com](https://platform.openai.com/api-keys)

## Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd JewelryBoxAI_Bot
```

### 2. Create Environment File
Create a `.env` file in the root directory with your OpenAI API key:

```bash
# For Windows (PowerShell)
echo "OPENAI_API_KEY=your_actual_openai_api_key_here" > .env
echo "ALLOWED_ORIGINS=*" >> .env

# For Linux/Mac
echo "OPENAI_API_KEY=your_actual_openai_api_key_here" > .env
echo "ALLOWED_ORIGINS=*" >> .env
```

**Important**: Replace `your_actual_openai_api_key_here` with your real OpenAI API key!

### 3. Deploy the Application

#### Option A: Automated Deployment (Recommended)

**Windows:**
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

#### Option B: Manual Deployment
```bash
# Build the Docker image
docker build -t jewelrybox-ai:latest .

# Start the application
docker-compose up -d
```

### 4. Access the Application

Once deployed, you can access:
- **Main Application**: http://localhost:8000
- **Chat Widget**: http://localhost:8000/widget
- **API Documentation**: http://localhost:8000/docs

## Managing the Application

### View Logs
```bash
docker-compose logs -f
```

### Stop the Application
```bash
docker-compose down
```

### Restart the Application
```bash
docker-compose restart
```

### Update the Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Troubleshooting

### Common Issues

1. **"Docker is not running"**
   - Make sure Docker Desktop is started
   - On Windows, check the system tray for Docker icon

2. **"Port 8000 already in use"**
   - Stop any other applications using port 8000
   - Or change the port in `docker-compose.yml`

3. **"OpenAI API key not found"**
   - Verify your `.env` file exists and contains the correct API key
   - Make sure there are no extra spaces or quotes around the key

4. **"Build failed"**
   - Check your internet connection
   - Try running `docker system prune` to clean up Docker cache

### Health Check
The application includes a health check endpoint. You can verify it's running:
```bash
curl http://localhost:8000/
```

### Container Status
Check if the container is running:
```bash
docker ps
```

## Security Notes

- The `.env` file is git-ignored for security
- Never commit your actual OpenAI API key to version control
- The application runs as a non-root user inside the container
- CORS is configured to allow all origins by default (change for production)

## Production Deployment

For production deployment:
1. Set `ALLOWED_ORIGINS` to your specific domain
2. Use a reverse proxy (nginx) for SSL termination
3. Set up proper logging and monitoring
4. Use Docker secrets or environment variable injection for API keys 