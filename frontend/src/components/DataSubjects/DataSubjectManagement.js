import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Grid,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Tooltip,
  Pagination
} from '@mui/material';
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import api from '../../services/api';

const formatDate = (dateString) => {
  if (!dateString) return 'Not set';
  return new Date(dateString).toLocaleDateString();
};

const DataSubjectManagement = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSubjects, setDataSubjects] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedDataSubject, setSelectedDataSubject] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);
  const [consentHistory, setConsentHistory] = useState([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmDeleteDialogOpen, setConfirmDeleteDialogOpen] = useState(false);
  const [dataSubjectToDelete, setDataSubjectToDelete] = useState(null);

  useEffect(() => {
    fetchDataSubjects();
  }, [selectedTab, currentPage, searchTerm]);

  const fetchDataSubjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Determine filter based on tab
      let params = {
        page: currentPage,
        page_size: 10
      };
      
      if (searchTerm) {
        params.search = searchTerm;
      }
      
      switch (selectedTab) {
        case 1: // Expiring Soon
          params.expiring_soon = true;
          break;
        case 2: // With Marketing Consent
          params.marketing_consent = true;
          break;
        case 3: // Without Data Processing Consent
          params.data_processing_consent = false;
          break;
        default:
          // No additional filter for "All"
          break;
      }
      
      const response = await api.get('/data-subjects/', { params });
      
      setDataSubjects(response.data.results || []);
      setTotalPages(Math.ceil(response.data.count / 10) || 1);
    } catch (err) {
      console.error('Error fetching data subjects:', err);
      setError('Failed to load data subjects. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchConsentHistory = async (dataSubjectId) => {
    try {
      setLoading(true);
      const response = await api.get(`/data-subjects/${dataSubjectId}/consent_activities/`);
      setConsentHistory(response.data || []);
      setHistoryDialogOpen(true);
    } catch (err) {
      console.error('Error fetching consent history:', err);
      setError('Failed to load consent history');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
    setCurrentPage(1); // Reset to first page when changing tabs
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setCurrentPage(1); // Reset to first page when searching
  };

  const handlePageChange = (event, value) => {
    setCurrentPage(value);
  };

  const handleEditClick = (dataSubject) => {
    setSelectedDataSubject({...dataSubject});
    setEditDialogOpen(true);
  };

  const handleHistoryClick = (dataSubjectId) => {
    fetchConsentHistory(dataSubjectId);
  };

  const handleDeleteClick = (dataSubject) => {
    setDataSubjectToDelete(dataSubject);
    setConfirmDeleteDialogOpen(true);
  };

  const handleEditDialogClose = () => {
    setEditDialogOpen(false);
  };

  const handleHistoryDialogClose = () => {
    setHistoryDialogOpen(false);
  };

  const handleConfirmDeleteDialogClose = () => {
    setConfirmDeleteDialogOpen(false);
  };

  const handleEditInputChange = (e) => {
    const { name, value, checked, type } = e.target;
    setSelectedDataSubject({
      ...selectedDataSubject,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSaveEdit = async () => {
    try {
      setLoading(true);
      await api.put(`/data-subjects/${selectedDataSubject.id}/`, selectedDataSubject);
      
      // Record consent changes
      const consentTypes = [
        { field: 'marketing_consent', type: 'marketing' },
        { field: 'data_processing_consent', type: 'data_processing' },
        { field: 'cookie_consent', type: 'cookies' }
      ];
      
      for (const consent of consentTypes) {
        if (selectedDataSubject[`${consent.field}`] !== dataSubjects.find(ds => ds.id === selectedDataSubject.id)[`${consent.field}`]) {
          const activity_type = selectedDataSubject[`${consent.field}`] ? 'consent_given' : 'consent_withdrawn';
          await api.post(`/data-subjects/${selectedDataSubject.id}/record_consent/`, {
            activity_type,
            consent_type: consent.type,
            notes: 'Updated via admin interface'
          });
        }
      }
      
      setEditDialogOpen(false);
      fetchDataSubjects(); // Refresh the list
    } catch (err) {
      console.error('Error updating data subject:', err);
      setError('Failed to update data subject');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmDelete = async () => {
    try {
      setLoading(true);
      await api.delete(`/data-subjects/${dataSubjectToDelete.id}/`);
      setConfirmDeleteDialogOpen(false);
      fetchDataSubjects(); // Refresh the list
    } catch (err) {
      console.error('Error deleting data subject:', err);
      setError('Failed to delete data subject');
    } finally {
      setLoading(false);
    }
  };

  const isDateExpiringSoon = (dateString) => {
    if (!dateString) return false;
    
    const expiryDate = new Date(dateString);
    const now = new Date();
    const thirtyDaysInMs = 30 * 24 * 60 * 60 * 1000;
    
    return expiryDate > now && (expiryDate - now) < thirtyDaysInMs;
  };
  
  const isDateExpired = (dateString) => {
    if (!dateString) return false;
    
    const expiryDate = new Date(dateString);
    const now = new Date();
    
    return expiryDate < now;
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Subject Management
      </Typography>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <TextField
          placeholder="Search data subjects..."
          value={searchTerm}
          onChange={handleSearchChange}
          variant="outlined"
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: '300px' }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={() => {
            setSelectedDataSubject({
              first_name: '',
              last_name: '',
              email: '',
              phone: '',
              marketing_consent: false,
              data_processing_consent: false,
              cookie_consent: false,
              notes: ''
            });
            setEditDialogOpen(true);
          }}
        >
          Add New Data Subject
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="All Data Subjects" />
          <Tab label="Expiring Soon" />
          <Tab label="With Marketing Consent" />
          <Tab label="Without Processing Consent" />
        </Tabs>
      </Paper>
      
      {loading && !dataSubjects.length ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : dataSubjects.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            No data subjects found with the selected filter.
          </Typography>
        </Paper>
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Data Expiry</TableCell>
                  <TableCell>Consent Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dataSubjects.map((subject) => (
                  <TableRow key={subject.id}>
                    <TableCell>
                      {subject.first_name} {subject.last_name}
                    </TableCell>
                    <TableCell>{subject.email}</TableCell>
                    <TableCell>
                      {isDateExpiringSoon(subject.data_expiry_date) ? (
                        <Tooltip title="Expiring soon">
                          <Chip
                            icon={<WarningIcon />}
                            label={formatDate(subject.data_expiry_date)}
                            color="warning"
                            size="small"
                          />
                        </Tooltip>
                      ) : isDateExpired(subject.data_expiry_date) ? (
                        <Tooltip title="Expired">
                          <Chip
                            label={formatDate(subject.data_expiry_date)}
                            color="error"
                            size="small"
                          />
                        </Tooltip>
                      ) : (
                        formatDate(subject.data_expiry_date)
                      )}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Data Processing Consent">
                          <Chip
                            label="Processing"
                            color={subject.data_processing_consent ? "success" : "default"}
                            size="small"
                          />
                        </Tooltip>
                        <Tooltip title="Marketing Consent">
                          <Chip
                            label="Marketing"
                            color={subject.marketing_consent ? "success" : "default"}
                            size="small"
                          />
                        </Tooltip>
                        <Tooltip title="Cookie Consent">
                          <Chip
                            label="Cookies"
                            color={subject.cookie_consent ? "success" : "default"}
                            size="small"
                          />
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditClick(subject)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleHistoryClick(subject.id)}
                      >
                        <HistoryIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteClick(subject)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Pagination
              count={totalPages}
              page={currentPage}
              onChange={handlePageChange}
              color="primary"
            />
          </Box>
        </>
      )}
      
      {/* Edit/Add Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={handleEditDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedDataSubject?.id ? 'Edit Data Subject' : 'Add New Data Subject'}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                name="first_name"
                label="First Name"
                value={selectedDataSubject?.first_name || ''}
                onChange={handleEditInputChange}
                fullWidth
                margin="normal"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                name="last_name"
                label="Last Name"
                value={selectedDataSubject?.last_name || ''}
                onChange={handleEditInputChange}
                fullWidth
                margin="normal"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                name="email"
                label="Email"
                type="email"
                value={selectedDataSubject?.email || ''}
                onChange={handleEditInputChange}
                fullWidth
                margin="normal"
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                name="phone"
                label="Phone"
                value={selectedDataSubject?.phone || ''}
                onChange={handleEditInputChange}
                fullWidth
                margin="normal"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                Consent Settings
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <FormControlLabel
                  control={
                    <Switch
                      name="data_processing_consent"
                      checked={selectedDataSubject?.data_processing_consent || false}
                      onChange={handleEditInputChange}
                      color="primary"
                    />
                  }
                  label="Data Processing Consent"
                />
                <FormControlLabel
                  control={
                    <Switch
                      name="marketing_consent"
                      checked={selectedDataSubject?.marketing_consent || false}
                      onChange={handleEditInputChange}
                      color="primary"
                    />
                  }
                  label="Marketing Consent"
                />
                <FormControlLabel
                  control={
                    <Switch
                      name="cookie_consent"
                      checked={selectedDataSubject?.cookie_consent || false}
                      onChange={handleEditInputChange}
                      color="primary"
                    />
                  }
                  label="Cookie Consent"
                />
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                name="notes"
                label="Notes"
                value={selectedDataSubject?.notes || ''}
                onChange={handleEditInputChange}
                fullWidth
                multiline
                rows={3}
                margin="normal"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditDialogClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveEdit}
            color="primary"
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Consent History Dialog */}
      <Dialog
        open={historyDialogOpen}
        onClose={handleHistoryDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Consent Activity History</DialogTitle>
        <DialogContent dividers>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : consentHistory.length === 0 ? (
            <Typography variant="body1" color="textSecondary" sx={{ textAlign: 'center', py: 2 }}>
              No consent activity history found.
            </Typography>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Activity</TableCell>
                    <TableCell>Consent Type</TableCell>
                    <TableCell>Date & Time</TableCell>
                    <TableCell>IP Address</TableCell>
                    <TableCell>Notes</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {consentHistory.map((activity) => (
                    <TableRow key={activity.id}>
                      <TableCell>{activity.activity_type}</TableCell>
                      <TableCell>{activity.consent_type || 'N/A'}</TableCell>
                      <TableCell>{new Date(activity.timestamp).toLocaleString()}</TableCell>
                      <TableCell>{activity.ip_address || 'N/A'}</TableCell>
                      <TableCell>{activity.notes || 'N/A'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleHistoryDialogClose}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Confirm Delete Dialog */}
      <Dialog
        open={confirmDeleteDialogOpen}
        onClose={handleConfirmDeleteDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography variant="body1">
            Are you sure you want to delete the data subject: {dataSubjectToDelete?.first_name} {dataSubjectToDelete?.last_name}?
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 2 }}>
            Warning: This action cannot be undone. All associated consent records and documents will also be deleted.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleConfirmDeleteDialogClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataSubjectManagement; 