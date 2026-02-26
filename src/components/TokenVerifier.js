import React, { useState, useEffect } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Button,
    Box,
    Alert,
    Chip,
    Divider,
    Grid
} from '@mui/material';
import {
    VerifiedUser as VerifiedIcon,
    Error as ErrorIcon,
    Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const TokenVerifier = () => {
    const { verifyToken, token } = useAuth();
    const [tokenData, setTokenData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleVerifyToken = async () => {
        setLoading(true);
        setError('');
        
        const result = await verifyToken();
        
        if (result.success) {
            setTokenData(result.data);
        } else {
            setError(result.error);
        }
        
        setLoading(false);
    };

    const getRoleColor = (role) => {
        switch (role) {
            case 'super_admin':
                return 'error';
            case 'admin':
                return 'warning';
            case 'marketing_manager':
                return 'info';
            default:
                return 'default';
        }
    };

    useEffect(() => {
        // Auto-verify token when component mounts or token changes
        if (token) {
            handleVerifyToken();
        }
    }, [token]);

    return (
        <Box sx={{ maxWidth: 600, margin: 'auto', mt: 4 }}>
            <Card>
                <CardContent>
                    <Typography variant="h5" gutterBottom>
                        JWT Token Verification
                    </Typography>
                    
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                        Verify your JWT token and get decoded user information
                    </Typography>

                    {error && (
                        <Alert severity="error" sx={{ mb: 2 }}>
                            {error}
                        </Alert>
                    )}

                    {loading && (
                        <Box display="flex" justifyContent="center" sx={{ mb: 2 }}>
                            <RefreshIcon sx={{ animation: 'spin 1s linear infinite' }} />
                            <Typography variant="body2">Verifying token...</Typography>
                        </Box>
                    )}

                    {tokenData && (
                        <Box>
                            <Box display="flex" alignItems="center" mb={2}>
                                <VerifiedIcon color="success" sx={{ mr: 1 }} />
                                <Typography variant="h6" color="success.main">
                                    Token Verified Successfully
                                </Typography>
                            </Box>

                            <Divider sx={{ mb: 2 }} />

                            <Grid container spacing={2}>
                                <Grid item xs={12} sm={6}>
                                    <Typography variant="body2" color="textSecondary">
                                        Name
                                    </Typography>
                                    <Typography variant="body1" fontWeight="bold">
                                        {tokenData.name || 'N/A'}
                                    </Typography>
                                </Grid>

                                <Grid item xs={12} sm={6}>
                                    <Typography variant="body2" color="textSecondary">
                                        Company ID
                                    </Typography>
                                    <Typography variant="body1" fontWeight="bold">
                                        {tokenData.companyId || 'N/A'}
                                    </Typography>
                                </Grid>

                                <Grid item xs={12} sm={6}>
                                    <Typography variant="body2" color="textSecondary">
                                        Role
                                    </Typography>
                                    <Chip
                                        label={tokenData.roleName || 'N/A'}
                                        color={getRoleColor(tokenData.role)}
                                        size="small"
                                        sx={{ fontWeight: 'bold' }}
                                    />
                                </Grid>

                                <Grid item xs={12} sm={6}>
                                    <Typography variant="body2" color="textSecondary">
                                        Username
                                    </Typography>
                                    <Typography variant="body1" fontWeight="bold">
                                        {tokenData.username || 'N/A'}
                                    </Typography>
                                </Grid>

                                <Grid item xs={12} sm={6}>
                                    <Typography variant="body2" color="textSecondary">
                                        Email
                                    </Typography>
                                    <Typography variant="body1" fontWeight="bold">
                                        {tokenData.email || 'N/A'}
                                    </Typography>
                                </Grid>

                                <Grid item xs={12} sm={6}>
                                    <Typography variant="body2" color="textSecondary">
                                        Account Status
                                    </Typography>
                                    <Chip
                                        label={tokenData.activitystatus ? 'Active' : 'Inactive'}
                                        color={tokenData.activitystatus ? 'success' : 'error'}
                                        size="small"
                                    />
                                </Grid>
                            </Grid>

                            {tokenData.permissions && (
                                <Box mt={3}>
                                    <Typography variant="h6" gutterBottom>
                                        Role Permissions
                                    </Typography>
                                    
                                    {Object.entries(tokenData.permissions).map(([module, permissions]) => (
                                        <Card key={module} sx={{ mb: 2 }}>
                                            <CardContent>
                                                <Typography variant="subtitle1" gutterBottom>
                                                    {module.charAt(0).toUpperCase() + module.slice(1)}
                                                </Typography>
                                                
                                                <Grid container spacing={1}>
                                                    {Object.entries(permissions).map(([action, allowed]) => (
                                                        <Grid item xs={6} sm={3}>
                                                            <Typography variant="body2" color="textSecondary">
                                                                {action}
                                                            </Typography>
                                                            <Chip
                                                                label={allowed ? 'Allowed' : 'Denied'}
                                                                color={allowed ? 'success' : 'error'}
                                                                size="small"
                                                            />
                                                        </Grid>
                                                    ))}
                                                </Grid>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </Box>
                            )}

                            <Box mt={3}>
                                <Button
                                    variant="contained"
                                    startIcon={<RefreshIcon />}
                                    onClick={handleVerifyToken}
                                    disabled={loading}
                                    fullWidth
                                >
                                    {loading ? 'Verifying...' : 'Verify Token'}
                                </Button>
                            </Box>
                        </Box>
                    )}
                </CardContent>
            </Card>
        </Box>
    );
};

export default TokenVerifier;
