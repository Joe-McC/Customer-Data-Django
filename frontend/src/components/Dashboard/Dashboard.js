import React, { useState, useEffect } from 'react';
import { Typography, Grid, Paper, Box, Button, CircularProgress, Divider, Card, CardContent, List, ListItem, ListItemText, Chip } from '@mui/material';
import { Link } from 'react-router-dom';
import api from '../../services/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    data_subjects: { count: 0, expiring_soon: 0 },
    data_subject_requests: { total: 0, pending: 0, in_progress: 0, completed: 0, overdue: 0 },
    workflows: { total: 0, pending: 0, in_progress: 0, completed: 0, active_templates: 0 },
    documents: { total: 0, templates: 0, active: 0, needs_review: 0 },
    consent: { marketing_consent: 0, data_processing_consent: 0, cookie_consent: 0, total_data_subjects: 0 },
    recent_consent_activities: []
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/dashboard/enhanced/');
        setDashboardData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const processAutomatedWorkflows = async () => {
    try {
      setLoading(true);
      const response = await api.post('/automated-workflows/process/');
      alert(`Processed ${response.data.processed} workflows. Success: ${response.data.successful}, Failed: ${response.data.failed}`);
      // Refresh dashboard data
      const dashboardResponse = await api.get('/dashboard/enhanced/');
      setDashboardData(dashboardResponse.data);
    } catch (err) {
      console.error('Error processing automated workflows:', err);
      setError('Failed to process automated workflows');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !dashboardData.data_subjects.count) {
    return <CircularProgress />;
  }

  const { data_subjects, data_subject_requests, workflows, documents, consent, recent_consent_activities } = dashboardData;

  return (
    <div>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          GDPR Compliance Dashboard
        </Typography>
        <Button 
          variant="contained" 
          color="primary"
          onClick={processAutomatedWorkflows}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'Process Automated Workflows'}
        </Button>
      </Box>
      
      {error && (
        <Paper elevation={2} sx={{ p: 2, mb: 3, bgcolor: '#fff4f4' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
      
      <Typography variant="h6" sx={{ mb: 2 }}>Data Subject Overview</Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle1">Data Subjects</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">{data_subjects.count}</Typography>
              <Typography variant="body2" color="textSecondary">Registered Individuals</Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Paper elevation={2} sx={{ p: 2, height: '100%', bgcolor: data_subjects.expiring_soon > 0 ? '#fff9e6' : 'inherit' }}>
            <Typography variant="subtitle1">Expiring Soon</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3" color={data_subjects.expiring_soon > 0 ? 'warning.main' : 'inherit'}>
                {data_subjects.expiring_soon}
              </Typography>
              <Typography variant="body2" color="textSecondary">Records expiring in 30 days</Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle1">Consent Status</Typography>
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-around' }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4">{Math.round((consent.data_processing_consent / consent.total_data_subjects || 0) * 100)}%</Typography>
                <Typography variant="body2" color="textSecondary">Processing Consent</Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4">{Math.round((consent.marketing_consent / consent.total_data_subjects || 0) * 100)}%</Typography>
                <Typography variant="body2" color="textSecondary">Marketing Consent</Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4">{Math.round((consent.cookie_consent / consent.total_data_subjects || 0) * 100)}%</Typography>
                <Typography variant="body2" color="textSecondary">Cookie Consent</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      <Typography variant="h6" sx={{ mb: 2 }}>GDPR Workflows</Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Paper elevation={2} sx={{ p: 2, height: '100%', bgcolor: data_subject_requests.pending > 0 ? '#e8f4fd' : 'inherit' }}>
            <Typography variant="subtitle1">Data Subject Requests</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">{data_subject_requests.pending}</Typography>
              <Typography variant="body2" color="textSecondary">Pending Requests</Typography>
              <Box sx={{ mt: 1 }}>
                <Chip 
                  size="small" 
                  color={data_subject_requests.overdue > 0 ? "error" : "default"} 
                  label={`${data_subject_requests.overdue} Overdue`} 
                  sx={{ mr: 1 }} 
                />
                <Chip 
                  size="small" 
                  color="primary" 
                  label={`${data_subject_requests.in_progress} In Progress`} 
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle1">Active Workflows</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">{workflows.in_progress}</Typography>
              <Typography variant="body2" color="textSecondary">In-progress workflows</Typography>
              <Box sx={{ mt: 1 }}>
                <Chip 
                  size="small" 
                  color="secondary" 
                  label={`${workflows.active_templates} Active Templates`} 
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle1">Documents</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">{documents.templates}</Typography>
              <Typography variant="body2" color="textSecondary">Document Templates</Typography>
              <Box sx={{ mt: 1 }}>
                <Chip 
                  size="small" 
                  color={documents.needs_review > 0 ? "warning" : "success"} 
                  label={`${documents.needs_review} Need Review`} 
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Paper elevation={2} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="subtitle1">Quick Actions</Typography>
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1, flexGrow: 1, justifyContent: 'center' }}>
              <Button variant="outlined" component={Link} to="/data-subjects">
                Manage Data Subjects
              </Button>
              <Button variant="outlined" component={Link} to="/workflows">
                View Workflows
              </Button>
              <Button variant="outlined" component={Link} to="/documents">
                Manage Documents
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>
      
      <Typography variant="h6" sx={{ mb: 2 }}>Recent Consent Activities</Typography>
      <Paper elevation={2} sx={{ p: 2 }}>
        {recent_consent_activities.length === 0 ? (
          <Typography variant="body1" color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
            No recent consent activities found.
          </Typography>
        ) : (
          <List dense>
            {recent_consent_activities.map((activity) => (
              <ListItem key={activity.id} divider>
                <ListItemText
                  primary={
                    <Typography variant="body1">
                      <strong>{activity.data_subject}</strong> - {activity.activity_type}
                      {activity.consent_type && ` (${activity.consent_type})`}
                    </Typography>
                  }
                  secondary={new Date(activity.timestamp).toLocaleString()}
                />
                <Box>
                  <Button size="small" component={Link} to={`/data-subjects/${activity.data_subject_id}`}>
                    View Details
                  </Button>
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </div>
  );
};

export default Dashboard;