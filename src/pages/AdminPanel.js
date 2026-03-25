import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  Checkbox,
  ListItemText,
  FormControlLabel,
  Switch
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  AccessTime as AccessTimeIcon,
  Business as BusinessIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Restore as RestoreIcon
} from '@mui/icons-material';
import refreshService from '../services/refreshService';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import Swal from 'sweetalert2';

const AdminPanel = () => {
  const { getAuthHeaders, hasRole, user } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [rolesLoading, setRolesLoading] = useState(true);
  const [companies, setCompanies] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [showInactiveUsers, setShowInactiveUsers] = useState(false);
  const [selectedCompanyId, setSelectedCompanyId] = useState(user?.companyid || 1); // Default to user's company
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    role: '', // Will be set when roles are loaded
    companyid: user?.companyid || 1,
    access_hours: 24
  });
  
  // Update company ID when selection changes
  useEffect(() => {
    setFormData(prev => ({ ...prev, companyid: selectedCompanyId }));
  }, [selectedCompanyId]);
  
  // Update company ID when user changes
  useEffect(() => {
    if (user?.companyid) {
      setFormData(prev => ({ ...prev, companyid: user.companyid }));
    }
  }, [user]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Fetch available roles from role management
  const fetchRoles = useCallback(async () => {
    try {
      setRolesLoading(true);
      const response = await axios.get(
        `${process.env.REACT_APP_API_LINKS}/api/v1/admin/roles`,
        { headers: getAuthHeaders() }
      );
      console.log('Roles response:', response.data);
      const rolesData = response.data?.data?.roles || response.data?.roles || {};
      console.log('Parsed rolesData:', rolesData);
      
      // Extract role keys from the roles object
      const roleKeys = Object.keys(rolesData);
      
      // Always include basic roles for compatibility
      const allRoles = [...new Set([...roleKeys, 'user', 'admin'])];
      setAvailableRoles(allRoles);
      
      // Set default role to first available role if none selected
      if (allRoles.length > 0 && !formData.role) {
        setFormData(prev => ({ ...prev, role: allRoles[0] }));
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
      // Fallback to basic roles if role management fails
      const fallbackRoles = ['user', 'admin', 'marketing_manager', 'content_editor', 'sales_manager'];
      setAvailableRoles(fallbackRoles);
      if (!formData.role) {
        setFormData(prev => ({ ...prev, role: 'user' }));
      }
    } finally {
      setRolesLoading(false);
    }
  }, [getAuthHeaders, formData.role]);

  // Fetch companies from API
  const fetchCompanies = useCallback(async () => {
    try {
      // Add cache-busting to force fresh data
      const timestamp = new Date().getTime();
      const random = Math.random().toString(36).substring(7);
      const response = await axios.get(
        `${process.env.REACT_APP_API_LINKS}/api/v1/admin/companies/accessible?t=${timestamp}&r=${random}`,
        { headers: getAuthHeaders() }
      );
      console.log('Companies response:', response.data);
      const companiesData = response.data?.companies || [];
      setCompanies(companiesData);
    } catch (error) {
      console.error('Error fetching companies:', error);
      // Don't use fallback - empty array if API fails
      setCompanies([]);
    }
  }, [getAuthHeaders]);

  // Fetch users
  const fetchUsers = useCallback(async () => {
    try {
      const includeInactive = showInactiveUsers ? '&include_inactive=true' : '';
      const response = await axios.get(
        `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${selectedCompanyId}?${includeInactive}`,
        { headers: getAuthHeaders() }
      );
      console.log('Users response:', response.data);
      console.log('Setting users:', response.data.users || []);
      setUsers(response.data.users || []);
    } catch (error) {
      console.error('Error fetching users:', error);
      setSnackbar({ open: true, message: 'Failed to fetch users', severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, [getAuthHeaders, selectedCompanyId, showInactiveUsers]);

  // Setup refresh listener
  useEffect(() => {
    refreshService.onUserCreated((data) => {
      console.log('User created event received:', data);
      fetchUsers(); // Refresh user list
    });

    refreshService.onAutoRefresh(() => {
      console.log('Auto refresh triggered');
      fetchUsers(); // Refresh user list
    });
  }, [hasRole, fetchUsers, fetchRoles, fetchCompanies]);

  useEffect(() => {
    if (hasRole('admin') || hasRole('super_admin')) {
      fetchUsers();
      fetchRoles();
      fetchCompanies();
    } else if (user?.role === 'user') {
      // Show access denied popup for users
      Swal.fire({
        icon: 'error',
        title: 'Access Denied',
        text: "You don't have enough access rights to access the Admin Panel",
        confirmButtonColor: '#3085d6',
        confirmButtonText: 'OK'
      }).then(() => {
        // Redirect to dashboard
        window.location.hash = '/';
      });
    }
  }, [hasRole, fetchUsers, fetchRoles, fetchCompanies, user?.role]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const payload = {
        ...formData,
        companyid: parseInt(formData.companyid)
      };
      
      if (editingUser) {
        // Update user (if needed in future)
        const response = await axios.put(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${editingUser.companyid}/${editingUser.username}`,
          payload,
          { headers: getAuthHeaders() }
        );
        setSnackbar({ open: true, message: 'User updated successfully', severity: 'success' });
      } else {
        // Create new user
        const response = await axios.post(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${formData.companyid}`,
          payload,
          { headers: getAuthHeaders() }
        );
        setSnackbar({ open: true, message: 'User created successfully', severity: 'success' });
      }

      setOpenDialog(false);
      setEditingUser(null);
      setFormData({
        username: '',
        email: '',
        password: '',
        name: '',
        role: 'user',
        companyid: user?.companyid || 1,
        access_hours: 24
      });
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
      setSnackbar({ 
        open: true, 
        message: error.response?.data?.detail || 'Failed to save user', 
        severity: 'error' 
      });
    }
  };

  // Handle edit user
  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '', // Don't populate password for security
      name: user.name,
      role: user.role,
      companyid: user.companyid,
      access_hours: 24
    });
    setOpenDialog(true);
  };

  // Extend user access
  const handleExtendAccess = async (userId) => {
    const { value: hours } = await Swal.fire({
      title: 'Extend Access',
      input: 'number',
      inputLabel: 'Hours to extend',
      inputPlaceholder: 'Enter hours',
      inputValidator: (value) => {
        if (!value || value <= 0) {
          return 'Please enter a valid number of hours';
        }
        return null;
      }
    });

    if (hours) {
      try {
        const response = await axios.post(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/extend-access`,
          { user_id: userId, hours: parseInt(hours) },
          { headers: getAuthHeaders() }
        );
        setSnackbar({ open: true, message: 'Access extended successfully', severity: 'success' });
        fetchUsers();
      } catch (error) {
        console.error('Error extending access:', error);
        let errorMessage = 'Failed to extend access';
        
        if (error.response?.data?.detail) {
          errorMessage = typeof error.response.data.detail === 'string' 
            ? error.response.data.detail 
            : JSON.stringify(error.response.data.detail);
        } else if (error.response?.data?.message) {
          errorMessage = typeof error.response.data.message === 'string' 
            ? error.response.data.message 
            : JSON.stringify(error.response.data.message);
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setSnackbar({ open: true, message: errorMessage, severity: 'error' });
      }
    }
  };

  // Deactivate user
  const handleDeactivateUser = async (userId, username) => {
    const result = await Swal.fire({
      title: 'Deactivate User?',
      text: `Are you sure you want to deactivate ${username}? This action cannot be undone.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Deactivate',
      cancelButtonText: 'Cancel'
    });

    if (result.isConfirmed) {
      try {
        const response = await axios.delete(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${selectedCompanyId}/${userId}`,
          { headers: getAuthHeaders() }
        );
        setSnackbar({ open: true, message: 'User deactivated successfully', severity: 'success' });
        fetchUsers();
      } catch (error) {
        console.error('Error deactivating user:', error);
        let errorMessage = 'Failed to deactivate user';
        
        if (error.response?.data?.detail) {
          errorMessage = typeof error.response.data.detail === 'string' 
            ? error.response.data.detail 
            : JSON.stringify(error.response.data.detail);
        } else if (error.response?.data?.message) {
          errorMessage = typeof error.response.data.message === 'string' 
            ? error.response.data.message 
            : JSON.stringify(error.response.data.message);
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setSnackbar({ open: true, message: errorMessage, severity: 'error' });
      }
    }
  };

  // Reactivate user
  const handleReactivateUser = async (userId, username) => {
    const result = await Swal.fire({
      title: 'Reactivate User?',
      text: `Are you sure you want to reactivate ${username}?`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#28a745',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Reactivate',
      cancelButtonText: 'Cancel'
    });

    if (result.isConfirmed) {
      try {
        const headers = getAuthHeaders();
        console.log('Reactivate user - Headers:', headers);
        console.log('Reactivate user - URL:', `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${selectedCompanyId}/${userId}/reactivate`);
        
        const response = await axios.post(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${selectedCompanyId}/${userId}/reactivate`,
          {},
          { headers }
        );
        setSnackbar({ open: true, message: 'User reactivated successfully', severity: 'success' });
        fetchUsers();
      } catch (error) {
        console.error('Error reactivating user:', error);
        console.error('Error response:', error.response);
        console.error('Error status:', error.response?.status);
        console.error('Error data:', error.response?.data);
        
        let errorMessage = 'Failed to reactivate user';
        
        if (error.response?.data?.detail) {
          const errorDetail = error.response.data.detail;
          console.log('Error detail:', errorDetail);
          
          if (errorDetail.includes('already active') || errorDetail.includes('Failed to reactivate')) {
            errorMessage = 'User is already active';
          } else if (errorDetail.includes('Not authenticated') || errorDetail.includes('Unauthorized') || errorDetail.includes('invalid token')) {
            errorMessage = 'Authentication failed. Please log in again.';
          } else if (errorDetail.includes('Access denied') || errorDetail.includes('forbidden')) {
            errorMessage = 'Access denied. You do not have permission for this action.';
          } else {
            errorMessage = typeof errorDetail === 'string' 
              ? errorDetail 
              : JSON.stringify(errorDetail);
          }
        } else if (error.response?.data?.message) {
          errorMessage = typeof error.response.data.message === 'string' 
            ? error.response.data.message 
            : JSON.stringify(error.response.data.message);
        } else if (error.response?.status === 401) {
          errorMessage = 'Authentication failed. Please log in again.';
        } else if (error.response?.status === 403) {
          errorMessage = 'Access denied. You do not have permission for this action.';
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setSnackbar({ open: true, message: errorMessage, severity: 'warning' });
      }
    }
  };

  // Delete company
  const handleDeleteCompany = async (companyId) => {
    const result = await Swal.fire({
      title: 'Delete Company?',
      text: 'This will also delete all users in this company. This action cannot be undone!',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Delete Company',
      cancelButtonText: 'Cancel'
    });

    if (result.isConfirmed) {
      // Remove company from state
      setCompanies(companies.filter(c => c.id !== companyId));
      // Remove users from this company
      setUsers(users.filter(user => user.companyid !== companyId));
      setSnackbar({ open: true, message: 'Company deleted successfully', severity: 'success' });
    }
  };

  // Add new company
  const handleAddCompany = async () => {
    const { value: companyName } = await Swal.fire({
      title: 'Add New Company',
      input: 'text',
      inputLabel: 'Company Name',
      inputPlaceholder: 'Enter company name',
      inputValidator: (value) => {
        if (!value || value.trim() === '') {
          return 'Please enter a company name';
        }
        return null;
      }
    });

    if (companyName && companyName.trim() !== '') {
      try {
        // Call backend API to create company
        const response = await axios.post(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/companies`,
          {
            name: companyName.trim(),
            adminUsername: `admin_${companyName.trim().toLowerCase().replace(/\s+/g, '_')}`,
            adminEmail: `admin_${companyName.trim().toLowerCase().replace(/\s+/g, '_')}@company.com`,
            adminPassword: 'TempPassword123!',
            adminName: `Admin of ${companyName.trim()}`
          },
          { headers: getAuthHeaders() }
        );
        
        if (response.data.success || response.data.message) {
          // Refresh companies list from backend
          await fetchCompanies();
          setSnackbar({ open: true, message: 'Company created successfully', severity: 'success' });
        } else {
          // Handle error case
          const errorMessage = response.data?.detail || response.data?.message || 'Failed to create company';
          setSnackbar({ open: true, message: errorMessage, severity: 'error' });
        }
      } catch (error) {
        console.error('Error creating company:', error);
        setSnackbar({ open: true, message: 'Error creating company', severity: 'error' });
      }
    }
  };

  // Clear all data (super admin only)
  const handleClearAllData = async () => {
    const result = await Swal.fire({
      title: 'Clear All Data?',
      text: 'This will delete all users and reset the system. This action cannot be undone!',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Clear All Data',
      cancelButtonText: 'Cancel'
    });

    if (result.isConfirmed) {
      try {
        // This would be a backend endpoint to clear all data
        await axios.delete(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/clear-all-data`,
          { headers: getAuthHeaders() }
        );
        setSnackbar({ open: true, message: 'All data cleared successfully', severity: 'success' });
        fetchUsers();
      } catch (error) {
        console.error('Error clearing all data:', error);
        let errorMessage = 'Failed to clear all data';
        
        if (error.response?.data?.detail) {
          errorMessage = typeof error.response.data.detail === 'string' 
            ? error.response.data.detail 
            : JSON.stringify(error.response.data.detail);
        } else if (error.response?.data?.message) {
          errorMessage = typeof error.response.data.message === 'string' 
            ? error.response.data.message 
            : JSON.stringify(error.response.data.message);
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setSnackbar({ open: true, message: errorMessage, severity: 'error' });
      }
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'super_admin': return 'error';
      case 'admin': return 'warning';
      case 'marketing_manager': return 'secondary';
      case 'content_editor': return 'info';
      case 'sales_manager': return 'success';
      case 'user': return 'primary';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    return status ? 'success' : 'error';
  };

  if (!hasRole('admin') && !hasRole('super_admin')) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Access Denied: Admin privileges required</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#136aed', mb: 3 }}>
        Admin Panel
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Users" />
          <Tab label="Companies" />
        </Tabs>
      </Box>

      {activeTab === 0 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#136aed' }}>
              User Management
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              {hasRole('super_admin') && (
                <Button
                  variant="outlined"
                  color="error"
                  onClick={handleClearAllData}
                  sx={{ borderColor: '#d32f2f', color: '#d32f2f' }}
                >
                  Clear All Data
                </Button>
              )}
              {(hasRole('super_admin') || hasRole('admin')) && (
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenDialog(true)}
                  sx={{ backgroundColor: '#136aed' }}
                >
                  Create User
                </Button>
              )}
              <FormControlLabel
                control={
                  <Switch
                    checked={showInactiveUsers}
                    onChange={(e) => setShowInactiveUsers(e.target.checked)}
                    color="primary"
                  />
                }
                label="Show Inactive Users"
                sx={{ ml: 2 }}
              />
            </Box>
          </Box>

          {/* Company Selector */}
          <Box sx={{ mb: 2 }}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Company</InputLabel>
              <Select
                value={selectedCompanyId}
                label="Company"
                onChange={(e) => setSelectedCompanyId(e.target.value)}
              >
                {companies.map((company) => (
                  <MenuItem key={company.id} value={company.id}>
                    {company.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <Card>
            <CardContent>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Username</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Company</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Access Expires</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          <Typography>Loading...</Typography>
                        </TableCell>
                      </TableRow>
                    ) : users.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} align="center">
                          <Typography>No users found</Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      users.map((user) => (
                        <TableRow key={user.id || user.username}>
                          <TableCell>{user.username}</TableCell>
                          <TableCell>{user.name}</TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>
                            <Chip label={user.role} color={getRoleColor(user.role)} size="small" />
                          </TableCell>
                          <TableCell>
                            {companies.find(c => c.id === user.companyid)?.name || `Company ${user.companyid}`}
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={user.activitystatus ? 'Active' : 'Inactive'} 
                              color={getStatusColor(user.activitystatus)} 
                              size="small" 
                            />
                          </TableCell>
                          <TableCell>
                            {user.access_expires_at ? 
                              new Date(user.access_expires_at).toLocaleDateString() : 
                              'Never'
                            }
                          </TableCell>
                          <TableCell>
                            {(hasRole('super_admin') || hasRole('admin')) && (
                              <>
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditUser(user)}
                                  title="Edit User"
                                  color="primary"
                                >
                                  <EditIcon />
                                </IconButton>
                                {hasRole('super_admin') && user.access_expires_at && (
                                  <IconButton
                                    size="small"
                                    onClick={() => handleExtendAccess(user.id || user.username)}
                                    title="Extend Access"
                                  >
                                    <AccessTimeIcon />
                                  </IconButton>
                                )}
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeactivateUser(user.id || user.username, user.username)}
                                  title="Deactivate User"
                                  color="error"
                                >
                                  <DeleteIcon />
                                </IconButton>
                                {!user.activitystatus && (
                                  <IconButton
                                    size="small"
                                    onClick={() => handleReactivateUser(user.id || user.username, user.username)}
                                    title="Reactivate User"
                                    color="success"
                                  >
                                    <RestoreIcon />
                                  </IconButton>
                                )}
                              </>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#136aed' }}>
              Company Management
            </Typography>
            {hasRole('super_admin') && (
              <Button
                variant="contained"
                startIcon={<BusinessIcon />}
                onClick={handleAddCompany}
                sx={{ backgroundColor: '#136aed' }}
              >
                Add Company
              </Button>
            )}
          </Box>

          <Card>
            <CardContent>
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Company ID</TableCell>
                      <TableCell>Company Name</TableCell>
                      <TableCell>Number of Users</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {companies.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          <Typography>No companies found</Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      companies.map((company) => (
                        <TableRow key={company.id}>
                          <TableCell>{company.id}</TableCell>
                          <TableCell>{company.name}</TableCell>
                          <TableCell>
                            {users.filter(user => user.companyid === company.id).length}
                          </TableCell>
                          <TableCell>
                            {hasRole('super_admin') && (
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteCompany(company.id)}
                                title="Delete Company"
                                color="error"
                              >
                                <DeleteIcon />
                              </IconButton>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Create/Edit User Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingUser ? 'Edit User' : 'Create New User'}</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              margin="normal"
              required
              disabled={!!editingUser}
            />
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              margin="normal"
              required={!editingUser}
              placeholder={editingUser ? "Leave blank to keep current password" : ""}
            />
            <TextField
              fullWidth
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
              required
            />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FormControl fullWidth margin="normal" required>
                <InputLabel>Role</InputLabel>
                <Select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  disabled={rolesLoading}
                >
                  {rolesLoading ? (
                    <MenuItem value="" disabled>
                      Loading roles...
                    </MenuItem>
                  ) : availableRoles.length === 0 ? (
                    <MenuItem value="" disabled>
                      No roles available
                    </MenuItem>
                  ) : (
                    availableRoles.map((role) => (
                      <MenuItem key={role} value={role}>
                        {role.charAt(0).toUpperCase() + role.slice(1).replace(/_/g, ' ')}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
              <IconButton 
                onClick={fetchRoles} 
                disabled={rolesLoading}
                title="Refresh roles"
                sx={{ mt: 2 }}
              >
                <RefreshIcon />
              </IconButton>
            </Box>
            <FormControl fullWidth margin="normal" required>
              <InputLabel>Company</InputLabel>
              <Select
                value={formData.companyid}
                onChange={(e) => setFormData({ ...formData, companyid: e.target.value })}
              >
                {companies.map((company) => (
                  <MenuItem key={company.id} value={company.id}>
                    {company.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Access Hours (Optional)"
              name="access_hours"
              type="number"
              value={formData.access_hours}
              onChange={(e) => setFormData({ ...formData, access_hours: e.target.value })}
              margin="normal"
              helperText="Leave blank for permanent access"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained">{editingUser ? 'Update User' : 'Create User'}</Button>
          </DialogActions>
        </form>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AdminPanel;
