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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  Tabs,
  Tab,
  Checkbox,
  ListItemText
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  AccessTime as AccessTimeIcon,
  Business as BusinessIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
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
  const [companies, setCompanies] = useState([
    { id: 0, name: 'Hippo Cloud' },
    { id: 1, name: 'Company 1' },
    { id: 2, name: 'Company 2' }
  ]);
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    name: '',
    role: '', // Will be set when roles are loaded
    companyid: 1,
    access_hours: 24
  });
  
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

  // Fetch users
  const fetchUsers = useCallback(async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users`,
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
  }, [getAuthHeaders]);

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
  }, []);

  useEffect(() => {
    if (hasRole('admin') || hasRole('super_admin')) {
      fetchUsers();
      fetchRoles();
    }
  }, [hasRole, fetchUsers, fetchRoles]);

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
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${editingUser.id}`,
          payload,
          { headers: getAuthHeaders() }
        );
        setSnackbar({ open: true, message: 'User updated successfully', severity: 'success' });
      } else {
        // Create new user
        const response = await axios.post(
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users`,
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
          `${process.env.REACT_APP_API_LINKS}/api/v1/admin/users/${userId}`,
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
      // Get the highest current ID and add 1
      const newCompanyId = companies.length > 0 ? Math.max(...companies.map(c => c.id)) + 1 : 1;
      const newCompany = {
        id: newCompanyId,
        name: companyName.trim()
      };
      setCompanies([...companies, newCompany]);
      setSnackbar({ open: true, message: 'Company added successfully', severity: 'success' });
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
            </Box>
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
