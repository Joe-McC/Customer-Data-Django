import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Layout from './components/Layout/Layout';

// Import pages
import Dashboard from './components/Dashboard/Dashboard';
import DataInventory from './components/DataInventory/DataInventory';
import SubjectRequests from './components/Requests/DataSubjectRequestList';
import Documents from './components/Documents/DocumentGenerator';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/data-inventory" element={<DataInventory />} />
            <Route path="/subject-requests" element={<SubjectRequests />} />
            <Route path="/documents" element={<Documents />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;