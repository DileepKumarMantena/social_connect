import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Box,
    Grid,
    Avatar,
    Tooltip,
    Card,
    CardMedia,
    ButtonGroup
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Upload as UploadIcon,
    Business as BusinessIcon,
    SmartToy as BotIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';
import CompanyChatBot from '../components/ChatBot/CompanyChatBot';

const CompaniesPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingCompany, setEditingCompany] = useState(null);
    const [chatBotOpen, setChatBotOpen] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        logo_url: ''
    });

    // Check if user has permission
    const checkPermission = (action) => {
        if (user?.role !== 'super_admin') {
            Swal.fire({
                icon: 'error',
                title: 'Access Denied',
                text: 'Only super admins can access company management.',
                confirmButtonColor: '#3085d6',
            });
            return false;
        }
        return true;
    };

    const fetchCompanies = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/companies`,
                { headers: getAuthHeaders() }
            );
            
            setCompanies(response.data.companies || []);
            setError('');
        } catch (error) {
            console.error('Error fetching companies:', error);
            setError('Failed to fetch companies');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateCompany = () => {
        if (!checkPermission('create')) return;
        setEditingCompany(null);
        setFormData({
            name: '',
            description: '',
            logo_url: ''
        });
        setOpenDialog(true);
    };

    const handleEditCompany = (company) => {
        if (!checkPermission('edit')) return;
        setEditingCompany(company);
        setFormData({
            name: company.name || '',
            description: company.description || '',
            logo_url: company.logo_url || ''
        });
        setOpenDialog(true);
    };

    const handleCreateWithChatBot = () => {
        if (!checkPermission('create')) return;
        setChatBotOpen(true);
    };

    const handleCompanyCreated = (newCompany) => {
        // Add the new company to the companies list
        setCompanies(prev => [...prev, newCompany]);
        setChatBotOpen(false);
        Swal.fire({
            icon: 'success',
            title: 'Company Created!',
            text: 'Your company has been created successfully with AI assistance.',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'Great!'
        });
    };

    const handleDeleteCompany = async (company) => {
        if (!checkPermission('delete')) return;
        
        const result = await Swal.fire({
            title: 'Delete Company',
            text: `Are you sure you want to delete ${company.name}?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete!'
        });

        if (result.isConfirmed) {
            try {
                await axios.delete(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/companies/${company.id}`,
                    { headers: getAuthHeaders() }
                );
                
                setCompanies(companies.filter(c => c.id !== company.id));
                Swal.fire('Deleted!', 'Company has been deleted.', 'success');
            } catch (error) {
                console.error('Error deleting company:', error);
                Swal.fire('Error', 'Failed to delete company', 'error');
            }
        }
    };

    const handleSaveCompany = async () => {
        try {
            if (editingCompany) {
                // Update existing company
                await axios.put(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/companies/${editingCompany.id}`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                
                setCompanies(companies.map(c => 
                    c.id === editingCompany.id ? { ...c, ...formData } : c
                ));
            } else {
                // Create new company
                await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/companies`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                
                setCompanies([...companies, { ...formData, id: Date.now() }]);
            }
            
            setOpenDialog(false);
            setEditingCompany(null);
            setFormData({
                name: '',
                description: '',
                logo_url: ''
            });
            
            Swal.fire(
                'Success!',
                `Company ${editingCompany ? 'updated' : 'created'} successfully.`,
                'success'
            );
        } catch (error) {
            console.error('Error saving company:', error);
            Swal.fire('Error', 'Failed to save company', 'error');
        }
    };

    const handleLogoUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Check file type
        if (!file.type.startsWith('image/')) {
            Swal.fire('Error', 'Please upload an image file', 'error');
            return;
        }

        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            Swal.fire('Error', 'File size must be less than 5MB', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/upload/logo`,
                formData,
                {
                    headers: {
                        ...getAuthHeaders(),
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            // Update form with logo URL
            setFormData(prev => ({
                ...prev,
                logo_url: response.data.logo_url
            }));

            Swal.fire('Success!', 'Logo uploaded successfully', 'success');
        } catch (error) {
            console.error('Error uploading logo:', error);
            Swal.fire('Error', 'Failed to upload logo', 'error');
        }
    };

    useEffect(() => {
        fetchCompanies();
    }, []);

    if (user?.role !== 'super_admin') {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Access Denied
                    </Typography>
                    <Typography color="textSecondary">
                        You don't have permission to access company management.
                    </Typography>
                </Paper>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
                Company Management
            </Typography>
            
            <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
                <ButtonGroup variant="contained" size="medium">
                    <Button
                        startIcon={<AddIcon />}
                        onClick={handleCreateCompany}
                    >
                        Create Company
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

            <Paper sx={{ p: 2 }}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Logo</TableCell>
                                <TableCell>Company Name</TableCell>
                                <TableCell>Description</TableCell>
                                <TableCell>Created By</TableCell>
                                <TableCell>Created At</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={5} align="center">
                                        Loading...
                                    </TableCell>
                                </TableRow>
                            ) : error ? (
                                <TableRow>
                                    <TableCell colSpan={5} align="center">
                                        <Typography color="error">{error}</Typography>
                                    </TableCell>
                                </TableRow>
                            ) : (
                                companies.map((company) => (
                                    <TableRow key={company.id}>
                                        <TableCell>
                                            {company.logo_url ? (
                                                <Avatar 
                                                    src={company.logo_url}
                                                    variant="rounded"
                                                    sx={{ width: 50, height: 50 }}
                                                />
                                            ) : (
                                                <Avatar sx={{ bgcolor: 'primary.main' }}>
                                                    <BusinessIcon />
                                                </Avatar>
                                            )}
                                        </TableCell>
                                        <TableCell>{company.name}</TableCell>
                                        <TableCell>{company.description || 'No description'}</TableCell>
                                        <TableCell>{company.created_by}</TableCell>
                                        <TableCell>
                                            {new Date(company.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>
                                            <Tooltip title="Edit Company">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleEditCompany(company)}
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Delete Company">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleDeleteCompany(company)}
                                                    color="error"
                                                >
                                                    <DeleteIcon />
                                                </IconButton>
                                            </Tooltip>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>

            {/* Company Create/Edit Dialog */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
                <DialogTitle>
                    {editingCompany ? 'Edit Company' : 'Create Company'}
                </DialogTitle>
                <DialogContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Company Name"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                margin="normal"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Description"
                                multiline
                                rows={3}
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                margin="normal"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Box sx={{ textAlign: 'center', mb: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Company Logo
                                </Typography>
                                {formData.logo_url ? (
                                    <Card sx={{ maxWidth: 200, mb: 2 }}>
                                        <CardMedia
                                            component="img"
                                            height="140"
                                            image={formData.logo_url}
                                            alt="Company logo"
                                        />
                                    </Card>
                                ) : (
                                    <Box 
                                        sx={{ 
                                            border: '2px dashed #ccc', 
                                            borderRadius: 1, 
                                            p: 2, 
                                            textAlign: 'center',
                                            bgcolor: 'grey.50'
                                        }}
                                    >
                                        <UploadIcon sx={{ fontSize: 48, color: 'grey.400' }} />
                                        <Typography variant="body2" sx={{ mt: 1 }}>
                                            Click to upload logo
                                        </Typography>
                                    </Box>
                                )}
                            </Box>
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleLogoUpload}
                                style={{ display: 'none' }}
                                id="logo-upload-input"
                            />
                        </Grid>
                    </Grid>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpenDialog(false)}>
                        Cancel
                    </Button>
                    <Button 
                        type="submit" 
                        variant="contained" 
                        onClick={handleSaveCompany}
                        color="primary"
                    >
                        {editingCompany ? 'Update' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>
            
            <CompanyChatBot 
                open={chatBotOpen} 
                onClose={() => setChatBotOpen(false)}
                onCompanyCreated={handleCompanyCreated}
            />
        </Container>
    );
};

export default CompaniesPage;
