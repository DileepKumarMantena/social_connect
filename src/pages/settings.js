import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    CircularProgress,
    Alert,
    Switch,
    FormControlLabel,
    TextField,
    Button,
    Divider,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Chip
} from '@mui/material';
import {
    Notifications as NotificationsIcon,
    Security as SecurityIcon,
    Palette as PaletteIcon,
    Language as LanguageIcon,
    Schedule as ScheduleIcon,
    Save as SaveIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const SettingsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [settings, setSettings] = useState({
        notifications: {
            email_alerts: true,
            sms_alerts: false,
            push_notifications: true,
            weekly_reports: true
        },
        preferences: {
            theme: 'light',
            language: 'en',
            timezone: 'UTC',
            date_format: 'MM/DD/YYYY'
        },
        security: {
            session_timeout: 30,
            two_factor_auth: false,
            login_notifications: true
        }
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/settings`,
                { headers: getAuthHeaders() }
            );
            setSettings(response.data.settings || settings);
            setError('');
        } catch (error) {
            console.error('Error fetching settings:', error);
            setError('Failed to fetch settings');
        } finally {
            setLoading(false);
        }
    };

    const handleSaveSettings = async () => {
        try {
            setSaving(true);
            // TODO: Implement save settings API call
            console.log('Saving settings:', settings);
            setSuccess('Settings saved successfully!');
            setError('');
            setTimeout(() => setSuccess(''), 3000);
        } catch (error) {
            console.error('Error saving settings:', error);
            setError('Failed to save settings');
        } finally {
            setSaving(false);
        }
    };

    const handleNotificationChange = (key, value) => {
        setSettings(prev => ({
            ...prev,
            notifications: {
                ...prev.notifications,
                [key]: value
            }
        }));
    };

    const handlePreferenceChange = (key, value) => {
        setSettings(prev => ({
            ...prev,
            preferences: {
                ...prev.preferences,
                [key]: value
            }
        }));
    };

    const handleSecurityChange = (key, value) => {
        setSettings(prev => ({
            ...prev,
            security: {
                ...prev.security,
                [key]: value
            }
        }));
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                    <Typography variant="h4" component="h1">
                        Settings
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Manage your account preferences and security
                    </Typography>
                </Box>
                <Box>
                    <Button
                        variant="outlined"
                        startIcon={<RefreshIcon />}
                        onClick={fetchSettings}
                        sx={{ mr: 2 }}
                    >
                        Refresh
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={handleSaveSettings}
                        disabled={saving}
                    >
                        {saving ? 'Saving...' : 'Save Changes'}
                    </Button>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                    {success}
                </Alert>
            )}

            <Grid container spacing={3}>
                {/* Notification Settings */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <NotificationsIcon color="primary" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Notification Preferences
                                </Typography>
                            </Box>
                            <Box>
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={settings.notifications.email_alerts}
                                            onChange={(e) => handleNotificationChange('email_alerts', e.target.checked)}
                                        />
                                    }
                                    label="Email Alerts"
                                />
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={settings.notifications.sms_alerts}
                                            onChange={(e) => handleNotificationChange('sms_alerts', e.target.checked)}
                                        />
                                    }
                                    label="SMS Alerts"
                                />
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={settings.notifications.push_notifications}
                                            onChange={(e) => handleNotificationChange('push_notifications', e.target.checked)}
                                        />
                                    }
                                    label="Push Notifications"
                                />
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={settings.notifications.weekly_reports}
                                            onChange={(e) => handleNotificationChange('weekly_reports', e.target.checked)}
                                        />
                                    }
                                    label="Weekly Reports"
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* User Preferences */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <PaletteIcon color="primary" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    User Preferences
                                </Typography>
                            </Box>
                            <Box>
                                <FormControl fullWidth margin="normal">
                                    <InputLabel>Theme</InputLabel>
                                    <Select
                                        value={settings.preferences.theme}
                                        onChange={(e) => handlePreferenceChange('theme', e.target.value)}
                                    >
                                        <MenuItem value="light">Light</MenuItem>
                                        <MenuItem value="dark">Dark</MenuItem>
                                        <MenuItem value="auto">Auto</MenuItem>
                                    </Select>
                                </FormControl>
                                <FormControl fullWidth margin="normal">
                                    <InputLabel>Language</InputLabel>
                                    <Select
                                        value={settings.preferences.language}
                                        onChange={(e) => handlePreferenceChange('language', e.target.value)}
                                    >
                                        <MenuItem value="en">English</MenuItem>
                                        <MenuItem value="es">Spanish</MenuItem>
                                        <MenuItem value="fr">French</MenuItem>
                                        <MenuItem value="de">German</MenuItem>
                                    </Select>
                                </FormControl>
                                <FormControl fullWidth margin="normal">
                                    <InputLabel>Timezone</InputLabel>
                                    <Select
                                        value={settings.preferences.timezone}
                                        onChange={(e) => handlePreferenceChange('timezone', e.target.value)}
                                    >
                                        <MenuItem value="UTC">UTC</MenuItem>
                                        <MenuItem value="EST">Eastern Time</MenuItem>
                                        <MenuItem value="PST">Pacific Time</MenuItem>
                                        <MenuItem value="GMT">Greenwich Mean Time</MenuItem>
                                    </Select>
                                </FormControl>
                                <FormControl fullWidth margin="normal">
                                    <InputLabel>Date Format</InputLabel>
                                    <Select
                                        value={settings.preferences.date_format}
                                        onChange={(e) => handlePreferenceChange('date_format', e.target.value)}
                                    >
                                        <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                                        <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                                        <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                                    </Select>
                                </FormControl>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Security Settings */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={2}>
                                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Security Settings
                                </Typography>
                            </Box>
                            <Box>
                                <TextField
                                    fullWidth
                                    label="Session Timeout (minutes)"
                                    type="number"
                                    value={settings.security.session_timeout}
                                    onChange={(e) => handleSecurityChange('session_timeout', parseInt(e.target.value))}
                                    margin="normal"
                                />
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={settings.security.two_factor_auth}
                                            onChange={(e) => handleSecurityChange('two_factor_auth', e.target.checked)}
                                        />
                                    }
                                    label="Two-Factor Authentication"
                                />
                                <FormControlLabel
                                    control={
                                        <Switch
                                            checked={settings.security.login_notifications}
                                            onChange={(e) => handleSecurityChange('login_notifications', e.target.checked)}
                                        />
                                    }
                                    label="Login Notifications"
                                />
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Account Information */}
                <Grid item xs={12} md={6}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Account Information
                            </Typography>
                            <Box>
                                <TextField
                                    fullWidth
                                    label="Username"
                                    value={user?.username || ''}
                                    margin="normal"
                                    disabled
                                />
                                <TextField
                                    fullWidth
                                    label="Email"
                                    value={user?.email || ''}
                                    margin="normal"
                                    disabled
                                />
                                <TextField
                                    fullWidth
                                    label="Name"
                                    value={user?.name || ''}
                                    margin="normal"
                                    disabled
                                />
                                <TextField
                                    fullWidth
                                    label="Role"
                                    value={user?.role || ''}
                                    margin="normal"
                                    disabled
                                />
                                <Box mt={2}>
                                    <Chip
                                        label={`Account Status: ${user?.activitystatus ? 'Active' : 'Inactive'}`}
                                        color={user?.activitystatus ? 'success' : 'error'}
                                        size="small"
                                    />
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default SettingsPage;
