# Social Connect - Deployment Guide

This guide will help you deploy your Social Connect application to production so users can access it via a single URL like `https://yourapp.com`.

## Quick Start (Recommended for Beginners)

### Option 1: Render.com (Easiest) 🚀

1. **Prepare Your Code**
   ```bash
   # Make sure you're on the main branch
   git checkout main
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Sign up and connect your GitHub repository
   - Use the `render.yaml` file in your project
   - Render will automatically detect and deploy your app

3. **Environment Variables**
   - In Render dashboard, set your environment variables
   - Copy from `.env.example` and use secure values
   - Your app will be live at: `https://your-app-name.onrender.com`

**Cost:** $7-25/month  
**Time:** 15-30 minutes

---

## Option 2: Docker (Full Control) 🐳

### Local Development
```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 2. Deploy locally
./deploy.sh
# Choose option 1 for local deployment

# 3. Access your app
# Frontend: http://localhost
# Backend: http://localhost:8003
```

### Production Server
```bash
# 1. On your server (Ubuntu/Debian)
sudo apt update
sudo apt install docker.io docker-compose nginx certbot

# 2. Clone your repository
git clone https://github.com/yourusername/social_connect.git
cd social_connect

# 3. Setup environment
cp .env.example .env
nano .env  # Edit with your production values

# 4. Deploy
./deploy.sh
# Choose option 1 for local deployment (on server)

# 5. Setup SSL
./deploy.sh
# Choose option 5 to generate SSL certificate
```

**Cost:** $5-20/month (VPS)  
**Time:** 1-2 hours

---

## Option 3: DigitalOcean App Platform (Balanced) 🌊

1. **Create DigitalOcean Account**
   - Go to [digitalocean.com](https://digitalocean.com)
   - Create an account

2. **Create App**
   - Click "Create" → "Apps"
   - Connect your GitHub repository
   - Use the following build command:
     ```bash
     npm run build && cd backend && pip install -r requirements.txt
     ```
   - Run command: `python backend/extension.py`
   - Set environment variables from `.env.example`

3. **Deploy**
   - Click "Deploy" and wait for deployment
   - Your app will be live at the provided URL

**Cost:** $5-25/month  
**Time:** 30-45 minutes

---

## Configuration Files Explained

### `.env.example`
Template for environment variables. Copy to `.env` and fill with your values:
- Database credentials
- API keys
- Security secrets
- Domain configuration

### `Dockerfile`
Multi-stage build that:
1. Builds React frontend
2. Sets up Python backend
3. Combines both into one container

### `docker-compose.yml`
Orchestrates multiple services:
- MongoDB database
- Redis cache
- Backend API
- Nginx reverse proxy

### `nginx.conf`
Web server configuration:
- HTTPS/SSL setup
- API routing
- Security headers
- Rate limiting

### `deploy.sh`
Automated deployment script with options for:
- Local Docker deployment
- Multiple cloud providers
- SSL certificate generation
- Database backups

---

## Environment Variables

### Required for Production
```bash
# Database
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=your_secure_password
MONGODB_URL=mongodb://admin:password@host:27017/social_connect

# Security
JWT_SECRET_KEY=your_32_character_minimum_secret
CORS_ORIGINS=https://yourapp.com

# URLs
FRONTEND_URL=https://yourapp.com
BACKEND_URL=https://api.yourapp.com

# Mode
NODE_ENV=production
DEV_MODE=False
PRODUCTION_MODE=True
```

### Optional (Social Media APIs)
```bash
# Facebook/Instagram
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret

# WhatsApp
WHATSAPP_ACCESS_TOKEN=your_token

# LinkedIn
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

---

## Security Checklist

### Before Going Live
- [ ] Change all default passwords
- [ ] Set strong JWT secret key
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS correctly
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Backup strategy
- [ ] Monitoring setup

### SSL Certificate Setup
```bash
# Using Let's Encrypt (free)
sudo certbot certonly --standalone -d yourapp.com

# Or use the deployment script
./deploy.sh
# Choose option 5
```

---

## Monitoring and Maintenance

### Health Checks
- Frontend: `https://yourapp.com/health`
- Backend: `https://yourapp.com/api/v1/health`

### Logs
```bash
# View application logs
./deploy.sh
# Choose option 7

# Docker logs
docker-compose logs -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
```

### Backups
```bash
# Automated database backup
./deploy.sh
# Choose option 6

# Manual backup
docker exec mongodb mongodump --out /backup/$(date +%Y%m%d)
```

---

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find what's using port 8003
sudo lsof -i :8003
# Kill the process
sudo kill -9 <PID>
```

**Database Connection Failed**
```bash
# Check MongoDB status
docker-compose logs mongodb

# Restart database
docker-compose restart mongodb
```

**SSL Certificate Issues**
```bash
# Check certificate expiration
sudo certbot certificates

# Renew certificate
sudo certbot renew
```

**Frontend Not Loading**
```bash
# Check Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Getting Help

1. Check logs: `./deploy.sh` → option 7
2. Verify environment variables
3. Check firewall settings
4. Review documentation: [GitHub Issues](https://github.com/yourrepo/issues)

---

## Performance Optimization

### Database
- Create indexes for frequently queried fields
- Use connection pooling
- Enable query caching

### Frontend
- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading

### Backend
- Use Redis for caching
- Implement rate limiting
- Optimize API responses

---

## Scaling

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize database queries
- Enable caching

### Horizontal Scaling
- Load balancer setup
- Multiple app instances
- Database replication

---

## Cost Summary

| Platform | Monthly Cost | Setup Time | Difficulty |
|----------|--------------|-------------|------------|
| Render.com | $7-25 | 15-30 min | Easy |
| DigitalOcean | $5-20 | 1-2 hours | Medium |
| AWS | $10-50 | 2-4 hours | Hard |
| VPS + Docker | $5-15 | 1-2 hours | Medium |

**Recommendation:** Start with Render.com for easiest deployment, then migrate to VPS for more control as you grow.

---

## Next Steps

1. **Choose your deployment platform**
2. **Prepare your environment variables**
3. **Run the deployment script**
4. **Configure your domain**
5. **Set up SSL certificate**
6. **Test all functionality**
7. **Monitor performance**

Your Social Connect application will be available at a single URL where users can:
- Register and login
- Manage campaigns
- Connect social media
- View analytics
- Schedule posts
- Manage leads

All from one web application! 🎉
