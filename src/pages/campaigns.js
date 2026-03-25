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
    Visibility as VisibilityIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';

const CampaignsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingCampaign, setEditingCampaign] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        status: 'draft'
    });

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

    useEffect(() => {
        fetchCampaigns();
    }, []);

    const fetchCampaigns = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns`,
                { headers: getAuthHeaders() }
            );
            setCampaigns(response.data.campaigns || []);
            setError('');
        } catch (error) {
            console.error('Error fetching campaigns:', error);
            setError('Failed to fetch campaigns');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'active':
                return 'success';
            case 'completed':
                return 'default';
            case 'draft':
                return 'warning';
            default:
                return 'default';
        }
    };

    const handleCreateCampaign = () => {
        if (!checkPermission('create')) return;
        setOpenDialog(true);
    };

    const handleSaveCampaign = async () => {
        try {
            if (editingCampaign) {
                // Update existing campaign
                const response = await axios.put(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns/${editingCampaign.id}`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                // Update the campaign in the campaigns array
                setCampaigns(campaigns.map(c => 
                    c.id === editingCampaign.id ? response.data.campaign : c
                ));
            } else {
                // Create new campaign
                const response = await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                // Add the new campaign to the campaigns array
                setCampaigns([...campaigns, response.data.campaign]);
            }
            setOpenDialog(false);
            setEditingCampaign(null);
            setFormData({ name: '', status: 'draft' });
            console.log(`Campaign ${editingCampaign ? 'updated' : 'created'}:`, editingCampaign ? formData : formData);
        } catch (error) {
            console.error(`Error ${editingCampaign ? 'updating' : 'creating'} campaign:`, error);
        }
    };

    const handleEditCampaign = (campaign) => {
        if (!checkPermission('edit')) return;
        setEditingCampaign(campaign);
        setFormData({
            name: campaign.name,
            status: campaign.status
        });
        setOpenDialog(true);
    };

    const handleDeleteCampaign = async (campaign) => {
        if (!checkPermission('delete')) return;
        if (window.confirm(`Are you sure you want to delete "${campaign.name}"?`)) {
            try {
                await axios.delete(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns/${campaign.id}`,
                    { headers: getAuthHeaders() }
                );
                // Remove the campaign from the campaigns array
                setCampaigns(campaigns.filter(c => c.id !== campaign.id));
                console.log('Campaign deleted successfully');
            } catch (error) {
                console.error('Error deleting campaign:', error);
            }
        }
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
                    Campaigns
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreateCampaign}
                >
                    Create Campaign
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
                                Campaign List
                            </Typography>
                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Campaign Name</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Leads</TableCell>
                                            <TableCell>Conversion Rate</TableCell>
                                            <TableCell>Created By</TableCell>
                                            <TableCell>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {campaigns.map((campaign) => (
                                            <TableRow key={campaign.id}>
                                                <TableCell>{campaign.name}</TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={campaign.status}
                                                        color={getStatusColor(campaign.status)}
                                                        size="small"
                                                    />
                                                </TableCell>
                                                <TableCell>{campaign.leads}</TableCell>
                                                <TableCell>{campaign.conversion_rate}%</TableCell>
                                                <TableCell>{campaign.created_by || 'Unknown'}</TableCell>
                                                <TableCell>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleEditCampaign(campaign)}
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleDeleteCampaign(campaign)}
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
                                Campaign Summary
                            </Typography>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Total Campaigns
                                </Typography>
                                <Typography variant="h4">
                                    {campaigns.length}
                                </Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Active Campaigns
                                </Typography>
                                <Typography variant="h4">
                                    {campaigns.filter(c => c.status === 'active').length}
                                </Typography>
                            </Box>
                            <Box>
                                <Typography variant="body2" color="textSecondary">
                                    Total Leads
                                </Typography>
                                <Typography variant="h4">
                                    {campaigns.reduce((sum, c) => sum + c.leads, 0)}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Create Campaign Dialog */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>{editingCampaign ? 'Edit Campaign' : 'Create New Campaign'}</DialogTitle>
                <form onSubmit={(e) => { e.preventDefault(); handleSaveCampaign(); }}>
                    <DialogContent>
                        <TextField
                            fullWidth
                            label="Campaign Name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            margin="normal"
                            required
                        />
                        <FormControl fullWidth margin="normal">
                            <InputLabel>Status</InputLabel>
                            <Select
                                value={formData.status}
                                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                            >
                                <MenuItem value="draft">Draft</MenuItem>
                                <MenuItem value="active">Active</MenuItem>
                                <MenuItem value="completed">Completed</MenuItem>
                            </Select>
                        </FormControl>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => {
                            setOpenDialog(false);
                            setEditingCampaign(null);
                            setFormData({ name: '', status: 'draft' });
                        }}>Cancel</Button>
                        <Button type="submit" variant="contained">
                            {editingCampaign ? 'Update Campaign' : 'Create Campaign'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default CampaignsPage;
