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
} from "@mui/material";
import GroupsIcon from "@mui/icons-material/Groups";
import CampaignIcon from "@mui/icons-material/Campaign";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import InsightsIcon from "@mui/icons-material/Insights";
import WavesIcon from "@mui/icons-material/Waves";
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

// Blue Ocean Theme (matching AppLayout)
const theme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#1e4b8c", // Deep ocean blue
            light: "#2e7eb0", // Lighter ocean blue
            dark: "#0a2a4a", // Deep sea blue
            contrastText: "#ffffff",
        },
        secondary: {
            main: "#00b4d8", // Tropical ocean blue
            light: "#48cae4",
            dark: "#0096c7",
        },
        background: {
            default: "#f0f7ff", // Light ocean mist
            paper: "#ffffff",
            light: "#e3f2fd", // Very light ocean breeze
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

const SECTIONS = [
    {
        id: "channels",
        label: "Channels",
        desc: "Connect Facebook, Instagram, LinkedIn & more",
        icon: <GroupsIcon fontSize="large" />,
        color: "#00b4d8",
        emptyState: "No channels connected yet",
        emptyAction: "Connect Channel",
    },
    {
        id: "campaigns",
        label: "Campaigns",
        desc: "Create and manage campaigns",
        icon: <CampaignIcon fontSize="large" />,
        color: "#0077b6",
        emptyState: "No active campaigns",
        emptyAction: "Create Campaign",
    },
    {
        id: "leads",
        label: "Leads",
        desc: "Track and follow up on leads",
        icon: <AccountTreeIcon fontSize="large" />,
        color: "#023e8a",
        emptyState: "No leads yet",
        emptyAction: "Import Leads",
    },
    {
        id: "rolemanagement",
        label: "Role Management",
        desc: "Manage user roles and permissions",
        icon: <AdminPanelSettingsIcon fontSize="large" />,
        color: "#2e7eb0",
        emptyState: "No roles configured",
        emptyAction: "Add Role",
    },
];

export default function Dashboard({ onNavigate }) {
    const { user, token, getAuthHeaders } = useAuth();
    const [stats, setStats] = useState({ channels: 0, campaigns: 0, leads: 0 });
    const [loading, setLoading] = useState(true);
    const [hasFetched, setHasFetched] = useState(false);

    useEffect(() => {
        if (hasFetched) return; // Prevent multiple calls
        
        const fetchStats = async () => {
            try {
                // Fetch real data from APIs
                const authHeaders = getAuthHeaders();
                
                const [statsResponse, channelsResponse, campaignsResponse, leadsResponse] = await Promise.all([
                    axios.get(`${process.env.REACT_APP_API_LINKS}/api/v1/dashboard/stats`, { 
                        withCredentials: true,
                        headers: authHeaders
                    }),
                    axios.get(`${process.env.REACT_APP_API_LINKS}/api/v1/channels`, { 
                        withCredentials: true,
                        headers: authHeaders
                    }),
                    axios.get(`${process.env.REACT_APP_API_LINKS}/api/v1/campaigns`, { 
                        withCredentials: true,
                        headers: authHeaders
                    }),
                    axios.get(`${process.env.REACT_APP_API_LINKS}/api/v1/leads`, { 
                        withCredentials: true,
                        headers: authHeaders
                    })
                ]);

                const stats = statsResponse.data.stats || {};
                // eslint-disable-next-line no-unused-vars
                const channels = channelsResponse.data.channels || [];
                // eslint-disable-next-line no-unused-vars
                const campaigns = campaignsResponse.data.campaigns || [];
                // eslint-disable-next-line no-unused-vars
                const leads = leadsResponse.data.leads || [];

                setStats({
                    channels: stats.channels || 0,
                    campaigns: stats.campaigns || 0,
                    leads: stats.leads || 0,
                });
                setHasFetched(true); // Mark as fetched
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
                // Fallback to mock data if API fails
                const [channels, campaigns, leads] = await Promise.all([
                    Promise.resolve(getChannels),
                    Promise.resolve(getCampaigns),
                    Promise.resolve(getLeads),
                ]);

                const connectedChannels = (channels || []).filter(
                    (c) => c.connected || c.active
                ).length;

                setStats({
                    channels: connectedChannels,
                    campaigns: (campaigns || []).length,
                    leads: (leads || []).length,
                });
                setHasFetched(true); // Mark as fetched
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, [hasFetched]); // Only depend on hasFetched, not token

    // Check if data is empty
    const hasData = stats.channels > 0 || stats.campaigns > 0 || stats.leads > 0;

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />

            <Box sx={{ 
                p: { xs: 2, sm: 3, md: 4 },
                minHeight: "100vh",
                background: theme.palette.background.default,
            }}>
                {/* Welcome Header with Wave Icon */}
                <Box sx={{ 
                    display: "flex", 
                    alignItems: "center", 
                    justifyContent: "space-between",
                    mb: 4,
                    flexWrap: "wrap",
                    gap: 2,
                }}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                      
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
                    >
                        New Campaign
                    </Button>
                </Box>

                {/* Stats Section with Ocean-themed Cards */}
                <Grid container spacing={3} mb={4}>
                    {[
                        { 
                            label: "Channels Connected", 
                            value: stats.channels, 
                            icon: <ConnectWithoutContactIcon />,
                            color: "#00b4d8",
                            bgColor: alpha("#00b4d8", 0.1),
                        },
                        { 
                            label: "Active Campaigns", 
                            value: stats.campaigns, 
                            icon: <CampaignIcon />,
                            color: "#0077b6",
                            bgColor: alpha("#0077b6", 0.1),
                        },
                        { 
                            label: "Total Leads", 
                            value: stats.leads, 
                            icon: <PeopleIcon />,
                            color: "#023e8a",
                            bgColor: alpha("#023e8a", 0.1),
                        },
                    ].map((item, index) => (
                        <Grid item xs={12} sm={6} md={6} key={index}>
                            <Card sx={{ 
                                background: `linear-gradient(135deg, ${item.bgColor} 0%, #ffffff 100%)`,
                                border: `1px solid ${alpha(item.color, 0.2)}`,
                            }}>
                                <CardContent>
                                    <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                                        <Box>
                                            <Typography variant="h3" sx={{ 
                                                color: item.color,
                                                fontWeight: 700,
                                                mb: 1,
                                            }}>
                                                {loading ? <CircularProgress size={40} sx={{ color: item.color }} /> : item.value}
                                            </Typography>
                                            <Typography variant="body1" color="text.secondary" sx={{ fontWeight: 500 }}>
                                                {item.label}
                                            </Typography>
                                        </Box>
                                        <Avatar sx={{ 
                                            bgcolor: alpha(item.color, 0.2),
                                            width: 56,
                                            height: 56,
                                        }}>
                                            {React.cloneElement(item.icon, { sx: { color: item.color, fontSize: 28 } })}
                                        </Avatar>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>

                {/* Blank State / Empty Data Section */}
                {!hasData && !loading && (
                    <Paper 
                        sx={{ 
                            p: 4, 
                            mb: 4, 
                            textAlign: "center",
                            background: "linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%)",
                            border: `2px dashed ${alpha(theme.palette.primary.main, 0.2)}`,
                        }}
                    >
                        <Avatar
                            sx={{
                                bgcolor: alpha(theme.palette.primary.main, 0.1),
                                width: 80,
                                height: 80,
                                mx: "auto",
                                mb: 2,
                            }}
                        >
                            <DataUsageIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />
                        </Avatar>
                        <Typography variant="h5" gutterBottom sx={{ color: theme.palette.primary.main }}>
                            Get Started with SocialConnect
                        </Typography>
                        <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: "auto" }}>
                            Connect your first channel to start managing your social media presence, 
                            create campaigns, and track leads all in one place.
                        </Typography>
                        <Box sx={{ display: "flex", gap: 2, justifyContent: "center", flexWrap: "wrap" }}>
                            <Button 
                                variant="contained" 
                                size="large"
                                startIcon={<GroupsIcon />}
                                onClick={() => onNavigate?.("channels")}
                            >
                                Connect Channel
                            </Button>
                            <Button 
                                variant="outlined" 
                                size="large"
                                startIcon={<InsightsIcon />}
                                sx={{ borderColor: theme.palette.primary.main, color: theme.palette.primary.main }}
                            >
                                Watch Tutorial
                            </Button>
                        </Box>
                    </Paper>
                )}

                {/* Analytics Preview Card - Always visible but with blank state styling */}
                <Card sx={{ mb: 4 }}>
                    <CardContent>
                        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <InsightsIcon sx={{ color: theme.palette.primary.main }} />
                                <Typography variant="h6">
                                    Campaign Performance
                                </Typography>
                            </Box>
                            {!hasData && (
                                <Chip 
                                    label="No Data Available" 
                                    size="small"
                                    sx={{ bgcolor: alpha(theme.palette.warning?.main || "#ff9800", 0.1), color: "#b26a00" }}
                                />
                            )}
                        </Box>
                        
                        {/* Chart Placeholder with blank state styling */}
                        <Paper
                            sx={{
                                height: 200,
                                width: "100%",
                                background: "linear-gradient(180deg, #e3f2fd 0%, #ffffff 100%)",
                                borderRadius: 4,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                flexDirection: "column",
                                gap: 2,
                                border: `2px dashed ${alpha(theme.palette.primary.main, 0.2)}`,
                            }}
                        >
                            {hasData ? (
                                <Box sx={{ width: "100%", p: 2 }}>
                                    <Box sx={{ display: "flex", alignItems: "flex-end", gap: 2, height: 150, justifyContent: "center" }}>
                                        {[40, 65, 45, 80, 55, 70].map((height, i) => (
                                            <Box
                                                key={i}
                                                sx={{
                                                    width: 40,
                                                    height: height,
                                                    background: `linear-gradient(180deg, ${theme.palette.secondary.main} 0%, ${theme.palette.primary.main} 100%)`,
                                                    borderRadius: "8px 8px 0 0",
                                                    transition: "height 0.3s ease",
                                                    "&:hover": {
                                                        height: height + 10,
                                                    },
                                                }}
                                            />
                                        ))}
                                    </Box>
                                    <Box sx={{ display: "flex", justifyContent: "center", gap: 5, mt: 2 }}>
                                        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(day => (
                                            <Typography key={day} variant="caption" color="text.secondary">{day}</Typography>
                                        ))}
                                    </Box>
                                </Box>
                            ) : (
                                <>
                                    <DataUsageIcon sx={{ fontSize: 48, color: alpha(theme.palette.primary.main, 0.3) }} />
                                    <Typography variant="body1" color="text.secondary">
                                        Connect channels and run campaigns to see analytics
                                    </Typography>
                                    <Button 
                                        variant="outlined" 
                                        size="small"
                                        onClick={() => onNavigate?.("campaigns")}
                                        sx={{ mt: 1 }}
                                    >
                                        Create Your First Campaign
                                    </Button>
                                </>
                            )}
                        </Paper>
                    </CardContent>
                </Card>

                {/* Navigation Cards with Blank States */}
                <Grid container spacing={3}>
                    {SECTIONS.map((section) => (
                        <Grid item xs={12} sm={6} md={3} key={section.id}>
                            <Card
                                sx={{
                                    textAlign: "center",
                                    cursor: "pointer",
                                    height: "100%",
                                    display: "flex",
                                    flexDirection: "column",
                                    position: "relative",
                                    overflow: "visible",
                                    "&:hover": { 
                                        boxShadow: 12,
                                        "& .section-icon": {
                                            transform: "scale(1.1) rotate(5deg)",
                                        }
                                    },
                                }}
                                onClick={() => onNavigate?.(section.id)}
                            >
                                <CardContent sx={{ flexGrow: 1 }}>
                                    <Box 
                                        className="section-icon"
                                        sx={{ 
                                            color: section.color,
                                            mb: 2,
                                            transition: "transform 0.3s ease",
                                            transform: "scale(1)",
                                            display: "inline-block",
                                            p: 1.5,
                                            borderRadius: "50%",
                                            bgcolor: alpha(section.color, 0.1),
                                        }}
                                    >
                                        {section.icon}
                                    </Box>
                                    <Typography variant="h6" gutterBottom>
                                        {section.label}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                        {section.desc}
                                    </Typography>
                                    
                                    {/* Blank state indicator for sections with no data */}
                                    {((section.id === "channels" && stats.channels === 0) ||
                                      (section.id === "campaigns" && stats.campaigns === 0) ||
                                      (section.id === "leads" && stats.leads === 0)) && (
                                        <Box sx={{ mt: "auto" }}>
                                            <Divider sx={{ my: 1.5 }} />
                                            <Chip 
                                                label={section.emptyState}
                                                size="small"
                                                sx={{ 
                                                    bgcolor: alpha(section.color, 0.1),
                                                    color: section.color,
                                                    fontSize: "0.7rem",
                                                }}
                                            />
                                            <Typography 
                                                variant="caption" 
                                                display="block" 
                                                sx={{ 
                                                    mt: 1,
                                                    color: theme.palette.primary.main,
                                                    fontWeight: 600,
                                                }}
                                            >
                                                {section.emptyAction} →
                                            </Typography>
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
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
            <ChatBot />
        </ThemeProvider>
    );
}