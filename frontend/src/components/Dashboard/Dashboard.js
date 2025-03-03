import React from 'react';
import { Typography, Grid, Paper, Box } from '@mui/material';

const Dashboard = () => {
  return (
    <div>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6">Data Subject Requests</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">0</Typography>
              <Typography variant="body2" color="textSecondary">Pending Requests</Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6">Data Categories</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">0</Typography>
              <Typography variant="body2" color="textSecondary">Registered Categories</Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6">Compliance Status</Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="h3">-</Typography>
              <Typography variant="body2" color="textSecondary">Documentation Status</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </div>
  );
};

export default Dashboard;