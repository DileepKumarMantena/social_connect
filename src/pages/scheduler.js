import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Grid,
    CircularProgress,
    Alert,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    Button,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    MenuItem,
    FormControl,
    InputLabel,
    Select
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Schedule as ScheduleIcon,
    Event as EventIcon,
    Alarm as AlarmIcon,
    CheckCircle as CheckCircleIcon,
    RadioButtonUnchecked as RadioButtonUncheckedIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const SchedulerPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingSchedule, setEditingSchedule] = useState(null);
    const [formData, setFormData] = useState({
        task_name: '',
        campaign_id: '',
        scheduled_date: '',
        scheduled_time: '',
        priority: 'medium'
    });

    useEffect(() => {
        fetchSchedules();
    }, []);

    const fetchSchedules = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/scheduler`,
                { headers: getAuthHeaders() }
            );
            setSchedules(response.data.schedules || []);
            setError('');
        } catch (error) {
            console.error('Error fetching schedules:', error);
            setError('Failed to fetch schedules');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'success';
            case 'scheduled':
                return 'info';
            case 'pending':
                return 'warning';
            default:
                return 'default';
        }
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 'high':
                return 'error';
            case 'medium':
                return 'warning';
            case 'low':
                return 'success';
            default:
                return 'default';
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'completed':
                return <CheckCircleIcon />;
            case 'scheduled':
                return <ScheduleIcon />;
            case 'pending':
                return <RadioButtonUncheckedIcon />;
            default:
                return <ScheduleIcon />;
        }
    };

    const handleCreateSchedule = () => {
        setEditingSchedule(null);
        setFormData({
            task_name: '',
            campaign_id: '',
            scheduled_date: '',
            scheduled_time: '',
            priority: 'medium'
        });
        setOpenDialog(true);
    };

    const handleEditSchedule = (schedule) => {
        setEditingSchedule(schedule);
        setFormData({
            task_name: schedule.task_name,
            campaign_id: schedule.campaign_id,
            scheduled_date: schedule.scheduled_date,
            scheduled_time: schedule.scheduled_time,
            priority: schedule.priority
        });
        setOpenDialog(true);
    };

    const handleDeleteSchedule = async (schedule) => {
        if (window.confirm(`Are you sure you want to delete "${schedule.task_name}"?`)) {
            try {
                await axios.delete(
                    `${process.env.REACT_APP_API_LINKS}/api/v1/scheduler/${schedule.id}`,
                    { headers: getAuthHeaders() }
                );
                // Remove the schedule from the schedules array
                setSchedules(schedules.filter(s => s.id !== schedule.id));
                console.log('Schedule deleted successfully');
            } catch (error) {
                console.error('Error deleting schedule:', error);
            }
        }
    };

    const handleSaveSchedule = async () => {
        try {
            const url = editingSchedule 
                ? `${process.env.REACT_APP_API_LINKS}/api/v1/scheduler/${editingSchedule.id}`
                : `${process.env.REACT_APP_API_LINKS}/api/v1/scheduler`;
            
            const method = editingSchedule ? 'put' : 'post';
            
            const response = await axios({
                method,
                url,
                data: formData,
                headers: getAuthHeaders()
            });
            
            if (response.data.success || response.data.message) {
                // Refresh schedules list
                fetchSchedules();
                setOpenDialog(false);
                setEditingSchedule(null);
                setFormData({
                    task_name: '',
                    campaign_id: '',
                    scheduled_date: '',
                    scheduled_time: '',
                    priority: 'medium'
                });
                console.log('Schedule saved successfully:', response.data);
            } else {
                console.error('Failed to save schedule:', response.data.message);
            }
        } catch (error) {
            console.error('Error saving schedule:', error);
            const errorMessage = error.response?.data?.message || error.message || 'Failed to save schedule';
            setError(errorMessage);
        }
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingSchedule(null);
    };

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
                <Box>
                    <Typography variant="h4" component="h1">
                        Scheduler
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        Manage campaign schedules and tasks
                    </Typography>
                </Box>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleCreateSchedule}
                >
                    Add Schedule
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                {/* Summary Cards */}
                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <ScheduleIcon color="primary" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Total Tasks
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {schedules.length}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Scheduled tasks
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Completed
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {schedules.filter(s => s.status === 'completed').length}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Tasks completed
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <AlarmIcon color="warning" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Pending
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {schedules.filter(s => s.status === 'pending').length}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Tasks pending
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <EventIcon color="info" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Scheduled
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {schedules.filter(s => s.status === 'scheduled').length}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Tasks scheduled
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Schedule Table */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Scheduled Tasks
                            </Typography>
                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Task Name</TableCell>
                                            <TableCell>Campaign ID</TableCell>
                                            <TableCell>Date</TableCell>
                                            <TableCell>Time</TableCell>
                                            <TableCell>Status</TableCell>
                                            <TableCell>Priority</TableCell>
                                            <TableCell>Created By</TableCell>
                                            <TableCell>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {schedules.map((schedule) => (
                                            <TableRow key={schedule.id}>
                                                <TableCell>
                                                    <Typography variant="body1" fontWeight="medium">
                                                        {schedule.task_name}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={schedule.campaign_id}
                                                        size="small"
                                                        color="primary"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    {new Date(schedule.scheduled_date).toLocaleDateString()}
                                                </TableCell>
                                                <TableCell>
                                                    {schedule.scheduled_time}
                                                </TableCell>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center">
                                                        {getStatusIcon(schedule.status)}
                                                        <Chip
                                                            label={schedule.status}
                                                            color={getStatusColor(schedule.status)}
                                                            size="small"
                                                            sx={{ ml: 1 }}
                                                        />
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={schedule.priority}
                                                        color={getPriorityColor(schedule.priority)}
                                                        size="small"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    {schedule.created_by || 'Unknown'}
                                                </TableCell>
                                                <TableCell>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleEditSchedule(schedule)}
                                                    >
                                                        <EditIcon />
                                                    </IconButton>
                                                    <IconButton
                                                        size="small"
                                                        onClick={() => handleDeleteSchedule(schedule)}
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
            </Grid>

            {/* Add/Edit Schedule Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {editingSchedule ? 'Edit Schedule' : 'Add New Schedule'}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <TextField
                            fullWidth
                            label="Task Name"
                            value={formData.task_name}
                            onChange={(e) => setFormData({ ...formData, task_name: e.target.value })}
                            margin="normal"
                        />
                        <TextField
                            fullWidth
                            label="Campaign ID"
                            value={formData.campaign_id}
                            onChange={(e) => setFormData({ ...formData, campaign_id: e.target.value })}
                            margin="normal"
                        />
                        <TextField
                            fullWidth
                            label="Scheduled Date"
                            type="date"
                            value={formData.scheduled_date}
                            onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                            margin="normal"
                            InputLabelProps={{ shrink: true }}
                        />
                        <TextField
                            fullWidth
                            label="Scheduled Time"
                            type="time"
                            value={formData.scheduled_time}
                            onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                            margin="normal"
                            InputLabelProps={{ shrink: true }}
                        />
                        <FormControl fullWidth margin="normal">
                            <InputLabel>Priority</InputLabel>
                            <Select
                                value={formData.priority}
                                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                            >
                                <MenuItem value="high">High</MenuItem>
                                <MenuItem value="medium">Medium</MenuItem>
                                <MenuItem value="low">Low</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancel</Button>
                    <Button onClick={handleSaveSchedule} variant="contained">
                        {editingSchedule ? 'Update' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default SchedulerPage;
