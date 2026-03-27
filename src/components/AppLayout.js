import React from 'react';
import { Box, AppBar, Toolbar, Typography, Button, IconButton, Menu, MenuItem, Chip, Avatar } from '@mui/material';
import { AccountCircle, Menu as MenuIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function AppLayout({ children, onLogout }) {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [mobileMenuAnchor, setMobileMenuAnchor] = React.useState(null);
  const { user } = useAuth();

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMobileMenuOpen = (event) => {
    setMobileMenuAnchor(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchor(null);
  };

  const handleNavigation = (path) => {
    navigate(path);
    handleMobileMenuClose();
  };

  const handleProfile = () => {
    navigate('/profile');
    handleClose();
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={handleMobileMenuOpen}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Social Connect
          </Typography>
          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
              sx={{ mr: 2 }}
            >
              <AccountCircle />
            </IconButton>
            {user && (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                <Typography variant="body1" sx={{ fontWeight: 'medium', whiteSpace: 'nowrap' }}>
                  {user.name}
                </Typography>
                <Chip
                  label={user.role?.replace('_', ' ').toUpperCase()}
                  size="small"
                  color="secondary"
                  sx={{ mt: 0.5 }}
                />
              </Box>
            )}
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleProfile}>Profile</MenuItem>
              <MenuItem onClick={onLogout}>Logout</MenuItem>
            </Menu>
          </div>
        </Toolbar>
      </AppBar>

      <Menu
        anchorEl={mobileMenuAnchor}
        open={Boolean(mobileMenuAnchor)}
        onClose={handleMobileMenuClose}
      >
        <MenuItem onClick={() => handleNavigation('/')}>Dashboard</MenuItem>
        <MenuItem onClick={() => handleNavigation('/profile')}>Profile</MenuItem>
        <MenuItem onClick={() => handleNavigation('/campaigns')}>Campaigns</MenuItem>
        <MenuItem onClick={() => handleNavigation('/leads')}>Leads</MenuItem>
        <MenuItem onClick={() => handleNavigation('/channels')}>Channels</MenuItem>
        <MenuItem onClick={() => handleNavigation('/analytics')}>Analytics</MenuItem>
        <MenuItem onClick={() => handleNavigation('/scheduler')}>Scheduler</MenuItem>
        <MenuItem onClick={() => handleNavigation('/settings')}>Settings</MenuItem>
        <MenuItem onClick={() => handleNavigation('/admin')}>Admin Panel</MenuItem>
      </Menu>

      <Box component="main" sx={{ p: 3 }}>
        {children}
      </Box>
    </Box>
  );
}

export default AppLayout;
