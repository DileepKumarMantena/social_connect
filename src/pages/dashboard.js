import React, { useEffect, useState } from "react";
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import {
    Toolbar,
    Typography,
    Box,
    Grid,
    Card,
    CardContent,
    Button,
    ThemeProvider,
    createTheme,
    CssBaseline,
    CircularProgress,
    alpha,
    Paper,
    Divider,
    Avatar,
    Chip,
    LinearProgress,
    Fade,
    Slide,
    Stack,
    IconButton,
    Tooltip,
} from "@mui/material";
import GroupsIcon from "@mui/icons-material/Groups";
import CampaignIcon from "@mui/icons-material/Campaign";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import InsightsIcon from "@mui/icons-material/Insights";
import AddIcon from "@mui/icons-material/Add";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import PeopleIcon from "@mui/icons-material/People";
import ConnectWithoutContactIcon from "@mui/icons-material/ConnectWithoutContact";
import DataUsageIcon from "@mui/icons-material/DataUsage";
import ChatBot from '../components/ChatBot/ChatBot';

// Mock data
const getChannels = ['facebook', 'instagram'];
const getCampaigns = ['digi'];
const getLeads = ['abcd'];

// Enhanced Blue Ocean Theme
const theme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#1e4b8c",
            light: "#2e7eb0",
            dark: "#0a2a4a",
            contrastText: "#ffffff",
        },
        secondary: {
            main: "#00b4d8",
            light: "#48cae4",
            dark: "#0096c7",
        },
        background: {
            default: "#f0f7ff",
            paper: "#ffffff",
            light: "#e3f2fd",
        },
        text: {
            primary: "#023047",
            secondary: "#2b5f8a",
        },
        ocean: {
            shallow: "#90e0ef",
            medium: "#00b4d8",
            deep: "#0077b6",
            abyss: "#023e8a",
        },
        success: {
            main: "#10b981",
            light: "#34d399",
            dark: "#059669",
        },
        warning: {
            main: "#f59e0b",
            light: "#fbbf24",
            dark: "#d97706",
        },
        error: {
            main: "#ef4444",
            light: "#f87171",
            dark: "#dc2626",
        },
    },
    typography: {
        fontFamily: '"nunito", "Roboto", "Helvetica", "Arial", sans-serif',
        h4: {
            fontWeight: 700,
            letterSpacing: "0.5px",
        },
        h5: {
            fontWeight: 600,
        },
        h6: {
            fontWeight: 600,
        },
    },
    shape: {
        borderRadius: 16,
    },
    components: {
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: 20,
                    boxShadow: "0 8px 32px rgba(0, 30, 60, 0.08)",
                    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    "&:hover": { 
                        transform: "translateY(-4px)",
                        boxShadow: "0 12px 48px rgba(0, 180, 216, 0.15)",
                    },
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 30,
                    textTransform: "none",
                    fontWeight: 600,
                    padding: "8px 20px",
                },
                contained: {
                    background: "linear-gradient(135deg, #1e4b8c 0%, #2e7eb0 100%)",
                    "&:hover": {
                        background: "linear-gradient(135deg, #0a2a4a 0%, #1e4b8c 100%)",
                    },
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    fontWeight: 500,
                },
            },
        },
    },
});

const Dashboard = ({ onNavigate }) => {
    const { user, token } = useAuth();
    const [stats, setStats] = useState({
        channels: 0,
        campaigns: 0,
        leads: 0,
    });
    const [loading, setLoading] = useState(true);
    const [hasFetched, setHasFetched] = useState(false);
    const [recentActivity, setRecentActivity] = useState([]);
    const [performanceData, setPerformanceData] = useState([]);

    // Get auth headers
    const getAuthHeaders = () => ({
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });

    // Fetch dashboard data
    useEffect(() => {
        if (!hasFetched && token) {
            const fetchStats = async () => {
                try {
                    setLoading(true);
                    
                    // Fetch stats
                    const statsResponse = await axios.get(
                        `${process.env.REACT_APP_API_LINKS}/api/v1/stats`,
                        getAuthHeaders()
                    );
                    const channelsResponse = await axios.get(
                        `${process.env.REACT_APP_API_LINKS}/api/v1/channels`,
                        getAuthHeaders()
                    );
                    const campaignsResponse = await axios.get(
                        `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns`,
                        getAuthHeaders()
                    );
                    const leadsResponse = await axios.get(
                        `${process.env.REACT_APP_API_LINKS}/api/v1/leads`,
                        getAuthHeaders()
                    );

                    const stats = statsResponse.data.stats || {};
                    const channels = channelsResponse.data.channels || [];
                    const campaigns = campaignsResponse.data.campaigns || [];
                    const leads = leadsResponse.data.leads || [];

                    setStats({
                        channels: stats.channels || 0,
                        campaigns: stats.campaigns || 0,
                        leads: stats.leads || 0,
                    });

                    // Mock recent activity
                    setRecentActivity([
                        { type: 'campaign', message: 'New campaign "Summer Sale" created', time: '2 hours ago', color: '#00b4d8' },
                        { type: 'lead', message: '15 new leads from Facebook', time: '4 hours ago', color: '#10b981' },
                        { type: 'channel', message: 'Instagram channel connected', time: '1 day ago', color: '#f59e0b' },
                    ]);

                    // Mock performance data
                    setPerformanceData([
                        { name: 'Mon', leads: 12, engagement: 85 },
                        { name: 'Tue', leads: 19, engagement: 92 },
                        { name: 'Wed', leads: 15, engagement: 78 },
                        { name: 'Thu', leads: 25, engagement: 95 },
                        { name: 'Fri', leads: 22, engagement: 88 },
                        { name: 'Sat', leads: 30, engagement: 96 },
                        { name: 'Sun', leads: 28, engagement: 90 },
                    ]);

                    setHasFetched(true);
                } catch (error) {
                    console.error('Error fetching dashboard data:', error);
                    // Fallback to mock data
                    setStats({
                        channels: 3,
                        campaigns: 5,
                        leads: 142,
                    });
                    setRecentActivity([
                        { type: 'campaign', message: 'New campaign "Summer Sale" created', time: '2 hours ago', color: '#00b4d8' },
                        { type: 'lead', message: '15 new leads from Facebook', time: '4 hours ago', color: '#10b981' },
                        { type: 'channel', message: 'Instagram channel connected', time: '1 day ago', color: '#f59e0b' },
                    ]);
                    setPerformanceData([
                        { name: 'Mon', leads: 12, engagement: 85 },
                        { name: 'Tue', leads: 19, engagement: 92 },
                        { name: 'Wed', leads: 15, engagement: 78 },
                        { name: 'Thu', leads: 25, engagement: 95 },
                        { name: 'Fri', leads: 22, engagement: 88 },
                        { name: 'Sat', leads: 30, engagement: 96 },
                        { name: 'Sun', leads: 28, engagement: 90 },
                    ]);
                    setHasFetched(true);
                } finally {
                    setLoading(false);
                }
            };

            fetchStats();
        }
    }, [hasFetched, token]);

    // Check if data is empty
    const hasData = stats.channels > 0 || stats.campaigns > 0 || stats.leads > 0;

    // Calculate percentages
    const channelUsage = stats.channels > 0 ? (stats.channels / 10) * 100 : 0;
    const campaignActive = stats.campaigns > 0 ? (stats.campaigns / 8) * 100 : 0;
    const leadGrowth = stats.leads > 0 ? (stats.leads / 200) * 100 : 0;

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />

            <Box sx={{ 
                p: { xs: 2, sm: 3, md: 4 },
                minHeight: "100vh",
                background: `linear-gradient(135deg, ${theme.palette.background.default} 0%, #e3f2fd 100%)`,
            }}>
                {/* Welcome Header */}
                <Fade in timeout={800}>
                    <Box sx={{ 
                        display: "flex", 
                        alignItems: "center", 
                        justifyContent: "space-between",
                        mb: 4,
                        flexWrap: "wrap",
                        gap: 2,
                    }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 3 }}>
                            <Avatar sx={{ 
                                width: 64, 
                                height: 64,
                                background: "linear-gradient(135deg, #1e4b8c 0%, #00b4d8 100%)",
                                fontSize: 24,
                                fontWeight: 700,
                            }}>
                                {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
                            </Avatar>
                            <Box>
                                <Typography variant="h4" sx={{ 
                                    background: "linear-gradient(135deg, #1e4b8c 0%, #00b4d8 100%)",
                                    WebkitBackgroundClip: "text",
                                    WebkitTextFillColor: "transparent",
                                    mb: 0.5,
                                }}>
                                    Welcome back, {user?.username ? user.username.charAt(0).toUpperCase() + user.username.slice(1) : "User"}!
                                </Typography>
                                <Typography variant="body1" color="text.secondary">
                                    Here's what's happening with your social presence today
                                </Typography>
                            </Box>
                        </Box>
                        
                        <Button 
                            variant="contained" 
                            startIcon={<AddIcon />}
                            onClick={() => onNavigate?.("campaigns")}
                            sx={{
                                background: "linear-gradient(135deg, #1e4b8c 0%, #00b4d8 100%)",
                                color: "white",
                                px: 3,
                                py: 1.5,
                                fontWeight: 600,
                                boxShadow: "0 4px 16px rgba(0, 180, 216, 0.3)",
                                "&:hover": {
                                    boxShadow: "0 6px 24px rgba(0, 180, 216, 0.4)",
                                },
                            }}
                        >
                            New Campaign
                        </Button>
                    </Box>
                </Fade>

                {/* Enhanced Stats Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { 
                            label: "Channels Connected", 
                            value: stats.channels, 
                            icon: <ConnectWithoutContactIcon />,
                            color: "#00b4d8",
                            bgColor: alpha("#00b4d8", 0.1),
                            progress: channelUsage,
                            trend: "+12%",
                        },
                        { 
                            label: "Active Campaigns", 
                            value: stats.campaigns, 
                            icon: <CampaignIcon />,
                            color: "#0077b6",
                            bgColor: alpha("#0077b6", 0.1),
                            progress: campaignActive,
                            trend: "+8%",
                        },
                        { 
                            label: "Total Leads", 
                            value: stats.leads, 
                            icon: <PeopleIcon />,
                            color: "#023e8a",
                            bgColor: alpha("#023e8a", 0.1),
                            progress: leadGrowth,
                            trend: "+25%",
                        },
                    ].map((item, index) => (
                        <Grid item xs={12} sm={6} md={4} key={index}>
                            <Slide in timeout={600 + index * 100} direction="up">
                                <Card sx={{ 
                                    height: "100%",
                                    background: `linear-gradient(135deg, ${item.bgColor} 0%, #ffffff 100%)`,
                                    border: `1px solid ${alpha(item.color, 0.2)}`,
                                    position: "relative",
                                    overflow: "hidden",
                                }}>
                                    <Box sx={{
                                        position: "absolute",
                                        top: -20,
                                        right: -20,
                                        width: 100,
                                        height: 100,
                                        borderRadius: "50%",
                                        background: alpha(item.color, 0.05),
                                    }} />
                                    <CardContent sx={{ position: "relative", zIndex: 1 }}>
                                        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                                            <Avatar sx={{ 
                                                bgcolor: alpha(item.color, 0.2),
                                                width: 56,
                                                height: 56,
                                            }}>
                                                {React.cloneElement(item.icon, { sx: { color: item.color, fontSize: 28 } })}
                                            </Avatar>
                                            <Chip 
                                                label={item.trend}
                                                size="small"
                                                sx={{
                                                    background: alpha("#10b981", 0.1),
                                                    color: "#10b981",
                                                    fontWeight: 600,
                                                }}
                                            />
                                        </Box>
                                        <Typography variant="h3" sx={{ 
                                            color: item.color,
                                            fontWeight: 700,
                                            mb: 1,
                                        }}>
                                            {loading ? <CircularProgress size={40} sx={{ color: item.color }} /> : item.value}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500, mb: 2 }}>
                                            {item.label}
                                        </Typography>
                                        <Box sx={{ width: "100%" }}>
                                            <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Usage
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    {Math.round(item.progress)}%
                                                </Typography>
                                            </Box>
                                            <LinearProgress 
                                                variant="determinate" 
                                                value={item.progress}
                                                sx={{
                                                    height: 6,
                                                    borderRadius: 3,
                                                    background: alpha(item.color, 0.1),
                                                    "& .MuiLinearProgress-bar": {
                                                        background: item.color,
                                                        borderRadius: 3,
                                                    },
                                                }}
                                            />
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Slide>
                        </Grid>
                    ))}
                </Grid>

                {/* Quick Tips Section - Always visible */}
                <Paper sx={{ mt: 4, p: 3, bgcolor: alpha(theme.palette.primary.main, 0.03) }}>
                    <Typography variant="h6" gutterBottom sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <TrendingUpIcon sx={{ color: theme.palette.primary.main }} />
                        Quick Tips
                    </Typography>
                    <Grid container spacing={2}>
                        {[
                            "Connect at least 3 channels to maximize reach",
                            "Schedule posts during peak engagement hours",
                            "Use A/B testing for better campaign performance",
                            "Follow up with leads within 24 hours",
                        ].map((tip, index) => (
                            <Grid item xs={12} sm={6} key={index}>
                                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                    <Avatar sx={{ width: 24, height: 24, bgcolor: alpha(theme.palette.primary.main, 0.2), fontSize: "0.8rem" }}>
                                        {index + 1}
                                    </Avatar>
                                    <Typography variant="body2" color="text.secondary">
                                        {tip}
                                    </Typography>
                                </Box>
                            </Grid>
                        ))}
                    </Grid>
                </Paper>
            </Box>
            
            {/* ChatBot Integration */}
            <ChatBot onNavigate={onNavigate} />
        </ThemeProvider>
    );
};

export default Dashboard;