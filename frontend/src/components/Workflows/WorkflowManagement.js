import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  CircularProgress,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Stepper,
  Step,
  StepLabel,
  LinearProgress
} from '@mui/material';
import api from '../../services/api';

// Status chip color mappings
const statusColors = {
  pending: 'default',
  in_progress: 'primary',
  completed: 'success',
  cancelled: 'error',
  failed: 'error',
  skipped: 'warning'
};

const WorkflowManagement = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [workflowDialogOpen, setWorkflowDialogOpen] = useState(false);
  
  useEffect(() => {
    fetchWorkflows();
  }, [tabValue]);
  
  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Determine status filter based on tab
      let statusFilter;
      switch (tabValue) {
        case 0: // All
          statusFilter = undefined;
          break;
        case 1: // Pending
          statusFilter = 'pending';
          break;
        case 2: // In Progress
          statusFilter = 'in_progress';
          break;
        case 3: // Completed
          statusFilter = 'completed';
          break;
        default:
          statusFilter = undefined;
      }
      
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await api.get('/workflow-instances/', { params });
      setWorkflows(response.data.results || []);
    } catch (err) {
      console.error('Error fetching workflows:', err);
      setError('Failed to load workflows. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleViewWorkflow = async (workflowId) => {
    try {
      setLoading(true);
      const response = await api.get(`/workflow-instances/${workflowId}/`);
      setSelectedWorkflow(response.data);
      setWorkflowDialogOpen(true);
    } catch (err) {
      console.error('Error fetching workflow details:', err);
      setError('Failed to load workflow details');
    } finally {
      setLoading(false);
    }
  };
  
  const handleCloseDialog = () => {
    setWorkflowDialogOpen(false);
  };
  
  const advanceWorkflow = async (workflowId) => {
    try {
      setLoading(true);
      await api.post(`/workflow-instances/${workflowId}/advance/`);
      
      // Refetch workflow details
      const response = await api.get(`/workflow-instances/${workflowId}/`);
      setSelectedWorkflow(response.data);
      
      // Also update workflows list
      fetchWorkflows();
    } catch (err) {
      console.error('Error advancing workflow:', err);
      setError('Failed to advance workflow');
    } finally {
      setLoading(false);
    }
  };
  
  const completeStep = async (stepId) => {
    try {
      setLoading(true);
      await api.post(`/workflow-steps/${stepId}/complete/`);
      
      // Refetch workflow details
      const response = await api.get(`/workflow-instances/${selectedWorkflow.id}/`);
      setSelectedWorkflow(response.data);
      
      // Also update workflows list
      fetchWorkflows();
    } catch (err) {
      console.error('Error completing step:', err);
      setError('Failed to complete step');
    } finally {
      setLoading(false);
    }
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };
  
  // Get active step index for stepper
  const getActiveStepIndex = (workflow) => {
    if (!workflow || !workflow.steps || workflow.steps.length === 0) return -1;
    
    const inProgressIndex = workflow.steps.findIndex(step => step.status === 'in_progress');
    if (inProgressIndex !== -1) return inProgressIndex;
    
    // If no in_progress step, find the first pending step
    const pendingIndex = workflow.steps.findIndex(step => step.status === 'pending');
    if (pendingIndex !== -1) return pendingIndex;
    
    // If all steps are completed, return the last step index
    return workflow.steps.length - 1;
  };
  
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        GDPR Workflow Management
      </Typography>
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="All Workflows" />
          <Tab label="Pending" />
          <Tab label="In Progress" />
          <Tab label="Completed" />
        </Tabs>
      </Paper>
      
      {error && (
        <Paper elevation={2} sx={{ p: 2, mb: 3, bgcolor: '#fff4f4' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
      
      {loading && !workflows.length ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : workflows.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No workflows found with the selected filter.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Workflow Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Due Date</TableCell>
                <TableCell>Data Subject</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {workflows.map((workflow) => (
                <TableRow key={workflow.id}>
                  <TableCell>{workflow.name}</TableCell>
                  <TableCell>
                    {workflow.template_detail?.workflow_type || 'Custom'}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      size="small" 
                      color={statusColors[workflow.status] || 'default'} 
                      label={workflow.status.toUpperCase()} 
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={workflow.progress_percentage || 0} 
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="textSecondary">
                          {`${workflow.progress_percentage || 0}%`}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {formatDate(workflow.due_date)}
                  </TableCell>
                  <TableCell>
                    {workflow.data_subject ? 
                      workflow.data_subject.first_name + ' ' + workflow.data_subject.last_name : 
                      'N/A'}
                  </TableCell>
                  <TableCell>
                    <Button 
                      size="small" 
                      color="primary" 
                      onClick={() => handleViewWorkflow(workflow.id)}
                    >
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {/* Workflow Detail Dialog */}
      <Dialog 
        open={workflowDialogOpen} 
        onClose={handleCloseDialog}
        fullWidth
        maxWidth="md"
      >
        {selectedWorkflow ? (
          <>
            <DialogTitle>
              Workflow: {selectedWorkflow.name}
              <Chip 
                size="small" 
                color={statusColors[selectedWorkflow.status] || 'default'} 
                label={selectedWorkflow.status.toUpperCase()} 
                sx={{ ml: 2 }}
              />
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1">Workflow Details</Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText 
                        primary="Type" 
                        secondary={selectedWorkflow.template_detail?.workflow_type || 'Custom'} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="Due Date" 
                        secondary={formatDate(selectedWorkflow.due_date)} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="Created" 
                        secondary={formatDate(selectedWorkflow.created_at)} 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary="Progress" 
                        secondary={`${selectedWorkflow.progress_percentage || 0}% Complete`} 
                      />
                    </ListItem>
                  </List>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1">Related Information</Typography>
                  {selectedWorkflow.data_subject ? (
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Data Subject" 
                          secondary={`${selectedWorkflow.data_subject.first_name} ${selectedWorkflow.data_subject.last_name}`} 
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Email" 
                          secondary={selectedWorkflow.data_subject.email} 
                        />
                      </ListItem>
                    </List>
                  ) : (
                    <Typography variant="body2" color="textSecondary">
                      No data subject associated with this workflow.
                    </Typography>
                  )}
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" sx={{ mb: 2 }}>Workflow Progress</Typography>
                  <Stepper activeStep={getActiveStepIndex(selectedWorkflow)} alternativeLabel>
                    {selectedWorkflow.steps?.map((step) => (
                      <Step key={step.id}>
                        <StepLabel error={step.status === 'failed'}>
                          {step.name}
                          <Box sx={{ mt: 1 }}>
                            <Chip 
                              size="small" 
                              color={statusColors[step.status] || 'default'} 
                              label={step.status.toUpperCase()} 
                            />
                          </Box>
                        </StepLabel>
                      </Step>
                    ))}
                  </Stepper>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>Step Details</Typography>
                  
                  {selectedWorkflow.current_step ? (
                    <Paper elevation={2} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                      <Typography variant="h6">
                        Current Step: {selectedWorkflow.current_step.name}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        {selectedWorkflow.current_step.description}
                      </Typography>
                      
                      {selectedWorkflow.current_step.status === 'in_progress' && !selectedWorkflow.current_step.is_automated && (
                        <Box sx={{ mt: 2 }}>
                          <Button 
                            variant="contained" 
                            color="primary" 
                            onClick={() => completeStep(selectedWorkflow.current_step.id)}
                            disabled={loading}
                          >
                            {loading ? <CircularProgress size={24} /> : 'Mark Step as Completed'}
                          </Button>
                        </Box>
                      )}
                    </Paper>
                  ) : (
                    <Typography variant="body2" color="textSecondary">
                      {selectedWorkflow.status === 'completed' ? 
                        'This workflow has been completed.' : 
                        'No active step found.'}
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              {selectedWorkflow.status === 'in_progress' && (
                <Button 
                  color="primary" 
                  onClick={() => advanceWorkflow(selectedWorkflow.id)}
                  disabled={loading || !selectedWorkflow.current_step || selectedWorkflow.current_step.status !== 'completed'}
                >
                  {loading ? <CircularProgress size={24} /> : 'Advance to Next Step'}
                </Button>
              )}
              <Button onClick={handleCloseDialog}>
                Close
              </Button>
            </DialogActions>
          </>
        ) : (
          <DialogContent>
            <CircularProgress />
          </DialogContent>
        )}
      </Dialog>
    </Box>
  );
};

export default WorkflowManagement; 