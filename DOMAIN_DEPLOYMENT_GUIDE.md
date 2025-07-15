# Domain Deployment Guide for LinkAbet

## Custom Domain Setup (xxx.com)

When you deploy LinkAbet on your custom domain (e.g., `mysite.com`), here's what you need to know:

### 1. Current Configuration
- **Default Domain**: Currently set to `lab.et` in the code
- **Backend URL**: Uses environment variable `REACT_APP_BACKEND_URL`
- **Link Generation**: Creates links like `lab.et/abc123`

### 2. For Custom Domain Deployment

#### Option A: Use Your Main Domain (mysite.com)
- Links will be: `mysite.com/abc123`
- **Pros**: Simple, uses your main domain
- **Cons**: Shorter URLs, may conflict with your main site routes

#### Option B: Use Subdomain (go.mysite.com or links.mysite.com)
- Links will be: `go.mysite.com/abc123`
- **Pros**: Cleaner separation, professional look
- **Cons**: Requires subdomain setup

### 3. Required Changes for Deployment

#### Step 1: Update Environment Variables
```bash
# In /app/frontend/.env
REACT_APP_BACKEND_URL=https://mysite.com
# or
REACT_APP_BACKEND_URL=https://go.mysite.com
```

#### Step 2: Update Default Domain in Code
The application currently uses hardcoded "lab.et" in several places. You need to:

1. **Update HomePage Component** (lines ~197, 898):
   ```javascript
   // Change from:
   code className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
     {link.customDomain || 'lab.et'}/{link.shortUrl.split('/').pop()}
   
   // To:
   code className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
     {link.customDomain || 'mysite.com'}/{link.shortUrl.split('/').pop()}
   ```

2. **Update Link Creation Logic**:
   ```javascript
   // Change from:
   shortUrl: `lnk.ly/${Math.random().toString(36).substr(2, 6)}`
   
   // To:
   shortUrl: `mysite.com/${Math.random().toString(36).substr(2, 6)}`
   ```

#### Step 3: Backend URL Routing
Make sure your web server (nginx/Apache) routes:
- `mysite.com/api/*` → Backend (port 8001)
- `mysite.com/*` → Frontend (port 3000)

### 4. DNS Configuration

#### For Main Domain (mysite.com):
```
A Record: mysite.com → Your Server IP
```

#### For Subdomain (go.mysite.com):
```
CNAME Record: go.mysite.com → mysite.com
# or
A Record: go.mysite.com → Your Server IP
```

### 5. SSL Certificate
Ensure your SSL certificate covers:
- `mysite.com`
- `go.mysite.com` (if using subdomain)

### 6. Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name mysite.com go.mysite.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name mysite.com go.mysite.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Backend API routes
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Frontend routes
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. Automatic Link Generation
Yes! Once configured properly:
- ✅ Links will automatically generate with your domain: `mysite.com/abc123`
- ✅ No manual intervention needed for each link
- ✅ Custom domains per customer will also work (go.clientdomain.com)

### 8. Testing Your Setup
1. Update the domain configuration
2. Create a test link
3. Verify it generates: `mysite.com/xyz123` (not lab.et)
4. Test the short link redirects properly

### Next Steps
Would you like me to:
1. Update the code to use a configurable domain instead of hardcoded "lab.et"?
2. Create an admin settings page to manage default domain?
3. Help with the nginx/Apache configuration?