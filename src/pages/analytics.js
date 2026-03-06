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
    Chip
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    BarChart as BarChartIcon,
    PieChart as PieChartIcon,
    Timeline as TimelineIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const AnalyticsPage = () => {
    const { getAuthHeaders, user } = useAuth();
    const [analytics, setAnalytics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAnalytics();
    }, []);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${process.env.REACT_APP_API_LINKS}/api/v1/analytics`,
                { headers: getAuthHeaders() }
            );
            setAnalytics(response.data.analytics || []);
            setError('');
        } catch (error) {
            console.error('Error fetching analytics:', error);
            setError('Failed to fetch analytics');
        } finally {
            setLoading(false);
        }
    };

    const getMetricIcon = (metric) => {
        switch (metric) {
            case 'campaign_performance':
                return <BarChartIcon />;
            case 'lead_conversion':
                return <TrendingUpIcon />;
            case 'engagement_rate':
                return <PieChartIcon />;
            case 'roi':
                return <TrendingUpIcon />;
            case 'click_through_rate':
                return <TimelineIcon />;
            case 'cost_per_lead':
                return <TrendingDownIcon />;
            default:
                return <BarChartIcon />;
        }
    };

    const getMetricColor = (metric) => {
        switch (metric) {
            case 'campaign_performance':
                return 'primary';
            case 'lead_conversion':
                return 'success';
            case 'engagement_rate':
                return 'info';
            case 'roi':
                return 'success';
            case 'click_through_rate':
                return 'warning';
            case 'cost_per_lead':
                return 'error';
            default:
                return 'default';
        }
    };

    const getPeriodColor = (period) => {
        switch (period) {
            case 'weekly':
                return 'info';
            case 'monthly':
                return 'success';
            case 'quarterly':
                return 'warning';
            default:
                return 'default';
        }
    };

    const formatMetricName = (metric) => {
        return metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };

    const formatValue = (metric, value) => {
        switch (metric) {
            case 'roi':
                return `${value}%`;
            case 'lead_conversion':
            case 'engagement_rate':
            case 'click_through_rate':
                return `${value}%`;
            case 'cost_per_lead':
                return `$${value}`;
            default:
                return value.toFixed(1);
        }
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
            <Box mb={3}>
                <Typography variant="h4" component="h1">
                    Analytics Dashboard
                </Typography>
                <Typography variant="body2" color="textSecondary">
                    Performance metrics and insights
                </Typography>
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
                                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Total Metrics
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {analytics.length}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Analytics tracked
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <BarChartIcon color="success" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Performance
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {analytics.filter(a => a.metric === 'campaign_performance').length > 0 
                                    ? analytics.filter(a => a.metric === 'campaign_performance')[0].value.toFixed(1)
                                    : '0'}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Campaign Performance
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Conversion
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {analytics.filter(a => a.metric === 'lead_conversion').length > 0 
                                    ? analytics.filter(a => a.metric === 'lead_conversion')[0].value.toFixed(1)
                                    : '0'}%
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Lead Conversion Rate
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} md={3}>
                    <Card>
                        <CardContent>
                            <Box display="flex" alignItems="center" mb={1}>
                                <PieChartIcon color="warning" sx={{ mr: 1 }} />
                                <Typography variant="h6">
                                    Engagement
                                </Typography>
                            </Box>
                            <Typography variant="h4">
                                {analytics.filter(a => a.metric === 'engagement_rate').length > 0 
                                    ? analytics.filter(a => a.metric === 'engagement_rate')[0].value.toFixed(1)
                                    : '0'}%
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                                Engagement Rate
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Detailed Analytics Table */}
                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Detailed Analytics
                            </Typography>
                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>Metric</TableCell>
                                            <TableCell>Value</TableCell>
                                            <TableCell>Period</TableCell>
                                            <TableCell>Campaign/Channel ID</TableCell>
                                            <TableCell>Date</TableCell>
                                            <TableCell>Created By</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {analytics.map((analytic) => (
                                            <TableRow key={analytic.id}>
                                                <TableCell>
                                                    <Box display="flex" alignItems="center">
                                                        {getMetricIcon(analytic.metric)}
                                                        <Typography variant="body2" sx={{ ml: 1 }}>
                                                            {formatMetricName(analytic.metric)}
                                                        </Typography>
                                                    </Box>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography variant="body1" fontWeight="bold">
                                                        {formatValue(analytic.metric, analytic.value)}
                                                    </Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={analytic.period}
                                                        color={getPeriodColor(analytic.period)}
                                                        size="small"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    {analytic.campaign_id || analytic.channel_id || 'N/A'}
                                                </TableCell>
                                                <TableCell>
                                                    {new Date(analytic.date).toLocaleDateString()}
                                                </TableCell>
                                                <TableCell>
                                                    {analytic.created_by || 'Unknown'}
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
        </Box>
    );
};

export default AnalyticsPage;
