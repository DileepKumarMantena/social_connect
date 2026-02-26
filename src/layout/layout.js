import React, { useEffect, useState } from "react";
import {
    AppBar,
    Toolbar,
    Typography,
    Drawer,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Box,
    CssBaseline,
    ThemeProvider,
    createTheme,
    Divider,
    IconButton,
    useMediaQuery,
    alpha,
    Avatar,
    Badge,
    Paper,
    Tooltip,
    Zoom,
    Fade,
} from "@mui/material";

import MenuIcon from "@mui/icons-material/Menu";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import DashboardIcon from "@mui/icons-material/Dashboard";
import CampaignIcon from "@mui/icons-material/Campaign";
import InsightsIcon from "@mui/icons-material/Insights";
import GroupIcon from "@mui/icons-material/Group";
import SettingsIcon from "@mui/icons-material/Settings";
import AdminPanelSettingsIcon from "@mui/icons-material/AdminPanelSettings";
import LogoutIcon from "@mui/icons-material/Logout";
import ScheduleIcon from "@mui/icons-material/Schedule";
import PhoneIphoneIcon from "@mui/icons-material/PhoneIphone";
import NotificationsNoneIcon from "@mui/icons-material/NotificationsNone";
import SearchIcon from "@mui/icons-material/Search";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import WorkIcon from '@mui/icons-material/Work';
import '@fontsource/nunito';
import { useAuth } from "../context/useAuth";
import { Link, useLocation } from "react-router-dom";

const drawerWidth = 280;
const collapsedDrawerWidth = 64;

// Blue Ocean Theme Configuration
const theme = createTheme({
    palette: {
        mode: "light",
        primary: { main: "#1e4b8c", light: "#2e7eb0", dark: "#0a2a4a", contrastText: "#ffffff" },
        secondary: { main: "#00b4d8", light: "#48cae4", dark: "#0096c7" },
        background: { default: "#f0f7ff", paper: "#ffffff" },
        text: { primary: "#023047", secondary: "#2b5f8a" },
    },
    typography: {
        fontFamily: '"nunito", "Roboto", "Helvetica", "Arial", sans-serif',
        h6: { fontWeight: 600, letterSpacing: "0.5px" },
    },
    shape: { borderRadius: 12 },
    components: {
        MuiListItemButton: {
            styleOverrides: {
                root: {
                    margin: "4px 12px",
                    borderRadius: 12,
                    transition: "all 0.3s ease",
                    "&.Mui-selected": {
                        backgroundColor: alpha("#1e4b8c", 0.12),
                        color: "#1e4b8c",
                        "& .MuiListItemIcon-root": { color: "#1e4b8c" },
                    },
                },
            },
        },
    },
});

export default function AppLayout({ onLogout, children }) {
    const [open, setOpen] = useState(true);
    const [hoverOpen, setHoverOpen] = useState(false);
    const { logindata } = useAuth();
    const location = useLocation(); // Hook to get current URL for active states
    const currentPath = location.pathname;

    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
    const isTablet = useMediaQuery(theme.breakpoints.between("sm", "md"));
    
    const effectiveOpen = isMobile ? false : isTablet ? false : open;
    const isExpanded = effectiveOpen || hoverOpen;
    const currentWidth = isMobile ? 0 : isExpanded ? drawerWidth : collapsedDrawerWidth;

    const handleDrawerToggle = () => setOpen(!open);

    const navItems = [
        { label: "Dashboard", icon: <DashboardIcon />, path: "/dashboard", tooltip: "Overview" },
        ...(logindata?.role === "super_admin" ? [
            { label: "Super Admin", icon: <AdminPanelSettingsIcon />, path: "/super-admin", tooltip: "Admin" },
            { label: "Role Management", icon: <WorkIcon />, path: "/roles", tooltip: "Roles" },
            { label: "Campaigns", icon: <CampaignIcon />, path: "/campaigns", tooltip: "Campaigns" },
            { label: "Analytics", icon: <InsightsIcon />, path: "/analytics", tooltip: "Insights" },
            { label: "Leads", icon: <GroupIcon />, path: "/leads", tooltip: "Leads" },
            { label: "Channels", icon: <PhoneIphoneIcon />, path: "/channels", tooltip: "Channels" },
            { label: "Scheduler", icon: <ScheduleIcon />, path: "/scheduler", tooltip: "Schedule" }
        ] : [
            { label: "Campaigns", icon: <CampaignIcon />, path: "/campaigns", tooltip: "Campaigns" },
            { label: "Analytics", icon: <InsightsIcon />, path: "/analytics", tooltip: "Insights" },
            { label: "Leads", icon: <GroupIcon />, path: "/leads", tooltip: "Leads" },
            { label: "Channels", icon: <PhoneIphoneIcon />, path: "/channels", tooltip: "Channels" },
        ]),
        ...(logindata?.role === "user" ? [{ label: "Scheduler", icon: <ScheduleIcon />, path: "/scheduler", tooltip: "Schedule" }] : []),
        { label: "Settings", icon: <SettingsIcon />, path: "/settings", tooltip: "Settings" },
    ];

    const NavList = ({ mobile = false }) => (
        <List sx={{ px: mobile ? 0 : 0 }}>
            {navItems.map((item) => (
                <Tooltip 
                    key={item.path} 
                    title={!isExpanded && !mobile ? item.label : ""} 
                    placement="right" 
                    TransitionComponent={Zoom}
                >
                    <ListItemButton
                        component={Link}
                        to={item.path}
                        selected={currentPath === item.path}
                        onClick={() => isMobile && setOpen(false)}
                        sx={{
                            justifyContent: isExpanded || mobile ? "initial" : "center",
                            px: 2.5,
                            "&::before": {
                                content: '""',
                                position: "absolute",
                                left: 0,
                                height: "60%",
                                width: 4,
                                background: "#00b4d8",
                                borderRadius: "0 4px 4px 0",
                                opacity: currentPath === item.path ? 1 : 0,
                            }
                        }}
                    >
                        <ListItemIcon sx={{ 
                            minWidth: 0, 
                            mr: isExpanded || mobile ? 2 : "auto", 
                            justifyContent: "center",
                            color: currentPath === item.path ? "primary.main" : "text.secondary"
                        }}>
                            {item.icon}
                        </ListItemIcon>
                        {(isExpanded || mobile) && (
                            <ListItemText 
                                primary={item.label} 
                                secondary={item.tooltip}
                                secondaryTypographyProps={{ sx: { fontSize: '0.65rem' }}}
                            />
                        )}
                    </ListItemButton>
                </Tooltip>
            ))}
        </List>
    );

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Box sx={{ display: "flex", minHeight: "100vh" }}>
                
                {/* Navbar */}
                <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
                    <Toolbar sx={{ justifyContent: "space-between" }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            <IconButton color="inherit" onClick={handleDrawerToggle} edge="start">
                                {isExpanded ? <ChevronLeftIcon /> : <MenuIcon />}
                            </IconButton>
                            <Typography variant="h6" sx={{ display: { xs: "none", sm: "block" } }}>
                                Social Connect
                            </Typography>
                        </Box>

                        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                            <Badge badgeContent={3} color="error">
                                <NotificationsNoneIcon />
                            </Badge>
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <Avatar sx={{ bgcolor: alpha("#fff", 0.2) }}><AccountCircleIcon /></Avatar>
                                <Box sx={{ display: { xs: "none", sm: "block" } }}>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{logindata?.tenant_name}</Typography>
                                    <Typography variant="caption" sx={{ opacity: 0.8 }}>{logindata?.role}</Typography>
                                </Box>
                            </Box>
                        </Box>
                    </Toolbar>
                </AppBar>

                {/* Mobile Drawer */}
                <Drawer
                    variant="temporary"
                    open={isMobile && open}
                    onClose={handleDrawerToggle}
                    sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
                >
                    <Toolbar />
                    <NavList mobile />
                </Drawer>

                {/* Desktop Drawer */}
                <Drawer
                    variant="permanent"
                    onMouseEnter={() => !open && setHoverOpen(true)}
                    onMouseLeave={() => setHoverOpen(false)}
                    sx={{
                        display: { xs: 'none', md: 'block' },
                        width: currentWidth,
                        flexShrink: 0,
                        '& .MuiDrawer-paper': {
                            width: currentWidth,
                            transition: theme.transitions.create('width', { duration: 300 }),
                            overflowX: 'hidden',
                        },
                    }}
                >
                    <Toolbar />
                    <NavList />
                    <Divider sx={{ my: 1 }} />
                    <ListItemButton onClick={onLogout} sx={{ mx: 1, borderRadius: 3, color: "error.main" }}>
                        <ListItemIcon sx={{ color: "error.main", minWidth: isExpanded ? 40 : 0, justifyContent: 'center' }}>
                            <LogoutIcon />
                        </ListItemIcon>
                        {isExpanded && <ListItemText primary="Logout" />}
                    </ListItemButton>
                </Drawer>

                {/* Content */}
                <Box component="main" sx={{ flexGrow: 1, p: 3, width: `calc(100% - ${currentWidth}px)` }}>
                    <Toolbar />
                    <Fade in={true} timeout={500}>
                        <Box>{children}</Box>
                    </Fade>
                </Box>
            </Box>
        </ThemeProvider>
    );
}