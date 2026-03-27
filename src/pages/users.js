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
    Chip,
    Box,
    Grid,
    Avatar,
    Tooltip,
    ButtonGroup
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Download as DownloadIcon,
    Upload as UploadIcon,
    Business as BusinessIcon,
    SmartToy as BotIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';
import UserChatBot from '../components/ChatBot/UserChatBot';

const UsersPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [chatBotOpen, setChatBotOpen] = useState(false);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        name: '',
        role: 'user',
        companyid: ''
    });

    // Check if user has permission
    const checkPermission = (action) => {
        if (user?.role !== 'super_admin') {
            Swal.fire({
                icon: 'error',
                title: 'Access Denied',
                text: 'Only super admins can access user management.',
                confirmButtonColor: '#3085d6',
            });
            return false;
        }
        return true;
    };

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/users`,
                { headers: getAuthHeaders() }
            );
            
            setUsers(response.data.users || []);
            setError('');
        } catch (error) {
            console.error('Error fetching users:', error);
            setError('Failed to fetch users');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = () => {
        if (!checkPermission('create')) return;
        setEditingUser(null);
        setFormData({
            username: '',
            email: '',
            name: '',
            role: 'user',
            companyid: ''
        });
        setOpenDialog(true);
    };

    const handleEditUser = (user) => {
        if (!checkPermission('edit')) return;
        setEditingUser(user);
        setFormData({
            username: user.username || '',
            email: user.email || '',
            name: user.name || '',
            role: user.role || 'user',
            companyid: user.companyid || ''
        });
        setOpenDialog(true);
    };

    const handleCreateWithChatBot = () => {
        if (!checkPermission('create')) return;
        setChatBotOpen(true);
    };

    const handleUserCreated = (newUser) => {
        // Add the new user to the users list
        setUsers(prev => [...prev, newUser]);
        setChatBotOpen(false);
        Swal.fire({
            icon: 'success',
            title: 'User Created!',
            text: 'Your user has been created successfully with AI assistance.',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'Great!'
        });
    };

    const handleDeleteUser = async (user) => {
        if (!checkPermission('delete')) return;
        
        const result = await Swal.fire({
            title: 'Delete User',
            text: `Are you sure you want to delete ${user.name}?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Yes, delete!'
        });

        if (result.isConfirmed) {
            try {
                await axios.delete(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/users/${user.id}`,
                    { headers: getAuthHeaders() }
                );
                
                setUsers(users.filter(u => u.id !== user.id));
                Swal.fire('Deleted!', 'User has been deleted.', 'success');
            } catch (error) {
                console.error('Error deleting user:', error);
                Swal.fire('Error', 'Failed to delete user', 'error');
            }
        }
    };

    const handleSaveUser = async () => {
        try {
            if (editingUser) {
                // Update existing user
                await axios.put(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/users/${editingUser.id}`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                
                setUsers(users.map(u => 
                    u.id === editingUser.id ? { ...u, ...formData } : u
                ));
            } else {
                // Create new user
                await axios.post(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/users`,
                    formData,
                    { headers: getAuthHeaders() }
                );
                
                setUsers([...users, { ...formData, id: Date.now() }]);
            }
            
            setOpenDialog(false);
            setEditingUser(null);
            setFormData({
                username: '',
                email: '',
                name: '',
                role: 'user',
                companyid: ''
            });
            
            Swal.fire(
                'Success!',
                `User ${editingUser ? 'updated' : 'created'} successfully.`,
                'success'
            );
        } catch (error) {
            console.error('Error saving user:', error);
            Swal.fire('Error', 'Failed to save user', 'error');
        }
    };

    const handleExportUsers = async () => {
        if (!checkPermission('export')) return;
        
        try {
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/users/export`,
                { 
                    headers: getAuthHeaders(),
                    responseType: 'blob'
                }
            );
            
            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.download = 'users_export.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
            
            Swal.fire('Exported!', 'Users data exported successfully.', 'success');
        } catch (error) {
            console.error('Error exporting users:', error);
            Swal.fire('Error', 'Failed to export users', 'error');
        }
    };

    const getRoleColor = (role) => {
        switch (role) {
            case 'super_admin':
                return 'error';
            case 'admin':
                return 'warning';
            case 'user':
                return 'success';
            default:
                return 'default';
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    if (user?.role !== 'super_admin') {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        Access Denied
                    </Typography>
                    <Typography color="textSecondary">
                        You don't have permission to access user management.
                    </Typography>
                </Paper>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Typography variant="h4" gutterBottom>
                User Management
            </Typography>
            
            <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
                <ButtonGroup variant="contained" size="medium">
                    <Button
                        startIcon={<AddIcon />}
                        onClick={handleCreateUser}
                    >
                        Create User
                    </Button>
                    <Button
                        startIcon={<BotIcon />}
                        onClick={handleCreateWithChatBot}
                        color="secondary"
                    >
                        AI Assistant
                    </Button>
                </ButtonGroup>
                <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleExportUsers}
                >
                    Export CSV
                </Button>
            </Box>

            <Paper sx={{ p: 2 }}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Avatar</TableCell>
                                <TableCell>Username</TableCell>
                                <TableCell>Name</TableCell>
                                <TableCell>Email</TableCell>
                                <TableCell>Role</TableCell>
                                <TableCell>Company</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Actions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {loading ? (
                                <TableRow>
                                    <TableCell colSpan={7} align="center">
                                        Loading...
                                    </TableCell>
                                </TableRow>
                            ) : error ? (
                                <TableRow>
                                    <TableCell colSpan={7} align="center">
                                        <Typography color="error">{error}</Typography>
                                    </TableCell>
                                </TableRow>
                            ) : (
                                users.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell>
                                            <Avatar sx={{ bgcolor: getRoleColor(user.role) }}>
                                                {user.name?.charAt(0)?.toUpperCase() || user.username?.charAt(0)?.toUpperCase() || 'U'}
                                            </Avatar>
                                        </TableCell>
                                        <TableCell>{user.username}</TableCell>
                                        <TableCell>{user.name}</TableCell>
                                        <TableCell>{user.email}</TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.role} 
                                                color={getRoleColor(user.role)}
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>{user.companyid || 'N/A'}</TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.activitystatus || 'active'} 
                                                color={user.activitystatus === 'active' ? 'success' : 'default'}
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Tooltip title="Edit User">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleEditUser(user)}
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                            </Tooltip>
                                            <Tooltip title="Delete User">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleDeleteUser(user)}
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

            {/* User Create/Edit Dialog */}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {editingUser ? 'Edit User' : 'Create User'}
                </DialogTitle>
                <DialogContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Username"
                                value={formData.username}
                                onChange={(e) => setFormData({...formData, username: e.target.value})}
                                margin="normal"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Email"
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({...formData, email: e.target.value})}
                                margin="normal"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                fullWidth
                                label="Name"
                                value={formData.name}
                                onChange={(e) => setFormData({...formData, name: e.target.value})}
                                margin="normal"
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <FormControl fullWidth margin="normal">
                                <InputLabel>Role</InputLabel>
                                <Select
                                    value={formData.role}
                                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                                    label="Role"
                                >
                                    <MenuItem value="user">User</MenuItem>
                                    <MenuItem value="admin">Admin</MenuItem>
                                    <MenuItem value="super_admin">Super Admin</MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                fullWidth
                                label="Company ID"
                                value={formData.companyid}
                                onChange={(e) => setFormData({...formData, companyid: e.target.value})}
                                margin="normal"
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <FormControl fullWidth margin="normal">
                                <InputLabel>Status</InputLabel>
                                <Select
                                    value={formData.activitystatus}
                                    onChange={(e) => setFormData({...formData, activitystatus: e.target.value})}
                                    label="Status"
                                >
                                    <MenuItem value="active">Active</MenuItem>
                                    <MenuItem value="inactive">Inactive</MenuItem>
                                </Select>
                            </FormControl>
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
                        onClick={handleSaveUser}
                        color="primary"
                    >
                        {editingUser ? 'Update' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>
            
            <UserChatBot 
                open={chatBotOpen} 
                onClose={() => setChatBotOpen(false)}
                onUserCreated={handleUserCreated}
            />
        </Container>
    );
};

export default UsersPage;
