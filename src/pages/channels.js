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
    LinearProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem
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
import Swal from 'sweetalert2';

const ChannelsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [channels, setChannels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingChannel, setEditingChannel] = useState(null);

    // Check if user has permission to perform action
    const checkPermission = (action) => {
        if (user?.role === 'user') {
            Swal.fire({
                icon: 'error',
                title: 'Access Denied',
                text: "You don't have enough access rights for this action",
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            });
            return false;
        }
        return true;
    };
    const [formData, setFormData] = useState({
        name: '',
        connected: false,
        active: false,
        followers: 0
    });

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

    const handleConnectChannel = async (channel) => {
        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/channels/${channel.id}/connect`,
                {},
                { headers: getAuthHeaders() }
            );
            // Update the channel in the channels array directly
            setChannels(channels.map(c => 
                c.id === channel.id ? { ...c, connected: true, active: true } : c
            ));
            console.log('Channel connected successfully:', response.data);
        } catch (error) {
            console.error('Error connecting channel:', error);
        }
    };

    const handleConfigureChannel = (channel) => {
        if (!checkPermission('edit')) return;
        setEditingChannel(channel);
        setFormData({
            name: channel.name,
            connected: channel.connected,
            active: channel.active,
            followers: channel.followers
        });
        setOpenDialog(true);
    };

    const handleCreateChannel = () => {
        if (!checkPermission('create')) return;
        setOpenDialog(true);
    };

    const handleSaveChannel = async () => {
        try {
            if (editingChannel) {
                // Update existing channel
                const response = await axios.put(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/channels/${editingChannel.id}`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                // Update the channel in the channels array
                setChannels(channels.map(c => 
                    c.id === editingChannel.id ? response.data.channel : c
                ));
            } else {
                // Create new channel
                const response = await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/channels`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                // Add the new channel to the channels array
                setChannels([...channels, response.data.channel]);
            }
            setOpenDialog(false);
            setEditingChannel(null);
            setFormData({ name: '', connected: false, active: false, followers: 0 });
            console.log(`Channel ${editingChannel ? 'updated' : 'created'}:`, editingChannel ? formData : formData);
        } catch (error) {
            console.error(`Error ${editingChannel ? 'updating' : 'creating'} channel:`, error);
        }
    };

    const handleDeleteChannel = async (channel) => {
        if (!checkPermission('delete')) return;
        if (window.confirm(`Are you sure you want to delete "${channel.name}"?`)) {
            try {
                await axios.delete(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/channels/${channel.id}`,
                    { headers: getAuthHeaders() }
                );
                // Remove the channel from the channels array
                setChannels(channels.filter(c => c.id !== channel.id));
                console.log('Channel deleted successfully');
            } catch (error) {
                console.error('Error deleting channel:', error);
            }
        }
    };

    const handleDisconnectChannel = async (channel) => {
        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/channels/${channel.id}/disconnect`,
                {},
                { headers: getAuthHeaders() }
            );
            // Update the channel in the channels array directly
            setChannels(channels.map(c => 
                c.id === channel.id ? { ...c, connected: false, active: false } : c
            ));
            console.log('Channel disconnected successfully:', response.data);
        } catch (error) {
            console.error('Error disconnecting channel:', error);
        }
    };

    const handleConnectionStatusChange = async (channel, newStatus) => {
        try {
            if (newStatus) {
                // Connect the channel
                const response = await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/channels/${channel.id}/connect`,
                    {},
                    { headers: getAuthHeaders() }
                );
                // Update the channel in the channels array
                setChannels(channels.map(c => 
                    c.id === channel.id ? { ...c, connected: true, active: true } : c
                ));
                console.log('Channel connected successfully:', response.data);
            } else {
                // Disconnect the channel
                const response = await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/channels/${channel.id}/disconnect`,
                    {},
                    { headers: getAuthHeaders() }
                );
                // Update the channel in the channels array
                setChannels(channels.map(c => 
                    c.id === channel.id ? { ...c, connected: false, active: false } : c
                ));
                console.log('Channel disconnected successfully:', response.data);
            }
        } catch (error) {
            console.error('Error updating channel connection status:', error);
        }
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
                    onClick={handleCreateChannel}
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
                                                    <FormControl size="small" sx={{ minWidth: 120 }}>
                                                        <Select
                                                            value={channel.connected && channel.active ? 'connected' : channel.connected ? 'inactive' : 'disconnected'}
                                                            onChange={(e) => handleConnectionStatusChange(channel, e.target.value === 'connected' || e.target.value === 'inactive')}
                                                            size="small"
                                                        >
                                                            <MenuItem value="disconnected">Disconnected</MenuItem>
                                                            <MenuItem value="inactive">Inactive</MenuItem>
                                                            <MenuItem value="connected">Connected</MenuItem>
                                                        </Select>
                                                    </FormControl>
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
                                                        onClick={() => handleConfigureChannel(channel)}
                                                        title="Edit"
                                                    >
                                                        <EditIcon />
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
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
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
                        </Grid>
                        <Grid item xs={12}>
                            <Card>
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
                </Grid>
            </Grid>

            {/* Create Channel Dialog */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>{editingChannel ? 'Edit Channel' : 'Create New Channel'}</DialogTitle>
                <form onSubmit={(e) => { e.preventDefault(); handleSaveChannel(); }}>
                    <DialogContent>
                        <TextField
                            fullWidth
                            label="Channel Name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            margin="normal"
                            required
                        />
                        <FormControl fullWidth margin="normal">
                            <InputLabel>Status</InputLabel>
                            <Select
                                value={formData.connected}
                                onChange={(e) => setFormData({ ...formData, connected: e.target.value === 'true' })}
                            >
                                <MenuItem value={false}>Disconnected</MenuItem>
                                <MenuItem value={true}>Connected</MenuItem>
                            </Select>
                        </FormControl>
                        <TextField
                            fullWidth
                            label="Followers"
                            type="number"
                            value={formData.followers}
                            onChange={(e) => setFormData({ ...formData, followers: parseInt(e.target.value) || 0 })}
                            margin="normal"
                        />
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => {
                            setOpenDialog(false);
                            setEditingChannel(null);
                            setFormData({ name: '', connected: false, active: false, followers: 0 });
                        }}>Cancel</Button>
                        <Button type="submit" variant="contained">
                            {editingChannel ? 'Update Channel' : 'Create Channel'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default ChannelsPage;
