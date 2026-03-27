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
    InputAdornment,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Search as SearchIcon,
    Person as PersonIcon,
    Download as DownloadIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';

const LeadsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [leads, setLeads] = useState([]);
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingLead, setEditingLead] = useState(null);

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
        email: '',
        phone: '',
        campaign_id: '',
        status: 'new'
    });

    useEffect(() => {
        fetchLeads();
        fetchCampaigns();
    }, []);

    const fetchCampaigns = async () => {
        try {
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/campaigns`,
                { headers: getAuthHeaders() }
            );
            setCampaigns(response.data.campaigns || []);
        } catch (error) {
            console.error('Error fetching campaigns:', error);
        }
    };

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
            // Ensure error is a string, not an object
            const errorMessage = typeof error === 'string' ? error : 
                              error.response?.data?.message || 
                              error.message || 
                              'Failed to fetch leads';
            setError(errorMessage);
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
        if (!checkPermission('create')) return;
        setOpenDialog(true);
    };

    const handleExportCSV = async () => {
        if (!checkPermission('view')) return;
        
        try {
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/ai/export/leads/csv`,
                { 
                    headers: getAuthHeaders(),
                    responseType: 'blob'
                }
            );
            
            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `leads_export_${new Date().toISOString().slice(0,10)}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            
            Swal.fire({
                icon: 'success',
                title: 'Export Successful!',
                text: 'Leads exported to CSV successfully',
                confirmButtonColor: '#3085d6'
            });
        } catch (error) {
            console.error('Error exporting leads:', error);
            Swal.fire({
                icon: 'error',
                title: 'Export Failed',
                text: 'Failed to export leads to CSV',
                confirmButtonColor: '#d33'
            });
        }
    };

    const handleSaveLead = async () => {
        try {
            if (editingLead) {
                // Update existing lead
                const response = await axios.put(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/leads/${editingLead.id}`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                // Update the lead in the leads array
                setLeads(leads.map(l => 
                    l.id === editingLead.id ? response.data.lead : l
                ));
                // Refresh leads to ensure data consistency
                await fetchLeads();
            } else {
                // Create new lead
                const response = await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/leads`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                // Add the new lead to the leads array using functional update
                setLeads(prevLeads => {
                    const newLeads = [...prevLeads, response.data.lead];
                    console.log('Updated leads array:', newLeads);
                    console.log('New lead added:', response.data.lead);
                    return newLeads;
                });
                // Refresh leads to ensure data consistency
                await fetchLeads();
            }
            setOpenDialog(false);
            setEditingLead(null);
            setFormData({ name: '', email: '', phone: '', campaign_id: '', status: 'new' });
            console.log(`Lead ${editingLead ? 'updated' : 'created'}:`, editingLead ? formData : formData);
        } catch (error) {
            console.error(`Error ${editingLead ? 'updating' : 'creating'} lead:`, error);
            const errorMessage = error.response?.data?.message || error.message || `Failed to ${editingLead ? 'update' : 'create'} lead`;
            setError(errorMessage);
        }
    };

    const handleEditLead = (lead) => {
        if (!checkPermission('edit')) return;
        setEditingLead(lead);
        setFormData({
            name: lead.name,
            email: lead.email,
            phone: lead.phone,
            campaign_id: lead.campaign_id,
            status: lead.status
        });
        setOpenDialog(true);
    };

    const handleDeleteLead = async (lead) => {
        if (!checkPermission('delete')) return;
        if (window.confirm(`Are you sure you want to delete "${lead.name}"?`)) {
            try {
                await axios.delete(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/leads/${lead.id}`,
                    { headers: getAuthHeaders() }
                );
                // Remove the lead from the leads array
                setLeads(leads.filter(l => l.id !== lead.id));
                // Refresh leads to ensure data consistency
                await fetchLeads();
                console.log('Lead deleted successfully');
            } catch (error) {
                console.error('Error deleting lead:', error);
                // Refresh leads to ensure data consistency
                await fetchLeads();
            }
        }
    };

    const handleStatusChange = async (lead, newStatus) => {
        try {
            const response = await axios.put(
                `${process.env.REACT_APP_API_LINKS}/api/v1/leads/${lead.id}`,
                { status: newStatus },
                { headers: getAuthHeaders() }
            );
            // Update the lead in the leads array
            setLeads(leads.map(l => 
                l.id === lead.id ? { ...l, status: newStatus } : l
            ));
            console.log('Lead status updated successfully');
        } catch (error) {
            console.error('Error updating lead status:', error);
        }
    };

    // Filter leads based on search term
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

    if (error) {
        return (
            <Alert severity="error" sx={{ mb: 2 }}>
                {error}
            </Alert>
        );
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1">
                    Leads
                </Typography>
                <Box sx={{ display: 'flex', gap: 2 }}>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={handleCreateLead}
                    >
                        Add Lead
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<DownloadIcon />}
                        onClick={handleExportCSV}
                        color="success"
                    >
                        Export CSV
                    </Button>
                </Box>
            </Box>

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
                                                    <FormControl size="small" sx={{ minWidth: 120 }}>
                                                        <Select
                                                            value={lead.status}
                                                            onChange={(e) => handleStatusChange(lead, e.target.value)}
                                                            size="small"
                                                        >
                                                            <MenuItem value="new">New</MenuItem>
                                                            <MenuItem value="contacted">Contacted</MenuItem>
                                                            <MenuItem value="converted">Converted</MenuItem>
                                                        </Select>
                                                    </FormControl>
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
                            {/* Debug info - remove later */}
                            <Box mt={2} p={1} bgcolor="grey.100">
                                <Typography variant="caption" color="textSecondary">
                                    Debug: Total leads in state: {leads.length}
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Create Lead Dialog */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>{editingLead ? 'Edit Lead' : 'Create New Lead'}</DialogTitle>
                <form onSubmit={(e) => { e.preventDefault(); handleSaveLead(); }}>
                    <DialogContent>
                        <TextField
                            fullWidth
                            label="Name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            margin="normal"
                            required
                        />
                        <TextField
                            fullWidth
                            label="Email"
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            margin="normal"
                            required
                        />
                        <TextField
                            fullWidth
                            label="Phone"
                            value={formData.phone}
                            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                            margin="normal"
                        />
                        <FormControl fullWidth margin="normal">
                            <InputLabel id="campaign-select-label">Campaign</InputLabel>
                            <Select
                                labelId="campaign-select-label"
                                value={formData.campaign_id}
                                onChange={(e) => setFormData({ ...formData, campaign_id: e.target.value })}
                                label="Campaign"
                            >
                                <MenuItem value="">
                                    <em>None</em>
                                </MenuItem>
                                {campaigns.map((campaign) => (
                                    <MenuItem key={campaign.id} value={campaign.id}>
                                        {campaign.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={() => {
                            setOpenDialog(false);
                            setEditingLead(null);
                            setFormData({ name: '', email: '', phone: '', campaign_id: '', status: 'new' });
                        }}>Cancel</Button>
                        <Button type="submit" variant="contained">
                            {editingLead ? 'Update Lead' : 'Create Lead'}
                        </Button>
                    </DialogActions>
                </form>
            </Dialog>
        </Box>
    );
};

export default LeadsPage;
