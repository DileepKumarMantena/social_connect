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
    MenuItem,
    ButtonGroup
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Visibility as VisibilityIcon,
    SmartToy as BotIcon,
    Download as DownloadIcon,
    Image as ImageIcon,
    Close as CloseIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';
import CampaignChatBot from '../components/ChatBot/CampaignChatBot';

const CampaignsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingCampaign, setEditingCampaign] = useState(null);
    const [chatBotOpen, setChatBotOpen] = useState(false);
    const [posterDialogOpen, setPosterDialogOpen] = useState(false);
    const [selectedCampaign, setSelectedCampaign] = useState(null);
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
            
            const campaignsData = response.data.campaigns || [];
            setCampaigns(campaignsData);
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

    const handleCreateWithChatBot = () => {
        if (!checkPermission('create')) return;
        setChatBotOpen(true);
    };

    const handleViewPoster = (campaign) => {
        setSelectedCampaign(campaign);
        setPosterDialogOpen(true);
    };

    const handleDownloadPoster = (campaign) => {
        const posterUrl = campaign.poster_url || '/posters/default_campaign.png';
        const link = document.createElement('a');
        link.href = posterUrl;
        link.download = `${campaign.name.replace(/\s+/g, '_')}_poster.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleCampaignCreated = (newCampaign) => {
        // Add the new campaign to the campaigns list
        setCampaigns(prev => [...prev, newCampaign]);
        setChatBotOpen(false);
        Swal.fire({
            icon: 'success',
            title: 'Campaign Created!',
            text: 'Your campaign has been created successfully with AI assistance.',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'Great!'
        });
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
                <ButtonGroup variant="contained" size="medium">
                    <Button
                        startIcon={<AddIcon />}
                        onClick={handleCreateCampaign}
                    >
                        Create Campaign
                    </Button>
                    <Button
                        startIcon={<BotIcon />}
                        onClick={handleCreateWithChatBot}
                        color="secondary"
                    >
                        AI Assistant
                    </Button>
                </ButtonGroup>
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
                                            <TableCell>Poster</TableCell>
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
                                                <TableCell>
                                                    <Box
                                                        component="img"
                                                        src={campaign.poster_url || '/posters/default_campaign.png'}
                                                        alt={`${campaign.name} poster`}
                                                        sx={{
                                                            width: 60,
                                                            height: 60,
                                                            objectFit: 'cover',
                                                            borderRadius: 1,
                                                            cursor: 'pointer',
                                                            border: '1px solid #e0e0e0',
                                                            '&:hover': {
                                                                borderColor: 'primary.main',
                                                                transform: 'scale(1.05)'
                                                            },
                                                            transition: 'all 0.2s ease-in-out'
                                                        }}
                                                        onClick={() => handleViewPoster(campaign)}
                                                        onError={(e) => {
                                                            e.target.src = '/posters/default_campaign.png';
                                                        }}
                                                    />
                                                </TableCell>
                                                <TableCell>{campaign.leads || 0}</TableCell>
                                                <TableCell>{campaign.conversion_rate || 0}%</TableCell>
                                                <TableCell>{campaign.created_by || 'System'}</TableCell>
                                                <TableCell>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleEditCampaign(campaign)}
                                                        title="Edit Campaign"
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleViewPoster(campaign)}
                                                        title="View Poster"
                                                        color="primary"
                                                    >
                                                        <ImageIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleDownloadPoster(campaign)}
                                                        title="Download Poster"
                                                        color="success"
                                                    >
                                                        <DownloadIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleDeleteCampaign(campaign)}
                                                        title="Delete Campaign"
                                                        color="error"
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

            {/* AI ChatBot Dialog */}
            <CampaignChatBot
                open={chatBotOpen}
                onClose={() => setChatBotOpen(false)}
                onCampaignCreated={handleCampaignCreated}
            />

            {/* Poster Preview Dialog */}
            <Dialog 
                open={posterDialogOpen} 
                onClose={() => setPosterDialogOpen(false)} 
                maxWidth="md" 
                fullWidth
            >
                <DialogTitle>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Typography variant="h6">
                            Campaign Poster: {selectedCampaign?.name}
                        </Typography>
                        <IconButton onClick={() => setPosterDialogOpen(false)}>
                            <CloseIcon />
                        </IconButton>
                    </Box>
                </DialogTitle>
                <DialogContent>
                    {selectedCampaign && (
                        <Box textAlign="center" py={2}>
                            <Typography variant="body2" color="textSecondary" gutterBottom>
                                Poster Preview
                            </Typography>
                            <Paper 
                                elevation={4} 
                                sx={{ 
                                    p: 2, 
                                    mb: 2, 
                                    display: 'inline-block',
                                    maxWidth: '100%'
                                }}
                            >
                                <img
                                    src={selectedCampaign.poster_url || '/posters/default_campaign.png'}
                                    alt={`${selectedCampaign.name} poster`}
                                    style={{
                                        maxWidth: '100%',
                                        height: 'auto',
                                        maxHeight: '500px',
                                        borderRadius: '8px'
                                    }}
                                    onError={(e) => {
                                        e.target.src = '/posters/default_campaign.png';
                                    }}
                                />
                            </Paper>
                            <Box display="flex" gap={2} justifyContent="center" mt={2}>
                                <Button
                                    variant="contained"
                                    startIcon={<DownloadIcon />}
                                    onClick={() => handleDownloadPoster(selectedCampaign)}
                                    color="success"
                                >
                                    Download Poster
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => setPosterDialogOpen(false)}
                                >
                                    Close
                                </Button>
                            </Box>
                            
                            {/* Campaign Details */}
                            <Box mt={3} p={2} bgcolor="grey.50" borderRadius={2}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Campaign Details
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">
                                            Type: {selectedCampaign.type || 'N/A'}
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">
                                            Status: {selectedCampaign.status}
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">
                                            Duration: {selectedCampaign.duration_days || 'N/A'} days
                                        </Typography>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <Typography variant="body2" color="textSecondary">
                                            Budget: {selectedCampaign.budget_range || 'N/A'}
                                        </Typography>
                                    </Grid>
                                    {selectedCampaign.special_offers && (
                                        <Grid item xs={12}>
                                            <Typography variant="body2" color="textSecondary">
                                                Special Offers: {selectedCampaign.special_offers}
                                            </Typography>
                                        </Grid>
                                    )}
                                    {selectedCampaign.call_to_action && (
                                        <Grid item xs={12}>
                                            <Typography variant="body2" color="textSecondary">
                                                Call to Action: {selectedCampaign.call_to_action}
                                            </Typography>
                                        </Grid>
                                    )}
                                </Grid>
                            </Box>
                        </Box>
                    )}
                </DialogContent>
            </Dialog>
        </Box>
    );
};

export default CampaignsPage;
