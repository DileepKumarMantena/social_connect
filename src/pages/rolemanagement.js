import React, { useState, useEffect } from "react";
import {
    Box,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Checkbox,
    Paper,
    Typography,
    Button,
    TextField,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Chip,
    Card,
    CardContent,
    Alert,
    Snackbar,
    Tooltip,
    alpha,
} from "@mui/material";
import { 
    Add, 
    Delete, 
    Edit, 
    Save,
    Close,
    WarningAmber 
} from "@mui/icons-material";
import { useAuth } from "../contexts/AuthContext";
import axios from "axios";

// ------------------- Modules & Permissions -------------------
const modules = [
    { key: "role_management", label: "Role Management" },
    { key: "campaigns", label: "Campaigns" },
    { key: "analytics", label: "Analytics" },
    { key: "leads", label: "Leads" },
    { key: "channels", label: "Channels" },
    { key: "scheduler", label: "Scheduler" },
];

const permissionTypes = ["Create", "Read", "Update", "Delete"];

const RoleManagementPage = () => {
    const { user, getAuthHeaders } = useAuth();
    const [roles, setRoles] = useState([]);
    const [selectedRole, setSelectedRole] = useState("");
    const [permissions, setPermissions] = useState({});
    const [loading, setLoading] = useState(true);
    
    // Dialog states
    const [openDialog, setOpenDialog] = useState(false);
    const [dialogMode, setDialogMode] = useState("add"); // "add" or "edit"
    const [currentRole, setCurrentRole] = useState({ key: "", label: "" });
    const [roleName, setRoleName] = useState("");
    const [roleError, setRoleError] = useState("");
    
    // Delete confirmation
    const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
    const [roleToDelete, setRoleToDelete] = useState(null);
    
    // Snackbar for notifications
    const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });

    const isSuperAdmin = user?.role === "super_admin";

    // API Functions
    const fetchRoles = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/admin/roles`,
                { headers: getAuthHeaders() }
            );
            setRoles(response.data.roles || []);
            setPermissions(response.data.permissions || {});
            if (response.data.roles?.length > 0 && !selectedRole) {
                setSelectedRole(response.data.roles[0]);
            }
        } catch (error) {
            console.error('Error fetching roles:', error);
            setSnackbar({ 
                open: true, 
                message: error.response?.data?.detail || 'Failed to fetch roles', 
                severity: 'error' 
            });
        } finally {
            setLoading(false);
        }
    };

    const createRole = async (roleName) => {
        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_LINKS}/api/v1/admin/roles`,
                { role_name: roleName },
                { headers: getAuthHeaders() }
            );
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    const updateRole = async (roleKey, roleName) => {
        try {
            const response = await axios.put(
                `${process.env.REACT_APP_API_LINKS}/api/v1/admin/roles/${roleKey}`,
                { role_name: roleName },
                { headers: getAuthHeaders() }
            );
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    const deleteRole = async (roleKey) => {
        try {
            const response = await axios.delete(
                `${process.env.REACT_APP_API_LINKS}/api/v1/admin/roles/${roleKey}`,
                { headers: getAuthHeaders() }
            );
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    const updatePermissions = async (roleKey, permissions) => {
        try {
            const response = await axios.put(
                `${process.env.REACT_APP_API_LINKS}/api/v1/admin/roles/${roleKey}/permissions`,
                { role_key: roleKey, permissions },
                { headers: getAuthHeaders() }
            );
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    // Load roles on component mount
    useEffect(() => {
        if (isSuperAdmin) {
            fetchRoles();
        }
    }, [isSuperAdmin]);

    // Open add role dialog
    const handleOpenAddDialog = () => {
        setDialogMode("add");
        setRoleName("");
        setRoleError("");
        setOpenDialog(true);
    };

    // Open edit role dialog
    const handleOpenEditDialog = (roleKey) => {
        const roleLabel = roleKey.charAt(0).toUpperCase() + roleKey.slice(1).replace(/_/g, ' ');
        setDialogMode("edit");
        setCurrentRole({ key: roleKey, label: roleLabel });
        setRoleName(roleLabel);
        setRoleError("");
        setOpenDialog(true);
    };

    // Close dialog
    const handleCloseDialog = () => {
        setOpenDialog(false);
        setRoleName("");
        setRoleError("");
    };

    // Validate role name
    const validateRoleName = (name) => {
        if (!name.trim()) return "Role name is required";
        const roleKey = name.toLowerCase().replace(/\s+/g, "_");
        if (dialogMode === "add" && roles.includes(roleKey)) {
            return "Role already exists";
        }
        if (dialogMode === "edit" && roleKey !== currentRole.key && roles.includes(roleKey)) {
            return "Another role with this name already exists";
        }
        return "";
    };

    // Save role (add or edit)
    const handleSaveRole = async () => {
        const error = validateRoleName(roleName);
        if (error) {
            setRoleError(error);
            return;
        }

        try {
            if (dialogMode === "add") {
                // Create new role
                const result = await createRole(roleName);
                setSnackbar({
                    open: true,
                    message: result.message,
                    severity: "success"
                });
                await fetchRoles(); // Refresh data
                setSelectedRole(result.role_key);
            } else {
                // Edit existing role
                const result = await updateRole(currentRole.key, roleName);
                setSnackbar({
                    open: true,
                    message: result.message,
                    severity: "success"
                });
                await fetchRoles(); // Refresh data
                if (selectedRole === currentRole.key) {
                    setSelectedRole(result.role_key);
                }
            }

            handleCloseDialog();
        } catch (error) {
            console.error('Error saving role:', error);
            setSnackbar({
                open: true,
                message: error.response?.data?.detail || 'Failed to save role',
                severity: 'error'
            });
        }
    };

    // Open delete confirmation
    const handleOpenDeleteConfirm = (roleKey, event) => {
        event.stopPropagation();
        setRoleToDelete(roleKey);
        setDeleteConfirmOpen(true);
    };

    // Delete role
    const handleDeleteRole = async () => {
        if (!roleToDelete) return;

        try {
            const result = await deleteRole(roleToDelete);
            setSnackbar({
                open: true,
                message: result.message,
                severity: "info"
            });
            
            await fetchRoles(); // Refresh data
            if (selectedRole === roleToDelete) {
                setSelectedRole(roles[0] || "");
            }
            
            setDeleteConfirmOpen(false);
            setRoleToDelete(null);
        } catch (error) {
            console.error('Error deleting role:', error);
            setSnackbar({
                open: true,
                message: error.response?.data?.detail || 'Failed to delete role',
                severity: 'error'
            });
        }
    };

    // Toggle permission
    const togglePermission = (moduleKey, perm) => {
        setPermissions((prev) => ({
            ...prev,
            [selectedRole]: {
                ...prev[selectedRole],
                [moduleKey]: {
                    ...prev[selectedRole][moduleKey],
                    [perm]: !prev[selectedRole][moduleKey][perm],
                },
            },
        }));
    };

    // Select all permissions for a module
    const handleSelectAll = (moduleKey, checked) => {
        setPermissions((prev) => ({
            ...prev,
            [selectedRole]: {
                ...prev[selectedRole],
                [moduleKey]: {
                    Create: checked,
                    Read: checked,
                    Update: checked,
                    Delete: checked,
                },
            },
        }));
    };

    // Save permissions
    const handleSavePermissions = async () => {
        try {
            const result = await updatePermissions(selectedRole, permissions[selectedRole]);
            setSnackbar({
                open: true,
                message: result.message,
                severity: "success"
            });
        } catch (error) {
            console.error('Error saving permissions:', error);
            setSnackbar({
                open: true,
                message: error.response?.data?.detail || 'Failed to save permissions',
                severity: 'error'
            });
        }
    };

    // Check if all permissions are selected for a module
    const isAllSelected = (moduleKey) => {
        if (!permissions[selectedRole]?.[moduleKey]) return false;
        return permissionTypes.every(perm => permissions[selectedRole][moduleKey][perm]);
    };

    // Modules to display
    const getModulesForRole = () => {
        if (isSuperAdmin) return modules;
        return modules.filter((mod) => mod.key !== "role_management");
    };

    return (
        <Box p={3}>
            {/* Access Check */}
            {!isSuperAdmin && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    Access Denied: Super Admin privileges required to manage roles and permissions.
                </Alert>
            )}

            {/* Loading State */}
            {isSuperAdmin && loading && (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                    <Typography>Loading roles...</Typography>
                </Box>
            )}

            {/* Header */}
            {isSuperAdmin && !loading && (
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                    <Typography variant="h5" fontWeight={600}>
                        Manage Roles & Permissions
                    </Typography>
                    
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={handleOpenAddDialog}
                        sx={{
                            borderRadius: 2,
                            textTransform: 'none',
                            boxShadow: '0 4px 12px rgba(30, 75, 140, 0.2)',
                        }}
                    >
                        Create New Role
                    </Button>
                </Box>
            )}

            {/* Roles List */}
            {isSuperAdmin && !loading && roles.length > 0 ? (
                <Card sx={{ mb: 3, borderRadius: 2 }}>
                    <CardContent>
                        <Typography variant="subtitle2" color="text.secondary" mb={2}>
                            Available Roles ({roles.length})
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                            {roles.map((role) => {
                                const roleLabel = role.charAt(0).toUpperCase() + role.slice(1).replace(/_/g, ' ');
                                return (
                                    <Chip
                                        key={role}
                                        label={roleLabel}
                                        onClick={() => setSelectedRole(role)}
                                        onDelete={(e) => handleOpenDeleteConfirm(role, e)}
                                        deleteIcon={<Delete />}
                                        color={selectedRole === role ? "primary" : "default"}
                                        variant={selectedRole === role ? "filled" : "outlined"}
                                        sx={{
                                            borderRadius: 2,
                                            py: 2,
                                            '& .MuiChip-label': { fontWeight: 500 },
                                            '& .MuiChip-deleteIcon': {
                                                color: selectedRole === role ? '#fff' : '#d32f2f',
                                                '&:hover': { color: '#b71c1c' }
                                            }
                                        }}
                                    />
                                );
                            })}
                        </Box>
                    </CardContent>
                </Card>
            ) : isSuperAdmin && !loading ? (
                <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                    No roles created yet. Click 'Create New Role' to get started.
                </Alert>
            ) : null}

            {/* Permissions Table */}
            {isSuperAdmin && !loading && selectedRole && permissions[selectedRole] && (
                <Card sx={{ borderRadius: 2, overflow: 'hidden' }}>
                    <Box sx={{ p: 2, backgroundColor: '#e3f2fd', borderBottom: '1px solid rgba(0,0,0,0.12)' }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Box>
                                <Typography variant="h6" fontWeight={600}>
                                    {selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1).replace(/_/g, ' ')}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Configure permissions for this role
                                </Typography>
                            </Box>
                            <Box>
                                <Tooltip title="Edit Role">
                                    <IconButton 
                                        onClick={() => handleOpenEditDialog(selectedRole)}
                                        sx={{ mr: 1 }}
                                    >
                                        <Edit />
                                    </IconButton>
                                </Tooltip>
                            </Box>
                        </Box>
                    </Box>

                    <TableContainer component={Paper} elevation={0}>
                        <Table>
                            <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
                                <TableRow>
                                    <TableCell sx={{ fontWeight: 600 }}>Module</TableCell>
                                    {permissionTypes.map((perm) => (
                                        <TableCell key={perm} align="center" sx={{ fontWeight: 600 }}>
                                            {perm}
                                        </TableCell>
                                    ))}
                                    <TableCell align="center" sx={{ fontWeight: 600 }}>
                                        Select All
                                    </TableCell>
                                </TableRow>
                            </TableHead>

                            <TableBody>
                                {getModulesForRole().map((mod) => (
                                    <TableRow 
                                        key={mod.key}
                                        sx={{ '&:hover': { backgroundColor: alpha('#00b4d8', 0.04) } }}
                                    >
                                        <TableCell sx={{ fontWeight: 500 }}>{mod.label}</TableCell>
                                        {permissionTypes.map((perm) => (
                                            <TableCell key={perm} align="center">
                                                <Checkbox
                                                    checked={permissions[selectedRole][mod.key]?.[perm] || false}
                                                    onChange={() => togglePermission(mod.key, perm)}
                                                    color="primary"
                                                    sx={{
                                                        '&.Mui-checked': {
                                                            color: '#1e4b8c',
                                                        },
                                                    }}
                                                />
                                            </TableCell>
                                        ))}
                                        <TableCell align="center">
                                            <Checkbox
                                                checked={isAllSelected(mod.key)}
                                                onChange={(e) => handleSelectAll(mod.key, e.target.checked)}
                                                color="primary"
                                                indeterminate={
                                                    !isAllSelected(mod.key) && 
                                                    permissionTypes.some(perm => permissions[selectedRole][mod.key]?.[perm])
                                                }
                                            />
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Card>
            )}

            {/* Save Button */}
            {isSuperAdmin && !loading && selectedRole && permissions[selectedRole] && (
                <Box mt={3} display="flex" justifyContent="flex-end">
                    <Button
                        variant="contained"
                        onClick={handleSavePermissions}
                        startIcon={<Save />}
                        sx={{
                            borderRadius: 2,
                            textTransform: 'none',
                            px: 4,
                            py: 1,
                        }}
                    >
                        Save Permissions
                    </Button>
                </Box>
            )}

            {/* Add/Edit Role Dialog */}
            <Dialog 
                open={openDialog} 
                onClose={handleCloseDialog}
                maxWidth="sm"
                fullWidth
                PaperProps={{
                    sx: { borderRadius: 3 }
                }}
            >
                <DialogTitle sx={{ pb: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="h6" fontWeight={600}>
                            {dialogMode === "add" ? "Create New Role" : "Edit Role"}
                        </Typography>
                        <IconButton onClick={handleCloseDialog} size="small">
                            <Close />
                        </IconButton>
                    </Box>
                </DialogTitle>
                
                <DialogContent>
                    <TextField
                        autoFocus
                        label="Role Name"
                        fullWidth
                        value={roleName}
                        onChange={(e) => {
                            setRoleName(e.target.value);
                            setRoleError("");
                        }}
                        error={!!roleError}
                        helperText={roleError}
                        placeholder="e.g., Marketing Manager, Content Editor"
                        sx={{ mt: 2 }}
                    />
                    
                    {dialogMode === "add" && (
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                            Role names should be unique and descriptive
                        </Typography>
                    )}
                </DialogContent>
                
                <DialogActions sx={{ p: 2, pt: 0 }}>
                    <Button 
                        onClick={handleCloseDialog}
                        variant="outlined"
                        sx={{ borderRadius: 2, textTransform: 'none' }}
                    >
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleSaveRole}
                        variant="contained"
                        startIcon={dialogMode === "add" ? <Add /> : <Save />}
                        sx={{ borderRadius: 2, textTransform: 'none' }}
                    >
                        {dialogMode === "add" ? "Create Role" : "Save Changes"}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Delete Confirmation Dialog */}
            <Dialog
                open={deleteConfirmOpen}
                onClose={() => setDeleteConfirmOpen(false)}
                maxWidth="xs"
                fullWidth
                PaperProps={{
                    sx: { borderRadius: 3 }
                }}
            >
                <DialogTitle sx={{ pb: 1 }}>
                    <Box display="flex" alignItems="center" gap={1}>
                        <WarningAmber color="error" />
                        <Typography variant="h6" fontWeight={600}>
                            Confirm Delete
                        </Typography>
                    </Box>
                </DialogTitle>
                
                <DialogContent>
                    <Typography>
                        Are you sure you want to delete the role "{roleToDelete?.charAt(0).toUpperCase() + roleToDelete?.slice(1).replace(/_/g, ' ')}"?
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        This action cannot be undone. All permissions associated with this role will be lost.
                    </Typography>
                </DialogContent>
                
                <DialogActions sx={{ p: 2 }}>
                    <Button 
                        onClick={() => setDeleteConfirmOpen(false)}
                        variant="outlined"
                        sx={{ borderRadius: 2, textTransform: 'none' }}
                    >
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleDeleteRole}
                        variant="contained"
                        color="error"
                        startIcon={<Delete />}
                        sx={{ borderRadius: 2, textTransform: 'none' }}
                    >
                        Delete Role
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar for notifications */}
            <Snackbar
                open={snackbar.open}
                autoHideDuration={4000}
                onClose={() => setSnackbar({ ...snackbar, open: false })}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
                <Alert 
                    onClose={() => setSnackbar({ ...snackbar, open: false })} 
                    severity={snackbar.severity}
                    sx={{ 
                        borderRadius: 2,
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                    }}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default RoleManagementPage;