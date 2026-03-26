# Social Media Integration System

Your Social Connect application now supports real social media integrations with automatic fallback to mock data. This system allows you to seamlessly switch between real social media APIs and mock data for development.

## 🚀 Features

### ✅ Implemented
- **Twitter/X Integration** - Full API support with OAuth authentication
- **Automatic Fallback** - Falls back to mock data if APIs are unavailable
- **Connection Health Monitoring** - Background health checks and reconnection logic
- **Unified Service Layer** - Single interface for all social platforms
- **Role-based Data Filtering** - Maintains existing security model
- **Real-time Status Tracking** - Monitor connection status and health

### 🔄 How It Works

The system uses a **3-tier fallback approach**:

1. **Real Social Media APIs** (when configured and connected)
2. **Existing Database/Mock System** (your current DEV_MODE setup)  
3. **Built-in Mock Data** (ultimate fallback)

## 📋 Quick Setup Guide

### 1. Environment Configuration

Copy the example environment file:
```bash
cp .env.example .env
```

### 2. Twitter Setup (Easiest - Start Here)

1. **Get Twitter API Credentials**:
   - Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
   - Create a new app
   - Get: API Key, API Secret, Access Token, Access Token Secret

2. **Configure Environment**:
   ```bash
   # In your .env file
   SOCIAL_INTEGRATION_ENABLED=true
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
   ```

3. **Restart Server**:
   ```bash
   python extension.py
   ```

### 3. Test Integration

Check your social media status:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8003/api/v1/social/status
```

## 🎛️ API Endpoints

### Social Media Management
- `GET /api/v1/social/status` - Overall integration status
- `GET /api/v1/social/platforms` - Supported platforms status
- `POST /api/v1/social/test-connection/{platform}` - Test platform connection
- `POST /api/v1/social/post` - Post content to social media
- `GET /api/v1/social/data-source` - Current data source information

### Enhanced Existing Endpoints
Your existing endpoints now automatically use real data when available:
- `GET /api/v1/channels` - Shows connected social media channels
- `GET /api/v1/campaigns` - Real campaign data from platforms
- `GET /api/v1/leads` - Leads generated from social media

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SOCIAL_INTEGRATION_ENABLED` | Enable real social media APIs | `false` |
| `TWITTER_API_KEY` | Twitter API Key | Required |
| `TWITTER_API_SECRET` | Twitter API Secret | Required |
| `TWITTER_ACCESS_TOKEN` | Twitter Access Token | Required |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter Access Token Secret | Required |

### Switching Between Data Sources

**Option 1: Environment Toggle**
```bash
# Use real social media APIs
SOCIAL_INTEGRATION_ENABLED=true

# Use only mock data
SOCIAL_INTEGRATION_ENABLED=false
```

**Option 2: Automatic Fallback**
The system automatically falls back to mock data if:
- API credentials are missing
- Social media platforms are down
- Rate limits are exceeded
- Network issues occur

## 📊 Data Flow

```
User Request → Social Data Service → [Real API if available] → Response
                    ↓
                [Fallback to DEV_MODE/MongoDB] 
                    ↓
                [Fallback to Mock Data]
```

## 🔍 Monitoring & Health Checks

The system includes automatic health monitoring:

- **Connection Testing**: Tests API connections every 5 minutes
- **Rate Limit Tracking**: Monitors API rate limits
- **Error Recovery**: Automatic reconnection attempts
- **Status Updates**: Real-time connection status

### Health Check Response
```json
{
  "social_integration_enabled": true,
  "real_data_available": true,
  "enabled_platforms": ["twitter"],
  "platform_status": {
    "twitter": {
      "configured": true,
      "status": "connected",
      "connected": true
    }
  }
}
```

## 🛡️ Security & Permissions

- **Role-based Access**: Maintains your existing user role system
- **Token Authentication**: Uses your existing JWT authentication
- **Credential Security**: API keys stored in environment variables
- **Permission-based Features**: Platform features controlled by user permissions

## 🚦 Troubleshooting

### Common Issues

**1. Social integration not working**
```bash
# Check if enabled
curl http://localhost:8003/api/v1/social/data-source

# Expected: "social_integration_enabled": true
```

**2. Twitter connection failed**
```bash
# Test connection
curl -X POST http://localhost:8003/api/v1/social/test-connection/twitter

# Check credentials in .env file
```

**3. Still seeing mock data**
- Verify `SOCIAL_INTEGRATION_ENABLED=true`
- Check API credentials are correct
- Ensure social platform is configured

**4. Rate limit errors**
- System automatically handles rate limits
- Check connection status for reset time
- Wait for automatic retry

### Debug Mode

Enable detailed logging:
```python
# In constants.py
DEV_MODE = True  # Shows more detailed logs
```

## 📁 File Structure

```
backend/
├── social_media/              # 🆕 Dedicated social media module
│   ├── __init__.py           # Module exports
│   ├── social_config.py      # Platform configuration & management
│   ├── twitter_service.py   # Twitter API integration
│   ├── twitter_oauth.py     # Real Twitter OAuth 2.0 implementation
│   ├── connection_manager.py # Health checks & reconnection
│   ├── oauth_manager.py     # OAuth flow management
│   ├── user_credentials.py  # Per-user credential storage
│   ├── social_data_service.py # Unified service layer
│   ├── SOCIAL_MEDIA_INTEGRATION.md # This documentation
│   ├── REAL_TWITTER_INTEGRATION.md # Real Twitter setup guide
│   └── ...
├── services/
│   ├── routes.py             # Updated with social media endpoints
│   └── extension.py          # Updated with social media initialization
├── .env.example              # Environment variables template
├── social_media_requirements.txt # Dependencies file
└── constants.py              # Updated with MongoDB URL
```

## 🔄 Adding New Platforms

The system is designed for easy expansion:

1. **Create Platform Service** (add to `social_media/`)
2. **Add Platform Config** (in `social_config.py`)
3. **Implement Health Check** (in `connection_manager.py`)
4. **Add to Unified Service** (in `social_data_service.py`)

## 📈 Next Steps

### Planned Features
- **LinkedIn Integration** - Professional networking and lead generation
- **Facebook Integration** - Business pages and ad management  
- **Instagram Integration** - Visual content and stories
- **Analytics Dashboard** - Cross-platform analytics
- **Scheduled Posting** - Advanced scheduling features
- **Social Listening** - Monitor brand mentions and engagement

### Current Limitations
- Twitter only (other platforms coming soon)
- Basic posting functionality
- Mock data for campaigns and analytics
- No real-time webhooks yet

## 🎯 Usage Examples

### Post to Twitter
```bash
curl -X POST http://localhost:8003/api/v1/social/post \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Hello from Social Connect! 🚀",
       "platform": "twitter"
     }'
```

### Check Channel Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8003/api/v1/channels
```

Expected response shows connected Twitter account with real follower count:
```json
{
  "channels": [
    {
      "id": "twitter_123456789",
      "name": "Twitter/X - @yourusername",
      "platform": "twitter", 
      "connected": true,
      "active": true,
      "followers": 1250,
      "username": "yourusername",
      "status": "connected"
    }
  ]
}
```

## 📞 Support

If you encounter issues:

1. Check the server logs for detailed error messages
2. Verify your API credentials are correct
3. Ensure social media platform apps are properly configured
4. Test with `SOCIAL_INTEGRATION_ENABLED=false` to isolate issues

---

**Ready to connect your social media accounts? Start with Twitter - it's the easiest to set up and provides immediate value!**
