import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Chip,
    Button,
    IconButton,
    Grid,
    CircularProgress,
    Alert,
    LinearProgress
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Link as LinkIcon,
    Settings as SettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const ChannelsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [channels, setChannels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchChannels();
    }, []);

    const fetchChannels = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/channels`,
                { headers: getAuthHeaders() }
            );
            setChannels(response.data.channels || []);
            setError('');
        } catch (error) {
            console.error('Error fetching channels:', error);
            setError('Failed to fetch channels');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (connected, active) => {
        if (!connected) return 'error';
        if (active) return 'success';
        return 'warning';
    };

    const getStatusText = (connected, active) => {
        if (!connected) return 'Disconnected';
        if (active) return 'Active';
        return 'Inactive';
    };

    const handleConnectChannel = (channel) => {
        // TODO: Implement channel connection dialog
        console.log('Connect channel:', channel);
    };

    const handleConfigureChannel = (channel) => {
        // TODO: Implement channel configuration dialog
        console.log('Configure channel:', channel);
    };

    const handleDeleteChannel = (channel) => {
        // TODO: Implement delete channel confirmation
        console.log('Delete channel:', channel);
    };

    const getChannelIcon = (name) => {
        const icons = {
            'facebook': '📘',
            'instagram': '📷',
            'linkedin': '💼',
            'twitter': '🐦'
        };
        return icons[name.toLowerCase()] || '📱';
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
                <Typography variant="h4" component="h1">
                    Channels
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => console.log('Add new channel')}
                >
                    Add Channel
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Channel List
                            </Typography>
                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Channel</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Followers</TableCell>
                                            <TableCell>Created By</TableCell>
                                            <TableCell>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {channels.map((channel) => (
                                            <TableRow key={channel.id}>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center">
                                                        <Typography variant="h6" sx={{ mr: 1 }}>
                                                            {getChannelIcon(channel.name)}
                                                        </Typography>
                                                        <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                                                            {channel.name}
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={getStatusText(channel.connected, channel.active)}
                                                        color={getStatusColor(channel.connected, channel.active)}
                                                        size="small"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body2">
                                                        {channel.followers.toLocaleString()}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>{channel.created_by || 'Unknown'}</TableCell>
                                                <TableCell>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleConnectChannel(channel)}
                                                        title={channel.connected ? 'Reconnect' : 'Connect'}
                                                    >
                                                        <LinkIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleConfigureChannel(channel)}
                                                        title="Configure"
                                                    >
                                                        <SettingsIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleDeleteChannel(channel)}
                                                        title="Delete"
                                                    >
                                                        <DeleteIcon />
                                                    </IconButton>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Channel Summary
                            </Typography>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Total Channels
                                </Typography>
                                <Typography variant="h4">
                                    {channels.length}
                                </Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Connected
                                </Typography>
                                <Typography variant="h4">
                                    {channels.filter(c => c.connected).length}
                                </Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Active
                                </Typography>
                                <Typography variant="h4">
                                    {channels.filter(c => c.active).length}
                                </Typography>
                            </Box>
                            <Box>
                                <Typography variant="body2" color="textSecondary">
                                    Total Followers
                                </Typography>
                                <Typography variant="h4">
                                    {channels.reduce((sum, c) => sum + c.followers, 0).toLocaleString()}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>

                    <Card sx={{ mt: 2 }}>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Connection Status
                            </Typography>
                            <Box>
                                {channels.map((channel) => (
                                    <Box key={channel.id} mb={1}>
                                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                                            <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                                {channel.name}
                                            </Typography>
                                            <Typography variant="body2" color="textSecondary">
                                                {getStatusText(channel.connected, channel.active)}
                                            </Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={channel.connected && channel.active ? 100 : channel.connected ? 50 : 0}
                                            color={getStatusColor(channel.connected, channel.active)}
                                            sx={{ height: 4, borderRadius: 2 }}
                                        />
                                    </Box>
                                ))}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default ChannelsPage;
