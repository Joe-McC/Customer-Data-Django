import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import api from '../../services/api';

const DocumentTemplateEditor = ({ templateId, onSave, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [template, setTemplate] = useState({
    title: '',
    document_type: 'privacy_policy',
    content: '',
    is_template: true,
    template_variables: {},
    status: 'draft',
    version: '1.0'
  });
  const [variableDialog, setVariableDialog] = useState(false);
  const [currentVariable, setCurrentVariable] = useState('');
  const [availableVariables, setAvailableVariables] = useState([
    { key: '{{subject_first_name}}', description: 'Data Subject First Name' },
    { key: '{{subject_last_name}}', description: 'Data Subject Last Name' },
    { key: '{{subject_email}}', description: 'Data Subject Email' },
    { key: '{{subject_full_name}}', description: 'Data Subject Full Name' },
    { key: '{{organization_name}}', description: 'Organization Name' },
    { key: '{{organization_address}}', description: 'Organization Address' },
    { key: '{{current_date}}', description: 'Current Date' },
    { key: '{{expiry_date}}', description: 'Data Expiry Date' }
  ]);

  useEffect(() => {
    if (templateId) {
      fetchTemplate();
    }
  }, [templateId]);

  const fetchTemplate = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/documents/${templateId}/`);
      setTemplate(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching template:', err);
      setError('Failed to load document template.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setTemplate({
      ...template,
      [name]: value
    });
  };

  const handleInsertVariable = (variable) => {
    const textField = document.getElementById('content-field');
    const cursorPosition = textField.selectionStart;
    
    const contentBefore = template.content.substring(0, cursorPosition);
    const contentAfter = template.content.substring(cursorPosition);
    
    const newContent = contentBefore + variable.key + contentAfter;
    setTemplate({
      ...template,
      content: newContent
    });
    
    setVariableDialog(false);
  };

  const handleOpenVariableDialog = () => {
    setVariableDialog(true);
  };

  const handleCloseVariableDialog = () => {
    setVariableDialog(false);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      let response;
      if (templateId) {
        response = await api.put(`/documents/${templateId}/`, template);
      } else {
        response = await api.post('/documents/', template);
      }
      
      if (onSave) {
        onSave(response.data);
      }
    } catch (err) {
      console.error('Error saving template:', err);
      setError('Failed to save document template.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" component="h2" gutterBottom>
        {templateId ? 'Edit Document Template' : 'Create Document Template'}
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            name="title"
            label="Template Title"
            value={template.title}
            onChange={handleChange}
            fullWidth
            required
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Document Type</InputLabel>
            <Select
              name="document_type"
              value={template.document_type}
              onChange={handleChange}
              label="Document Type"
            >
              <MenuItem value="privacy_policy">Privacy Policy</MenuItem>
              <MenuItem value="consent_form">Consent Form</MenuItem>
              <MenuItem value="dpa">Data Processing Agreement</MenuItem>
              <MenuItem value="subject_access_response">Subject Access Request Response</MenuItem>
              <MenuItem value="erasure_confirmation">Right to Erasure Confirmation</MenuItem>
              <MenuItem value="data_portability">Data Portability Export</MenuItem>
              <MenuItem value="other">Other Document</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              name="status"
              value={template.status}
              onChange={handleChange}
              label="Status"
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            name="version"
            label="Version"
            value={template.version}
            onChange={handleChange}
            fullWidth
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={12}>
          <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
            Template Content
            <Button
              size="small"
              variant="outlined"
              onClick={handleOpenVariableDialog}
              sx={{ ml: 2 }}
            >
              Insert Variable
            </Button>
          </Typography>
          
          <TextField
            id="content-field"
            name="content"
            value={template.content}
            onChange={handleChange}
            fullWidth
            multiline
            rows={15}
            margin="normal"
            placeholder="Enter your document template content here. Use variables like {{subject_first_name}} that will be replaced with actual values when the document is generated."
          />
          
          <Typography variant="caption" color="textSecondary">
            Use variables like {{subject_first_name}} that will be replaced with actual values when generated.
          </Typography>
        </Grid>
        
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3, gap: 2 }}>
            {onCancel && (
              <Button onClick={onCancel} disabled={saving}>
                Cancel
              </Button>
            )}
            <Button
              variant="contained"
              color="primary"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? <CircularProgress size={24} /> : (templateId ? 'Update Template' : 'Create Template')}
            </Button>
          </Box>
        </Grid>
      </Grid>
      
      {/* Variable Selection Dialog */}
      <Dialog
        open={variableDialog}
        onClose={handleCloseVariableDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Insert Template Variable</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2" paragraph>
            Select a variable to insert into your document template. These will be automatically 
            replaced with the appropriate values when the document is generated.
          </Typography>
          
          <List dense>
            {availableVariables.map((variable) => (
              <ListItem
                key={variable.key}
                button
                onClick={() => handleInsertVariable(variable)}
                divider
              >
                <ListItemText
                  primary={variable.description}
                  secondary={variable.key}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseVariableDialog}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default DocumentTemplateEditor; 