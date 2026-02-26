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
    Alert
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Visibility as VisibilityIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const CampaignsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

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
        // TODO: Implement create campaign dialog
        console.log('Create campaign');
    };

    const handleEditCampaign = (campaign) => {
        // TODO: Implement edit campaign dialog
        console.log('Edit campaign:', campaign);
    };

    const handleDeleteCampaign = (campaign) => {
        // TODO: Implement delete campaign confirmation
        console.log('Delete campaign:', campaign);
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
        </Box>
    );
};

export default CampaignsPage;
