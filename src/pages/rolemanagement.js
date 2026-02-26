import React, { useState } from "react";
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
import { useAuth } from "../context/useAuth";

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
    const { logindata } = useAuth();
    const [roles, setRoles] = useState([]);
    const [selectedRole, setSelectedRole] = useState("");
    const [permissions, setPermissions] = useState({});
    
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

    const isSuperAdmin = logindata?.role === "super_admin";

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
    const handleSaveRole = () => {
        const error = validateRoleName(roleName);
        if (error) {
            setRoleError(error);
            return;
        }

        const newRoleKey = roleName.toLowerCase().replace(/\s+/g, "_");
        const newRoleLabel = roleName.trim();

        if (dialogMode === "add") {
            // Add new role
            setRoles([...roles, newRoleKey]);
            setPermissions({
                ...permissions,
                [newRoleKey]: modules.reduce((acc, mod) => {
                    acc[mod.key] = { Create: false, Read: false, Update: false, Delete: false };
                    return acc;
                }, {}),
            });
            setSelectedRole(newRoleKey);
            setSnackbar({
                open: true,
                message: `Role "${newRoleLabel}" created successfully`,
                severity: "success"
            });
        } else {
            // Edit existing role
            if (currentRole.key !== newRoleKey) {
                // Role name changed - update key
                const updatedRoles = roles.map(r => 
                    r === currentRole.key ? newRoleKey : r
                );
                setRoles(updatedRoles);
                
                // Update permissions with new key
                const updatedPermissions = { ...permissions };
                updatedPermissions[newRoleKey] = updatedPermissions[currentRole.key];
                delete updatedPermissions[currentRole.key];
                setPermissions(updatedPermissions);
                
                if (selectedRole === currentRole.key) {
                    setSelectedRole(newRoleKey);
                }
            }
            setSnackbar({
                open: true,
                message: `Role "${newRoleLabel}" updated successfully`,
                severity: "success"
            });
        }

        handleCloseDialog();
    };

    // Open delete confirmation
    const handleOpenDeleteConfirm = (roleKey, event) => {
        event.stopPropagation();
        setRoleToDelete(roleKey);
        setDeleteConfirmOpen(true);
    };

    // Delete role
    const handleDeleteRole = () => {
        if (!roleToDelete) return;

        const roleLabel = roleToDelete.charAt(0).toUpperCase() + roleToDelete.slice(1).replace(/_/g, ' ');
        const updatedRoles = roles.filter((r) => r !== roleToDelete);
        const updatedPermissions = { ...permissions };
        delete updatedPermissions[roleToDelete];
        
        setRoles(updatedRoles);
        setPermissions(updatedPermissions);
        
        if (selectedRole === roleToDelete) {
            setSelectedRole(updatedRoles[0] || "");
        }
        
        setDeleteConfirmOpen(false);
        setRoleToDelete(null);
        
        setSnackbar({
            open: true,
            message: `Role "${roleLabel}" deleted successfully`,
            severity: "info"
        });
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
    const handleSavePermissions = () => {
        console.log("Permissions for", selectedRole, permissions[selectedRole]);
        setSnackbar({
            open: true,
            message: `Permissions for "${selectedRole}" saved successfully!`,
            severity: "success"
        });
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
            {/* Header */}
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5" fontWeight={600}>
                    Manage Roles & Permissions
                </Typography>
                
                {isSuperAdmin && (
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
                )}
            </Box>

            {/* Roles List */}
            {roles.length > 0 ? (
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
                                        onDelete={isSuperAdmin ? (e) => handleOpenDeleteConfirm(role, e) : undefined}
                                        deleteIcon={isSuperAdmin ? <Delete /> : undefined}
                                        color={selectedRole === role ? "primary" : "default"}
                                        variant={selectedRole === role ? "filled" : "outlined"}
                                        sx={{
                                            borderRadius: 2,
                                            py: 2,
                                            '& .MuiChip-label': { fontWeight: 500 },
                                            ...(isSuperAdmin && {
                                                '& .MuiChip-deleteIcon': {
                                                    color: selectedRole === role ? '#fff' : '#d32f2f',
                                                    '&:hover': { color: '#b71c1c' }
                                                }
                                            })
                                        }}
                                    />
                                );
                            })}
                        </Box>
                    </CardContent>
                </Card>
            ) : (
                <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                    No roles created yet. {isSuperAdmin && "Click 'Create New Role' to get started."}
                </Alert>
            )}

            {/* Permissions Table */}
            {selectedRole && permissions[selectedRole] && (
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
                            {isSuperAdmin && (
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
                            )}
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
                                    {isSuperAdmin && (
                                        <TableCell align="center" sx={{ fontWeight: 600 }}>
                                            Select All
                                        </TableCell>
                                    )}
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
                                                    disabled={!isSuperAdmin}
                                                    color="primary"
                                                    sx={{
                                                        '&.Mui-checked': {
                                                            color: '#1e4b8c',
                                                        },
                                                    }}
                                                />
                                            </TableCell>
                                        ))}
                                        {isSuperAdmin && (
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
                                        )}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Card>
            )}

            {/* Save Button */}
            {selectedRole && isSuperAdmin && (
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