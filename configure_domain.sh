#!/bin/bash

# LinkAbet Domain Configuration Script
# Run this script when deploying to your custom domain

echo "🚀 LinkAbet Domain Configuration Helper"
echo "======================================="

# Get the new domain from user input
read -p "Enter your domain name (e.g., mysite.com): " NEW_DOMAIN

if [ -z "$NEW_DOMAIN" ]; then
    echo "❌ No domain provided. Exiting."
    exit 1
fi

echo "📝 Updating domain configuration..."

# Update the domain config file
sed -i "s/DEFAULT_DOMAIN: 'lab.et'/DEFAULT_DOMAIN: '$NEW_DOMAIN'/" /app/frontend/src/config/domains.js
sed -i "s/SYSTEM_DOMAIN: 'linkabet.com'/SYSTEM_DOMAIN: '$NEW_DOMAIN'/" /app/frontend/src/config/domains.js

echo "✅ Domain configuration updated to: $NEW_DOMAIN"

# Update frontend environment variable if it exists
if [ -f "/app/frontend/.env" ]; then
    # Update existing REACT_APP_BACKEND_URL or add it
    if grep -q "REACT_APP_BACKEND_URL" /app/frontend/.env; then
        sed -i "s|REACT_APP_BACKEND_URL=.*|REACT_APP_BACKEND_URL=https://$NEW_DOMAIN|" /app/frontend/.env
    else
        echo "REACT_APP_BACKEND_URL=https://$NEW_DOMAIN" >> /app/frontend/.env
    fi
    echo "✅ Updated REACT_APP_BACKEND_URL to: https://$NEW_DOMAIN"
else
    echo "⚠️  Frontend .env file not found. You may need to create it manually:"
    echo "   echo 'REACT_APP_BACKEND_URL=https://$NEW_DOMAIN' > /app/frontend/.env"
fi

echo ""
echo "🎉 Configuration complete!"
echo ""
echo "📋 Next steps for deployment:"
echo "1. Update your DNS records:"
echo "   - A Record: $NEW_DOMAIN → Your Server IP"
echo "   - CNAME Record: *.subdomain.$NEW_DOMAIN → $NEW_DOMAIN (for subdomains)"
echo ""
echo "2. Configure your web server (nginx/Apache) to route:"
echo "   - $NEW_DOMAIN/api/* → Backend (port 8001)"
echo "   - $NEW_DOMAIN/* → Frontend (port 3000)"
echo ""
echo "3. Ensure SSL certificate covers $NEW_DOMAIN"
echo ""
echo "4. Restart the services:"
echo "   sudo supervisorctl restart all"
echo ""
echo "🔗 After deployment, your short links will be: $NEW_DOMAIN/abc123"