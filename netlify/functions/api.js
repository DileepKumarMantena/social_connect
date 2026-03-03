const express = require('express');
const serverless = require('serverless-http');
const cors = require('cors');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Mock data
const USERS = {
    "superadmin": {
        username: "superadmin",
        password: "SuperAdmin123!",
        name: "Super Admin",
        role: "super_admin",
        email: "superadmin@company.com"
    },
    "admin1": {
        username: "admin1", 
        password: "Admin123!",
        name: "Admin User",
        role: "admin",
        email: "admin1@company.com"
    },
    "user1": {
        username: "user1",
        password: "User123!",
        name: "Regular User", 
        role: "user",
        email: "user1@company.com"
    }
};

const CAMPAIGNS = [
    {id: 1, name: "Summer Sale", status: "active", leads: 45, conversion_rate: 12.5, created_by: "admin1"},
    {id: 2, name: "Product Launch", status: "completed", leads: 120, conversion_rate: 8.3, created_by: "admin1"},
    {id: 3, name: "Holiday Special", status: "draft", leads: 0, conversion_rate: 0, created_by: "superadmin"}
];

const CHANNELS = [
    {id: 1, name: "facebook", connected: true, active: true, followers: 1500, created_by: "admin1"},
    {id: 2, name: "instagram", connected: true, active: false, followers: 800, created_by: "admin1"},
    {id: 3, name: "linkedin", connected: false, active: false, followers: 0, created_by: "superadmin"},
    {id: 4, name: "twitter", connected: false, active: false, followers: 0, created_by: "admin1"},
    {id: 5, name: "youtube", connected: true, active: true, followers: 2500, created_by: "superadmin"}
];

const LEADS = [
    {id: 1, name: "John Doe", email: "john@example.com", status: "new", campaign_id: 1, created_by: "admin1"},
    {id: 2, name: "Jane Smith", email: "jane@example.com", status: "contacted", campaign_id: 1, created_by: "admin1"},
    {id: 3, name: "Bob Johnson", email: "bob@example.com", status: "converted", campaign_id: 2, created_by: "admin1"}
];

// API Routes
app.get('/api/v1/health', (req, res) => {
    res.json({
        status: "healthy", 
        database: "mock", 
        timestamp: new Date().toISOString(),
        platform: "netlify"
    });
});

app.get('/api/v1/channels', (req, res) => {
    res.json({success: true, channels: CHANNELS});
});

app.get('/api/v1/campaigns', (req, res) => {
    res.json({success: true, campaigns: CAMPAIGNS});
});

app.get('/api/v1/leads', (req, res) => {
    res.json({success: true, leads: LEADS});
});

app.get('/api/v1/dashboard/stats', (req, res) => {
    const connected_channels = CHANNELS.filter(ch => ch.connected).length;
    const active_campaigns = CAMPAIGNS.filter(ca => ca.status === "active").length;
    const total_leads = LEADS.length;
    
    res.json({
        success: true,
        stats: {
            connected_channels,
            active_campaigns,
            total_leads
        }
    });
});

app.post('/api/v1/login', (req, res) => {
    const {username, password} = req.body;
    
    if (USERS[username] && USERS[username].password === password) {
        const user = USERS[username];
        res.json({
            success: true,
            access_token: "mock_jwt_token_12345",
            user: {
                username: user.username,
                name: user.name,
                role: user.role,
                email: user.email
            }
        });
    } else {
        res.json({success: false, error: "Invalid credentials"});
    }
});

// Handle all other routes
app.use((req, res) => {
    res.status(404).json({error: "Endpoint not found"});
});

module.exports.handler = serverless(app);
