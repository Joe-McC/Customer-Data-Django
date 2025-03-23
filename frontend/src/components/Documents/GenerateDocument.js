import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Grid,
  Divider,
  Link,
  Snackbar
} from '@mui/material';
import api from '../../services/api';

const GenerateDocument = () => {
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [dataSubjects, setDataSubjects] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedDataSubject, setSelectedDataSubject] = useState('');
  const [generatedDocument, setGeneratedDocument] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch document templates
      const templatesResponse = await api.get('/documents/', {
        params: {
          is_template: true,
          status: 'active'
        }
      });
      
      // Fetch data subjects
      const subjectsResponse = await api.get('/data-subjects/');
      
      setTemplates(templatesResponse.data.results || []);
      setDataSubjects(subjectsResponse.data.results || []);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load templates or data subjects.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDocument = async () => {
    if (!selectedTemplate || !selectedDataSubject) {
      setError('Please select both a template and a data subject.');
      return;
    }
    
    try {
      setGenerating(true);
      setError(null);
      
      // Call the generate document endpoint
      const response = await api.post(`/generate-document/${selectedTemplate}/`, {
        data_subject_id: selectedDataSubject
      });
      
      setGeneratedDocument(response.data);
      setSuccess(true);
    } catch (err) {
      console.error('Error generating document:', err);
      setError('Failed to generate document. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  const handleTemplateChange = (event) => {
    setSelectedTemplate(event.target.value);
  };

  const handleDataSubjectChange = (event) => {
    setSelectedDataSubject(event.target.value);
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
        Generate GDPR Document
      </Typography>
      
      <Typography variant="body2" color="textSecondary" paragraph>
        Generate personalized GDPR compliance documents for specific data subjects using document templates.
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Document Template</InputLabel>
            <Select
              value={selectedTemplate}
              onChange={handleTemplateChange}
              label="Document Template"
            >
              <MenuItem value="">
                <em>Select a template</em>
              </MenuItem>
              {templates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.title} ({template.document_type}) - v{template.version}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Data Subject</InputLabel>
            <Select
              value={selectedDataSubject}
              onChange={handleDataSubjectChange}
              label="Data Subject"
            >
              <MenuItem value="">
                <em>Select a data subject</em>
              </MenuItem>
              {dataSubjects.map((subject) => (
                <MenuItem key={subject.id} value={subject.id}>
                  {subject.first_name} {subject.last_name} ({subject.email})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleGenerateDocument}
          disabled={generating || !selectedTemplate || !selectedDataSubject}
        >
          {generating ? <CircularProgress size={24} /> : 'Generate Document'}
        </Button>
      </Box>
      
      {generatedDocument && (
        <>
          <Divider sx={{ my: 3 }} />
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generated Document
            </Typography>
            
            <Paper elevation={1} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
              <Typography variant="subtitle1">
                {generatedDocument.title}
              </Typography>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Generated on: {new Date(generatedDocument.created_at).toLocaleString()}
              </Typography>
              
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                {generatedDocument.file && (
                  <Button
                    variant="outlined"
                    component={Link}
                    href={generatedDocument.file}
                    target="_blank"
                  >
                    Download Document
                  </Button>
                )}
                <Button
                  variant="outlined"
                  component={Link}
                  href={`/documents/${generatedDocument.id}`}
                  target="_blank"
                >
                  View Document
                </Button>
              </Box>
            </Paper>
          </Box>
        </>
      )}
      
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity="success">
          Document generated successfully!
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default GenerateDocument; 