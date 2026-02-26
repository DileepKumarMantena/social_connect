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
    TextField,
    InputAdornment
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Search as SearchIcon,
    Person as PersonIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const LeadsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [leads, setLeads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchLeads();
    }, []);

    const fetchLeads = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/leads`,
                { headers: getAuthHeaders() }
            );
            setLeads(response.data.leads || []);
            setError('');
        } catch (error) {
            console.error('Error fetching leads:', error);
            setError('Failed to fetch leads');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'new':
                return 'info';
            case 'contacted':
                return 'warning';
            case 'converted':
                return 'success';
            default:
                return 'default';
        }
    };

    const handleCreateLead = () => {
        // TODO: Implement create lead dialog
        console.log('Create lead');
    };

    const handleEditLead = (lead) => {
        // TODO: Implement edit lead dialog
        console.log('Edit lead:', lead);
    };

    const handleDeleteLead = (lead) => {
        // TODO: Implement delete lead confirmation
        console.log('Delete lead:', lead);
    };

    const filteredLeads = leads.filter(lead =>
        lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

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
                    Leads
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreateLead}
                >
                    Add Lead
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
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                                <Typography variant="h6">
                                    Lead List
                                </Typography>
                                <TextField
                                    size="small"
                                    placeholder="Search leads..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    InputProps={{
                                        startAdornment: (
                                            <InputAdornment position="start">
                                                <SearchIcon />
                                            </InputAdornment>
                                        ),
                                    }}
                                />
                            </Box>
                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Name</TableCell>
                                            <TableCell>Email</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Campaign ID</TableCell>
                                            <TableCell>Created By</TableCell>
                                            <TableCell>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {filteredLeads.map((lead) => (
                                            <TableRow key={lead.id}>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center">
                                                        <PersonIcon sx={{ mr: 1, fontSize: 20 }} />
                                                        {lead.name}
                                                    </Box>
                                                </TableCell>
                                                <TableCell>{lead.email}</TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={lead.status}
                                                        color={getStatusColor(lead.status)}
                                                        size="small"
                                                    />
                                                </TableCell>
                                                <TableCell>{lead.campaign_id}</TableCell>
                                                <TableCell>{lead.created_by || 'Unknown'}</TableCell>
                                                <TableCell>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleEditLead(lead)}
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleDeleteLead(lead)}
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
                                Lead Summary
                            </Typography>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Total Leads
                                </Typography>
                                <Typography variant="h4">
                                    {leads.length}
                                </Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    New Leads
                                </Typography>
                                <Typography variant="h4">
                                    {leads.filter(l => l.status === 'new').length}
                                </Typography>
                            </Box>
                            <Box mb={2}>
                                <Typography variant="body2" color="textSecondary">
                                    Contacted
                                </Typography>
                                <Typography variant="h4">
                                    {leads.filter(l => l.status === 'contacted').length}
                                </Typography>
                            </Box>
                            <Box>
                                <Typography variant="body2" color="textSecondary">
                                    Converted
                                </Typography>
                                <Typography variant="h4">
                                    {leads.filter(l => l.status === 'converted').length}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default LeadsPage;
