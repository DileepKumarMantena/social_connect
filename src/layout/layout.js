import React, { useState } from "react";
import { useAuth } from '../contexts/AuthContext';
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
import '@fontsource/nunito'

const drawerWidth = 280;
const collapsedDrawerWidth = 50;

// Beautiful Blue Ocean Theme
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
    },
    typography: {
        fontFamily: '"nunito", "Roboto", "Helvetica", "Arial", sans-serif',
        h6: {
            fontWeight: 600,
            letterSpacing: "0.5px",
        },
    },
    shape: {
        borderRadius: 12,
    },
    components: {
        MuiDrawer: {
            styleOverrides: {
                paper: {
                    background: "linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%)",
                    border: "none",
                    boxShadow: "4px 0 20px rgba(0, 30, 60, 0.1)",
                },
            },
        },
        MuiListItemButton: {
            styleOverrides: {
                root: {
                    margin: "4px 12px",
                    borderRadius: 12,
                    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    "&:hover": {
                        backgroundColor: alpha("#00b4d8", 0.12),
                        transform: "translateX(4px)",
                        boxShadow: "0 4px 12px rgba(0, 180, 216, 0.2)",
                    },
                    "&.Mui-selected": {
                        backgroundColor: alpha("#1e4b8c", 0.12),
                        color: "#1e4b8c",
                        "&:hover": {
                            backgroundColor: alpha("#1e4b8c", 0.18),
                        },
                        "& .MuiListItemIcon-root": {
                            color: "#1e4b8c",
                        },
                    },
                },
            },
        },
        MuiListItemIcon: {
            styleOverrides: {
                root: {
                    minWidth: 40,
                    color: "#2b5f8a",
                    transition: "color 0.3s ease",
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    background: "linear-gradient(135deg, #1e4b8c 0%, #2e7eb0 100%)",
                    boxShadow: "0 4px 20px rgba(0, 30, 60, 0.2)",
                },
            },
        },
    },
});

export default function AppLayout({
    onLogout,
    children,
}) {
    const { user, hasRole } = useAuth();
    const [open, setOpen] = useState(true);
    const [hoverOpen, setHoverOpen] = useState(false);
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
    const isTablet = useMediaQuery(theme.breakpoints.between("sm", "md"));

    const effectiveOpen = isMobile ? false : isTablet ? false : open;

    const handleDrawerToggle = () => {
        setOpen(!open);
    };

    const handleDrawerHover = (enter) => {
        if (!open && !isMobile && !isTablet) {
            setHoverOpen(enter);
        }
    };

    const navItems = [
        {
            label: "Dashboard",
            icon: <DashboardIcon />,
            path: "/dashboard",
            tooltip: "Overview & Metrics"
        },

        ...(hasRole('admin')
            ? [
                {
                    label: "Admin Panel",
                    icon: <AdminPanelSettingsIcon />,
                    path: "/admin",
                    tooltip: "User Management"
                },
            ]
            : []),

        ...(hasRole('super_admin')
            ? [
                {
                    label: "Super Admin",
                    icon: <AdminPanelSettingsIcon />,
                    path: "/super-admin",
                    tooltip: "Admin Controls"
                },
            ]
            : [
                {
                    label: "Campaigns",
                    icon: <CampaignIcon />,
                    path: "/campaigns",
                    tooltip: "Manage Campaigns"
                },
                {
                    label: "Analytics",
                    icon: <InsightsIcon />,
                    path: "/analytics",
                    tooltip: "Performance Insights"
                },
                {
                    label: "Leads",
                    icon: <GroupIcon />,
                    path: "/leads",
                    tooltip: "Lead Management"
                },
                {
                    label: "Channels",
                    icon: <PhoneIphoneIcon />,
                    path: "/channels",
                    tooltip: "Channel Integration"
                },
            ]),

        ...(hasRole('user')
            ? [{
                label: "Scheduler",
                icon: <ScheduleIcon />,
                path: "/scheduler",
                tooltip: "Content Schedule"
            }]
            : []),

        {
            label: "Settings",
            icon: <SettingsIcon />,
            path: "/settings",
            tooltip: "Account Settings"
        },
    ];

    const currentWidth = isMobile
        ? 0
        : (effectiveOpen || hoverOpen)
            ? drawerWidth
            : collapsedDrawerWidth;

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />

            <Box sx={{
                display: "flex",
                minHeight: "100vh",
                background: theme.palette.background.default,
            }}>
                {/* Top Navbar */}
                <AppBar
                    position="fixed"
                    sx={{
                        zIndex: (theme) => theme.zIndex.drawer + 1,
                        transition: "all 0.3s ease",
                    }}
                >
                    <Toolbar sx={{ justifyContent: "space-between" }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            {/* Menu icon - visible on all screens to control drawer */}
                            <IconButton
                                color="inherit"
                                aria-label="toggle drawer"
                                onClick={handleDrawerToggle}
                                edge="start"
                                sx={{
                                    mr: 1,
                                    background: alpha("#ffffff", 0.1),
                                    "&:hover": {
                                        background: alpha("#ffffff", 0.2),
                                    },
                                }}
                            >
                                {!isMobile && !isTablet ? (open ? <ChevronLeftIcon /> : <MenuIcon />) : <MenuIcon />}
                            </IconButton>

                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <Typography
                                    variant="h6"
                                    sx={{
                                        fontWeight: 700,
                                        color: '#fff',
                                        display: { xs: "none", sm: "block" }
                                    }}
                                >
                                    Social Connect
                                </Typography>
                            </Box>
                        </Box>

                        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                            {/* Search - Hidden on mobile */}
                            <Paper
                                elevation={0}
                                sx={{
                                    display: { xs: "none", md: "flex" },
                                    alignItems: "center",
                                    background: alpha("#ffffff", 0.15),
                                    borderRadius: 4,
                                    px: 2,
                                    py: 0.5,
                                    "&:hover": {
                                        background: alpha("#ffffff", 0.25),
                                    },
                                }}
                            >
                                <SearchIcon sx={{ color: alpha("#ffffff", 0.7), mr: 1 }} />
                                <Typography variant="body2" sx={{ color: alpha("#ffffff", 0.7) }}>
                                    Search...
                                </Typography>
                            </Paper>

                            {/* Notifications */}
                            <Tooltip title="Notifications" TransitionComponent={Zoom}>
                                <IconButton color="inherit" sx={{ background: alpha("#ffffff", 0.1) }}>
                                    <Badge badgeContent={3} color="error">
                                        <NotificationsNoneIcon />
                                    </Badge>
                                </IconButton>
                            </Tooltip>

                            {/* User Profile */}
                            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                <Avatar
                                    sx={{
                                        bgcolor: alpha("#90e0ef", 0.2),
                                        color: "#ffffff",
                                        width: 40,
                                        height: 40,
                                    }}
                                >
                                    <AccountCircleIcon />
                                </Avatar>
                                <Box sx={{ display: { xs: "none", sm: "block" } }}>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                        {user?.name}
                                    </Typography>
                                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                                        {user?.role}
                                    </Typography>
                                </Box>
                            </Box>
                        </Box>
                    </Toolbar>
                </AppBar>

                {/* Sidebar - Mobile Drawer */}
                <Drawer
                    variant="temporary"
                    open={isMobile ? open : false}
                    onClose={handleDrawerToggle}
                    sx={{
                        display: { xs: 'block', sm: 'block', md: 'none' },
                        '& .MuiDrawer-paper': {
                            width: drawerWidth,
                            boxSizing: 'border-box',
                            background: "linear-gradient(180deg, #ffffff 0%, #e3f2fd 100%)",
                        },
                    }}
                >
                    <Toolbar />
                    <Box sx={{ overflow: "auto", py: 1 }}>
                        <List>
                            {navItems.map((item) => (
                                <ListItemButton
                                    key={item.path}
                                    selected={window.location.hash === `#${item.path}`}
                                    onClick={() => {
                                        window.location.hash = item.path;
                                        handleDrawerToggle();
                                    }}
                                    sx={{
                                        mx: 1,
                                        py: 0.5,
                                        borderRadius: 3,
                                        position: "relative",
                                        overflow: "hidden",
                                        '&::before': {
                                            content: '""',
                                            position: "absolute",
                                            left: 0,
                                            top: 0,
                                            bottom: 0,
                                            width: 4,
                                            background: "linear-gradient(180deg, #00b4d8 0%, #0077b6 100%)",
                                            borderRadius: "0 4px 4px 0",
                                            opacity: window.location.hash === `#${item.path}` ? 1 : 0,
                                            transition: "opacity 0.3s ease",
                                            margin: 'auto'
                                        },
                                        '&:hover::before': {
                                            opacity: 0.5,
                                        },
                                    }}
                                >
                                    <ListItemIcon sx={{
                                        color: window.location.hash === `#${item.path}` ? "#0077b6" : "#2b5f8a",
                                        minWidth: 40,
                                        justifyContent: 'center',
                                    }}>
                                        {item.icon}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.label}
                                        secondary={item.tooltip}
                                        secondaryTypographyProps={{
                                            sx: {
                                                fontSize: '0.7rem',
                                                opacity: 0.7,
                                            }
                                        }}
                                        sx={{
                                            '& .MuiTypography-root': {
                                                fontWeight: window.location.hash === `#${item.path}` ? 600 : 400,
                                            },
                                        }}
                                    />
                                </ListItemButton>
                            ))}
                        </List>

                        <Divider sx={{
                            my: 2,
                            borderColor: alpha("#00b4d8", 0.2),
                            mx: 2,
                        }} />

                        <List>
                            <ListItemButton
                                onClick={onLogout}
                                sx={{
                                    mx: 1,
                                    borderRadius: 3,
                                    color: "#d32f2f",
                                    '&:hover': {
                                        backgroundColor: alpha("#d32f2f", 0.08),
                                    },
                                }}
                            >
                                <ListItemIcon sx={{
                                    color: "#d32f2f",
                                    minWidth: 40,
                                    justifyContent: 'center',
                                }}>
                                    <LogoutIcon />
                                </ListItemIcon>
                                <ListItemText primary="Logout" />
                            </ListItemButton>
                        </List>
                    </Box>
                </Drawer>

                {/* Sidebar - Desktop Permanent Drawer */}
                <Drawer
                    variant="permanent"
                    sx={{
                        width: currentWidth,
                        flexShrink: 0,
                        display: { xs: 'none', sm: 'none', md: 'block' },
                        transition: "width 0.3s ease",
                        "& .MuiDrawer-paper": {
                            width: currentWidth,
                            boxSizing: "border-box",
                            overflowX: "hidden",
                            transition: "width 0.3s ease, background-color 0.3s ease",
                            borderRight: "1px solid rgba(0, 180, 216, 0.12)",
                            background: "linear-gradient(180deg, #ffffff 0%, #e3f2fd 100%)",
                            ...(!(effectiveOpen || hoverOpen) && {
                                '& .MuiListItemText-root': {
                                    opacity: 0,
                                    transition: 'opacity 0.2s',
                                },
                                '& .MuiListItemIcon-root': {
                                    minWidth: 'auto',
                                    margin: '0 auto',
                                },
                                '& .MuiListItemButton-root': {
                                    justifyContent: 'center',
                                    px: 1,
                                },
                            }),
                        },
                    }}
                    onMouseEnter={() => handleDrawerHover(true)}
                    onMouseLeave={() => handleDrawerHover(false)}
                >
                    <Toolbar />
                    <Box sx={{ overflow: "auto", py: 1 }}>
                        <List>
                            {navItems.map((item) => (
                                <Tooltip
                                    key={item.path}
                                    title={!(effectiveOpen || hoverOpen) ? item.label : ""}
                                    placement="right"
                                    TransitionComponent={Zoom}
                                >
                                    <ListItemButton
                                        selected={window.location.hash === `#${item.path}`}
                                        onClick={() => window.location.hash = item.path}
                                        sx={{
                                            mx: 1,
                                            py: 0.5,
                                            borderRadius: 3,
                                            position: "relative",
                                            overflow: "hidden",
                                            '&::before': {
                                                content: '""',
                                                position: "absolute",
                                                left: 0,
                                                top: 0,
                                                bottom: 0,
                                                width: 4,
                                                background: "linear-gradient(180deg, #00b4d8 0%, #0077b6 100%)",
                                                borderRadius: "0 4px 4px 0",
                                                opacity: window.location.hash === `#${item.path}` ? 1 : 0,
                                                transition: "opacity 0.3s ease",
                                                margin: 'auto'
                                            },
                                            '&:hover::before': {
                                                opacity: 0.5,
                                            },
                                        }}
                                    >
                                        <ListItemIcon sx={{
                                            color: window.location.hash === `#${item.path}` ? "#0077b6" : "#2b5f8a",
                                            minWidth: (effectiveOpen || hoverOpen) ? 40 : 'auto',
                                            margin: (effectiveOpen || hoverOpen) && 'auto',
                                            justifyContent: 'center',
                                        }}>
                                            {item.icon}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={item.label}
                                            secondary={item.tooltip}
                                            secondaryTypographyProps={{
                                                sx: {
                                                    fontSize: '0.7rem',
                                                    opacity: 0.7,
                                                    display: (effectiveOpen || hoverOpen) ? 'block' : 'none',
                                                }
                                            }}
                                            sx={{
                                                opacity: (effectiveOpen || hoverOpen) ? 1 : 0,
                                                transition: 'opacity 0.2s',
                                                '& .MuiTypography-root': {
                                                    fontWeight: window.location.hash === `#${item.path}` ? 600 : 400,
                                                },
                                            }}
                                        />
                                    </ListItemButton>
                                </Tooltip>
                            ))}
                        </List>

                        <Divider sx={{
                            my: 2,
                            borderColor: alpha("#00b4d8", 0.2),
                            mx: (effectiveOpen || hoverOpen) ? 2 : 1,
                        }} />

                        <List>
                            <Tooltip
                                title={!(effectiveOpen || hoverOpen) ? "Logout" : ""}
                                placement="right"
                                TransitionComponent={Zoom}
                            >
                                <ListItemButton
                                    onClick={onLogout}
                                    sx={{
                                        mx: 1,
                                        borderRadius: 3,
                                        color: "#d32f2f",
                                        '&:hover': {
                                            backgroundColor: alpha("#d32f2f", 0.08),
                                        },
                                    }}
                                >
                                    <ListItemIcon sx={{
                                        color: "#d32f2f",
                                        minWidth: (effectiveOpen || hoverOpen) ? 40 : 'auto',
                                        justifyContent: 'center',
                                    }}>
                                        <LogoutIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Logout"
                                        sx={{
                                            opacity: (effectiveOpen || hoverOpen) ? 1 : 0,
                                            transition: 'opacity 0.2s',
                                        }}
                                    />
                                </ListItemButton>
                            </Tooltip>
                        </List>
                    </Box>
                </Drawer>

                {/* Main Content */}
                <Box
                    component="main"
                    sx={{
                        flexGrow: 1,
                        p: { xs: 2, sm: 3 },
                        minHeight: "100vh",
                        transition: "margin-left 0.3s ease",
                        width: { xs: "100%", md: `calc(100% - ${currentWidth}px)` },
                        background: theme.palette.background.default,
                    }}
                >
                    <Toolbar />
                    <Fade in={true} timeout={500}>
                        <Box>
                            {children}
                        </Box>
                    </Fade>
                </Box>
            </Box>
        </ThemeProvider>
    );
}