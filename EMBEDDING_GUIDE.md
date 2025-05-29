# JewelryBox AI Widget - Embedding Guide

## Quick Start: Docker Deployment for Embedding

### 1. Deploy Widget
```bash
# Linux/Mac
./deploy-widget.sh

# Windows (PowerShell)
.\deploy-widget.ps1
```

### 2. Embed in GoHighLevel (GHL)

#### Option A: iFrame Embedding
```html
<iframe 
  src="http://your-domain:8000/widget" 
  width="400" 
  height="600"
  frameborder="0"
  style="border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
</iframe>
```

#### Option B: Custom HTML Widget (GHL)
1. **Go to Sites → Funnels/Websites**
2. **Add Element → Custom Code/HTML**
3. **Paste the iframe code above**
4. **Replace `your-domain` with your actual domain**

### 3. Production Deployment URLs

```
Widget:     https://your-domain.com/widget
Chat API:   https://your-domain.com/chat
Health:     https://your-domain.com/
```

## Advanced Embedding Options

### Responsive Embedding
```html
<div style="position: relative; width: 100%; max-width: 400px;">
  <iframe 
    src="https://your-domain.com/widget"
    style="width: 100%; height: 600px; border: none; border-radius: 8px;"
    allow="microphone">
  </iframe>
</div>
```

### Modal/Popup Embedding
```html
<!-- Trigger Button -->
<button onclick="openJewelryChat()" class="jewelry-chat-btn">
  💎 Chat with Jewelry Expert
</button>

<!-- Modal Overlay -->
<div id="jewelry-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999;">
  <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 420px; height: 620px; background: white; border-radius: 12px; overflow: hidden;">
    <iframe src="https://your-domain.com/widget" width="100%" height="100%" frameborder="0"></iframe>
    <button onclick="closeJewelryChat()" style="position: absolute; top: 10px; right: 15px; background: none; border: none; font-size: 20px; cursor: pointer;">×</button>
  </div>
</div>

<script>
function openJewelryChat() {
  document.getElementById('jewelry-modal').style.display = 'block';
}
function closeJewelryChat() {
  document.getElementById('jewelry-modal').style.display = 'none';
}
</script>
```

## Platform-Specific Integration

### GoHighLevel (GHL)
- **Location**: Funnels → Custom HTML Element
- **Size**: 400px × 600px recommended
- **Permissions**: Ensure iframe permissions are enabled

### WordPress
```php
// Add to functions.php or use shortcode plugin
function jewelrybox_widget_shortcode() {
    return '<iframe src="https://your-domain.com/widget" width="400" height="600" frameborder="0"></iframe>';
}
add_shortcode('jewelrybox_chat', 'jewelrybox_widget_shortcode');

// Usage: [jewelrybox_chat]
```

### Squarespace
1. **Add Code Block**
2. **Paste iframe HTML**
3. **Adjust styling as needed**

### Shopify
```liquid
<!-- In theme templates -->
<div class="jewelry-chat-widget">
  <iframe 
    src="{{ settings.jewelry_chat_url | default: 'https://your-domain.com/widget' }}"
    width="400" 
    height="600"
    loading="lazy">
  </iframe>
</div>
```

## Production Setup

### 1. Domain Configuration
```bash
# Update docker-compose.yml environment
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - ALLOWED_ORIGINS=https://yourdomain.com,https://ghl-subdomain.com
```

### 2. SSL/HTTPS Setup
```nginx
# Nginx reverse proxy configuration
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. CORS Configuration
The widget is pre-configured with CORS support. For production, update `ALLOWED_ORIGINS` in your environment variables.

## Testing & Debugging

### Widget Health Check
```bash
curl https://your-domain.com/widget
```

### API Testing
```bash
curl -X POST https://your-domain.com/chat \
  -H "Content-Type: application/json" \
  -d '{"user_input":"Hello", "history":[]}'
```

### Browser Console
```javascript
// Test widget connectivity
fetch('https://your-domain.com/widget')
  .then(response => console.log('Widget Status:', response.status))
  .catch(error => console.error('Widget Error:', error));
```

## Customization

### Widget Styling
The widget inherits parent container styles. You can wrap it in a styled container:

```html
<div class="jewelry-widget-container">
  <iframe src="https://your-domain.com/widget"></iframe>
</div>

<style>
.jewelry-widget-container {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  overflow: hidden;
  background: white;
}
</style>
```

### Mobile Optimization
```css
@media (max-width: 768px) {
  .jewelry-widget-container iframe {
    width: 100vw;
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 9999;
  }
}
```

## Support & Monitoring

### Container Logs
```bash
docker-compose logs -f jewelrybox-ai
```

### Health Monitoring
```bash
# Set up health check endpoint monitoring
watch -n 30 'curl -s https://your-domain.com/ | grep -o "status.*"'
```

---

**Need Help?** Check the troubleshooting section in the main README.md or review Docker logs for detailed error information. 