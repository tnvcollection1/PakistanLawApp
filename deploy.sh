#!/bin/bash
# deploy.sh — Deploy to VPS

set -e

echo "Starting deployment..."

# Build frontend
cd /var/www/pakistanlawapp/frontend
yarn install
yarn build

# Copy build to nginx
cp -r build/* /var/www/html/

# Restart backend
cd /var/www/pakistanlawapp
pm2 restart pakistanlawapp-backend || pm2 start server.py --name pakistanlawapp-backend --interpreter python3

echo "Deployment complete!"
