import React, { useState } from 'react';
import { 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  FormControl, 
  FormLabel, 
  RadioGroup, 
  FormControlLabel, 
  Radio, 
  Checkbox, 
  CircularProgress, 
  Alert, 
  Snackbar 
} from '@mui/material';
import api from '../../services/api';

const DataSubjectRequestForm = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    request_type: 'access',
    request_details: '',
    agree_to_identity_verification: false
  });

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.agree_to_identity_verification) {
      setError('You must agree to identity verification to submit this request');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // First, check if this data subject exists
      let dataSubjectId = null;
      try {
        const subjectsResponse = await api.get('/data-subjects/', {
          params: { email: formData.email }
        });
        if (subjectsResponse.data.results && subjectsResponse.data.results.length > 0) {
          dataSubjectId = subjectsResponse.data.results[0].id;
        }
      } catch (err) {
        // Ignore errors here, we'll create a new data subject if needed
        console.log('Data subject not found, will create new one');
      }
      
      // If no existing data subject, create one
      if (!dataSubjectId) {
        const newSubjectResponse = await api.post('/data-subjects/', {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          data_processing_consent: true
        });
        dataSubjectId = newSubjectResponse.data.id;
      }
      
      // Create the data subject request
      const requestResponse = await api.post('/data-subject-requests/', {
        data_subject_name: `${formData.first_name} ${formData.last_name}`,
        data_subject_email: formData.email,
        request_type: formData.request_type,
        request_details: formData.request_details
      });
      
      // Start the appropriate workflow for this request type
      let workflowType;
      switch (formData.request_type) {
        case 'access':
          workflowType = 'subject_access';
          break;
        case 'erasure':
          workflowType = 'erasure';
          break;
        case 'rectification':
          workflowType = 'rectification';
          break;
        default:
          workflowType = 'subject_access';
      }
      
      // Find a workflow template for this type
      const templatesResponse = await api.get('/workflow-templates/', {
        params: { workflow_type: workflowType }
      });
      
      if (templatesResponse.data.results && templatesResponse.data.results.length > 0) {
        const templateId = templatesResponse.data.results[0].id;
        
        // Create a workflow from the template
        await api.post(`/workflow-templates/${templateId}/create_workflow/`, {
          data_subject_id: dataSubjectId,
          request_id: requestResponse.data.id
        });
      }
      
      setSuccess(true);
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        request_type: 'access',
        request_details: '',
        agree_to_identity_verification: false
      });
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      console.error('Error submitting request:', err);
      setError(err.response?.data?.detail || 'Failed to submit your request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: '800px', mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom>
        GDPR Data Subject Request Form
      </Typography>
      
      <Typography variant="body2" color="textSecondary" paragraph>
        Use this form to submit a request regarding your personal data. Under the General Data Protection Regulation (GDPR),
        you have the right to access, rectify, erase, restrict or object to the processing of your personal data.
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              name="first_name"
              label="First Name"
              value={formData.first_name}
              onChange={handleChange}
              fullWidth
              required
            />
            <TextField
              name="last_name"
              label="Last Name"
              value={formData.last_name}
              onChange={handleChange}
              fullWidth
              required
            />
          </Box>
          
          <TextField
            name="email"
            label="Email Address"
            type="email"
            value={formData.email}
            onChange={handleChange}
            fullWidth
            required
          />
          
          <FormControl component="fieldset">
            <FormLabel component="legend">Request Type</FormLabel>
            <RadioGroup
              name="request_type"
              value={formData.request_type}
              onChange={handleChange}
            >
              <FormControlLabel value="access" control={<Radio />} label="Right to Access (request a copy of your data)" />
              <FormControlLabel value="rectification" control={<Radio />} label="Right to Rectification (correct inaccurate data)" />
              <FormControlLabel value="erasure" control={<Radio />} label="Right to Erasure (delete your data)" />
              <FormControlLabel value="restriction" control={<Radio />} label="Right to Restrict Processing" />
              <FormControlLabel value="portability" control={<Radio />} label="Right to Data Portability (receive data in a reusable format)" />
              <FormControlLabel value="objection" control={<Radio />} label="Right to Object to Processing" />
            </RadioGroup>
          </FormControl>
          
          <TextField
            name="request_details"
            label="Request Details"
            multiline
            rows={4}
            value={formData.request_details}
            onChange={handleChange}
            fullWidth
            placeholder="Please provide any additional details about your request..."
          />
          
          <FormControlLabel
            control={
              <Checkbox
                name="agree_to_identity_verification"
                checked={formData.agree_to_identity_verification}
                onChange={handleChange}
                required
              />
            }
            label="I understand that identity verification may be required to process this request"
          />
          
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Submit Request'}
          </Button>
        </Box>
      </form>
      
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity="success">
          Your request was submitted successfully. You will receive a confirmation email shortly.
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default DataSubjectRequestForm; 