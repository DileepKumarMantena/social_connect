# Real Twitter Integration Setup Guide

Your Social Connect application now supports **real Twitter API v2 integration** with OAuth 2.0 authentication! This guide will help you set up and use the real Twitter integration.

## 🚀 **What's Now Available**

### ✅ **Real Twitter Features**
- **OAuth 2.0 with PKCE** - Secure authentication flow
- **Real Twitter API v2** - Access to actual Twitter data
- **Multi-user support** - Each user connects their own account
- **Real posting** - Post actual tweets to Twitter
- **Live metrics** - Real follower counts, engagement data
- **Rate limiting** - Proper Twitter API rate limit handling
- **Automatic fallback** - Falls back to mock data if APIs fail

### 🔄 **SOCIAL_INTEGRATION_ENABLED Toggle**
```bash
# Mock mode (development)
SOCIAL_INTEGRATION_ENABLED=false
# Uses mock data, no API calls

# Real mode (production)  
SOCIAL_INTEGRATION_ENABLED=true
# Uses real Twitter API with OAuth
```

## 📋 **Setup Requirements**

### **1. Twitter Developer Account**
1. **Apply for Twitter Developer Access**
   - Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
   - Sign up with your Twitter account
   - Apply for developer access (may take 1-3 days for approval)

### **2. Create Twitter App**
1. **Create New Project & App**
   ```
   Project Name: "Social Connect Integration"
   App Name: "Social Connect App"
   Use Case: "Automated app or bot"
   ```

2. **App Permissions Required**
   - ✅ **Read** - Read user data and tweets
   - ✅ **Write** - Post tweets and manage account
   - ✅ **Offline Access** - Refresh tokens for long-term access

### **3. Get App Credentials**
From your Twitter App settings, get:
- **API Key** (Client ID)
- **API Secret** (Client Secret)
- **Bearer Token** (for app-only requests)
- **Access Token** (for user-specific requests)
- **Access Token Secret** (for user-specific requests)

## ⚙️ **Configuration Setup**

### **1. Update .env file**
```bash
# Copy the template
cp backend/.env.example backend/.env

# Edit your .env file
# Enable real social media integration
SOCIAL_INTEGRATION_ENABLED=true

# Twitter API v2 Credentials
TWITTER_API_KEY=your_actual_api_key_here
TWITTER_API_SECRET=your_actual_api_secret_here
TWITTER_ACCESS_TOKEN=your_actual_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_actual_token_secret_here
TWITTER_REDIRECT_URI=http://localhost:3001/social/twitter/callback
```

### **2. Install Dependencies**
```bash
cd backend
pip install -r social_media_requirements.txt
```

### **3. Configure Twitter App Callback URL**
In your Twitter Developer Portal:
1. Go to your App settings
2. Add **Callback URL**: `http://localhost:3001/social/twitter/callback`
3. Enable **OAuth 2.0**
4. Set app permissions to **Read + Write**

## 🔐 **OAuth 2.0 Flow**

### **Step 1: Get Authorization URL**
```bash
POST /api/v1/social/oauth-url/twitter
{
  "callback_url": "http://localhost:3001/social/twitter/callback"
}

Response:
{
  "success": true,
  "data": {
    "authorization_url": "https://twitter.com/i/oauth2/authorize?response_type=code&client_id=...",
    "state": "abc123...",
    "expires_in": 600
  }
}
```

### **Step 2: User Authorizes**
1. User is redirected to Twitter authorization URL
2. User logs in to Twitter (if not already)
3. User grants permissions to your app
4. Twitter redirects back to your callback URL

### **Step 3: Handle Callback**
```bash
POST /api/v1/social/oauth-callback/twitter
{
  "code": "authorization_code_from_twitter",
  "state": "abc123...",
  "callback_url": "http://localhost:3001/social/twitter/callback"
}

Response:
{
  "success": true,
  "data": {
    "platform": "twitter",
    "connected_account": "your_twitter_handle",
    "user_id": "123456789",
    "name": "Your Name",
    "verified": true,
    "followers": 1250,
    "profile_image": "https://..."
  }
}
```

## 🎯 **Using Real Twitter Features**

### **Get User's Twitter Info**
```bash
GET /api/v1/social/connections

Response:
{
  "success": true,
  "data": {
    "username": "admin1",
    "connections": [
      {
        "platform": "twitter",
        "username": "your_twitter_handle",
        "user_id": "123456789",
        "verified": true,
        "followers": 1250,
        "connected_at": "2024-01-15T10:30:00.000Z",
        "status": "connected"
      }
    ]
  }
}
```

### **Get Real Channel Data**
```bash
GET /api/v1/channels

Response:
{
  "success": true,
  "channels": [
    {
      "id": "twitter_123456789_admin1",
      "name": "Twitter/X - @your_twitter_handle",
      "platform": "twitter",
      "connected": true,
      "followers": 1250,
      "username": "your_twitter_handle",
      "profile_image": "https://pbs.twimg.com/profile_images/...",
      "created_by": "admin1",
      "status": "connected"
    }
  ]
}
```

### **Post Real Tweet**
```bash
POST /api/v1/social/post
{
  "content": "Hello from Social Connect! 🚀 #TwitterAPI",
  "platform": "twitter"
}

Response:
{
  "success": true,
  "data": {
    "post_id": "1234567890123456789",
    "platform": "twitter",
    "content": "Hello from Social Connect! 🚀 #TwitterAPI",
    "posted_at": "2024-01-15T11:00:00.000Z",
    "url": "https://twitter.com/your_handle/status/1234567890123456789"
  }
}
```

## 🛡️ **Security Features**

### **OAuth 2.0 with PKCE**
- **Proof Key for Code Exchange** - Prevents authorization code interception
- **State Validation** - Prevents CSRF attacks
- **Secure Token Storage** - Tokens encrypted in database
- **Automatic Token Refresh** - Maintains long-term access

### **Rate Limiting**
- **Twitter API v2 Rate Limits** - Properly handles 15-minute windows
- **Automatic Backoff** - Waits when rate limited
- **Request Tracking** - Monitors API usage per user
- **Error Handling** - Graceful degradation when limits hit

### **Data Isolation**
- **Per-user Credentials** - Each user's tokens stored separately
- **Encryption** - All sensitive data encrypted at rest
- **Access Control** - Users can only access their own data
- **Audit Logging** - All Twitter API calls logged

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. "Twitter platform not enabled"**
```bash
# Check your configuration
GET /api/v1/social/status

# Solution: Add Twitter credentials to .env
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
# Set SOCIAL_INTEGRATION_ENABLED=true
```

#### **2. "Invalid or expired credentials"**
```bash
# Check user connection
GET /api/v1/social/connections

# Solution: User needs to reconnect their account
DELETE /api/v1/social/disconnect/twitter
POST /api/v1/social/connect/twitter
```

#### **3. "Rate limit exceeded"**
```bash
# Wait for rate limit reset (usually 15 minutes)
# System automatically handles this with backoff

# Check rate limit status
GET /api/v1/social/status
```

#### **4. "OAuth session expired"**
```bash
# OAuth sessions expire after 10 minutes
# User needs to restart the OAuth flow

# Solution: Start new OAuth flow
POST /api/v1/social/oauth-url/twitter
```

### **Debug Mode**
```bash
# Enable detailed logging
# In constants.py
DEV_MODE = True

# Check server logs for detailed error messages
tail -f backend/logs/social_connect_$(date +%Y-%m-%d).log
```

## 📊 **API Rate Limits**

### **Twitter API v2 Limits**
- **User Lookup**: 300 requests per 15 minutes
- **Tweet Posting**: 300 requests per 15 minutes  
- **User Timeline**: 300 requests per 15 minutes
- **Tweet Metrics**: 300 requests per 15 minutes

### **Best Practices**
- **Cache user data** - Don't fetch user info repeatedly
- **Batch requests** - Use expansions when possible
- **Monitor usage** - Track API calls per user
- **Handle limits gracefully** - Provide user feedback

## 🎯 **Production Deployment**

### **Environment Variables**
```bash
# Production .env
SOCIAL_INTEGRATION_ENABLED=true
TWITTER_API_KEY=prod_api_key
TWITTER_API_SECRET=prod_api_secret
TWITTER_ACCESS_TOKEN=prod_access_token
TWITTER_ACCESS_TOKEN_SECRET=prod_token_secret
TWITTER_REDIRECT_URI=https://yourdomain.com/social/twitter/callback
```

### **Security Considerations**
- **HTTPS Required** - Use HTTPS for all OAuth callbacks
- **Environment Variables** - Never commit credentials to git
- **Database Encryption** - Ensure database encryption at rest
- **Monitoring** - Monitor API usage and errors

### **Scaling**
- **Connection Pooling** - Reuse HTTP connections
- **Caching** - Cache user data and metrics
- **Background Tasks** - Handle rate limit resets in background
- **Load Balancing** - Distribute API calls across instances

## 🔄 **Testing**

### **Mock Mode Testing**
```bash
# Test with mock data first
SOCIAL_INTEGRATION_ENABLED=false

# Test multi-user mock flow
# Each user gets different mock accounts
```

### **Real API Testing**
```bash
# Test with real Twitter API
SOCIAL_INTEGRATION_ENABLED=true

# Use Twitter's sandbox environment first
# Test with a test Twitter account
```

### **Integration Tests**
```bash
# Test complete OAuth flow
# Test real posting
# Test rate limiting
# Test error handling
# Test multi-user isolation
```

---

**🎉 Your Social Connect application now supports real Twitter integration with enterprise-grade security and multi-user support!**

**Next Steps:**
1. Get Twitter Developer access
2. Create your Twitter app
3. Configure credentials in .env
4. Test the OAuth flow
5. Start connecting real Twitter accounts!
