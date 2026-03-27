import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    TextField,
    Button,
    Grid,
    CircularProgress,
    Alert,
    Avatar,
    Divider,
    Chip,
    IconButton
} from '@mui/material';
import {
    Person as PersonIcon,
    Email as EmailIcon,
    Business as BusinessIcon,
    Edit as EditIcon,
    Save as SaveIcon,
    PhotoCamera as CameraIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';

const ProfilePage = () => {
    const { user, getAuthHeaders } = useAuth();
    const [loading, setLoading] = useState(false);
    const [editing, setEditing] = useState(false);
    const [profileImage, setProfileImage] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        username: '',
        companyid: '',
        role: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        if (user) {
            setFormData({
                name: user.name || '',
                email: user.email || '',
                username: user.username || '',
                companyid: user.companyid || '',
                role: user.role || ''
            });
            setProfileImage(user.profileImage || null);
        }
    }, [user]);

    const handleImageUpload = (event) => {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) { // 5MB limit
                Swal.fire({
                    icon: 'error',
                    title: 'File Too Large',
                    text: 'Profile image must be less than 5MB',
                    confirmButtonColor: '#d33'
                });
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                setProfileImage(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleImageChange = () => {
        setEditing(true);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleEdit = () => {
        setEditing(true);
        setError('');
    };

    const handleCancel = () => {
        setEditing(false);
        // Reset form to original user data
        if (user) {
            setFormData({
                name: user.name || '',
                email: user.email || '',
                username: user.username || '',
                companyid: user.companyid || '',
                role: user.role || ''
            });
        }
        setError('');
    };

    const handleSave = async () => {
        setLoading(true);
        setError('');

        try {
            const response = await axios.put(
                `${process.env.REACT_APP_API_LINKS}/api/v1/user/profile`,
                {
                    name: formData.name,
                    email: formData.email
                },
                { headers: getAuthHeaders() }
            );

            if (response.data) {
                // Update user context if needed
                setEditing(false);
                Swal.fire({
                    icon: 'success',
                    title: 'Profile Updated!',
                    text: 'Your profile has been updated successfully.',
                    confirmButtonColor: '#3085d6'
                });
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            const errorMessage = error.response?.data?.detail || 'Failed to update profile';
            setError(errorMessage);
            Swal.fire({
                icon: 'error',
                title: 'Update Failed',
                text: errorMessage,
                confirmButtonColor: '#d33'
            });
        } finally {
            setLoading(false);
        }
    };

    const getRoleColor = (role) => {
        switch (role) {
            case 'super_admin':
                return 'error';
            case 'admin':
                return 'warning';
            case 'user':
                return 'primary';
            default:
                return 'default';
        }
    };

    if (!user) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Typography variant="h4" component="h1" gutterBottom>
                Profile
            </Typography>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Card>
                <CardContent>
                    <Box display="flex" alignItems="center" mb={3}>
                        <Box sx={{ position: 'relative' }}>
                            <input
                                type="file"
                                accept="image/*"
                                style={{ display: 'none' }}
                                id="profile-image-upload"
                                onChange={handleImageUpload}
                            />
                            <Avatar
                                src={profileImage || user?.profileImage}
                                sx={{
                                    width: 80,
                                    height: 80,
                                    bgcolor: 'primary.main',
                                    mr: 3,
                                    cursor: editing ? 'default' : 'pointer'
                                }}
                                onClick={handleImageChange}
                            >
                                {profileImage || user?.profileImage ? (
                                    <img src={profileImage || user?.profileImage} alt="Profile" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                ) : (
                                    <PersonIcon sx={{ fontSize: 40 }} />
                                )}
                            </Avatar>
                            {editing && (
                                <IconButton
                                    sx={{
                                        position: 'absolute',
                                        bottom: 0,
                                        right: 0,
                                        bgcolor: 'secondary.main',
                                        color: 'white',
                                        width: 32,
                                        height: 32
                                    }}
                                    component="label"
                                    htmlFor="profile-image-upload"
                                >
                                    <CameraIcon />
                                </IconButton>
                            )}
                        </Box>
                        <Box ml={2}>
                            <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                {user.name}
                            </Typography>
                            <Chip
                                label={user.role?.replace('_', ' ').toUpperCase()}
                                color={getRoleColor(user.role)}
                                size="small"
                                sx={{ ml: 1 }}
                            />
                        </Box>
                    </Box>

                    <Divider sx={{ mb: 3 }} />

                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Username"
                                name="username"
                                value={formData.username}
                                disabled
                                helperText="Username cannot be changed"
                                InputProps={{
                                    startAdornment: <PersonIcon sx={{ mr: 1, color: 'action.active' }} />
                                }}
                            />
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Role"
                                name="role"
                                value={formData.role?.replace('_', ' ').toUpperCase()}
                                disabled
                                helperText="Role is assigned by administrator"
                                InputProps={{
                                    startAdornment: <BusinessIcon sx={{ mr: 1, color: 'action.active' }} />
                                }}
                            />
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Name"
                                name="name"
                                value={formData.name}
                                onChange={handleInputChange}
                                disabled={!editing}
                                helperText={editing ? "Edit your name" : "Click edit to modify"}
                                InputProps={{
                                    startAdornment: <PersonIcon sx={{ mr: 1, color: 'action.active' }} />
                                }}
                            />
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Email"
                                name="email"
                                value={formData.email}
                                onChange={handleInputChange}
                                disabled={!editing}
                                helperText={editing ? "Edit your email" : "Click edit to modify"}
                                InputProps={{
                                    startAdornment: <EmailIcon sx={{ mr: 1, color: 'action.active' }} />
                                }}
                            />
                        </Grid>

                        <Grid item xs={12} md={6}>
                            <TextField
                                fullWidth
                                label="Company ID"
                                name="companyid"
                                value={formData.companyid}
                                disabled
                                helperText="Company is assigned by administrator"
                                InputProps={{
                                    startAdornment: <BusinessIcon sx={{ mr: 1, color: 'action.active' }} />
                                }}
                            />
                        </Grid>
                    </Grid>

                    <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                        {!editing ? (
                            <Button
                                variant="contained"
                                startIcon={<EditIcon />}
                                onClick={handleEdit}
                                color="primary"
                            >
                                Edit Profile
                            </Button>
                        ) : (
                            <>
                                <Button
                                    variant="outlined"
                                    onClick={handleCancel}
                                    disabled={loading}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    variant="contained"
                                    startIcon={<SaveIcon />}
                                    onClick={handleSave}
                                    disabled={loading}
                                    color="success"
                                >
                                    {loading ? <CircularProgress size={20} /> : 'Save Changes'}
                                </Button>
                            </>
                        )}
                    </Box>
                </CardContent>
            </Card>
        </Box>
    );
};

export default ProfilePage;
