import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';

const Login = () => {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('password');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Try direct API call first if in advanced mode
      if (showAdvanced) {
        console.log('Using direct API call for debugging');
        
        // Try with email as username (correct method)
        try {
          console.log('Trying with email as username');
          const response = await api.post('auth/login/', { 
            username: email, 
            password: password 
          });
          console.log('Login successful with email as username', response.data);
          
          // Store token and set auth state
          if (response.data.key) {
            localStorage.setItem('token', response.data.key);
            window.location.href = '/'; // Force reload to apply token
          }
          return;
        } catch (err) {
          console.log('Login with email as username failed', err);
          
          if (err.response && err.response.data) {
            console.log('Error response data:', JSON.stringify(err.response.data));
          }
        }
        
        // Try with both fields (some implementations accept this)
        try {
          console.log('Trying with both username and email fields');
          const response = await api.post('auth/login/', { 
            username: email,
            email: email, 
            password: password 
          });
          console.log('Login successful with both fields', response.data);
          
          // Store token and set auth state
          if (response.data.key) {
            localStorage.setItem('token', response.data.key);
            window.location.href = '/'; // Force reload to apply token
          }
          return;
        } catch (err) {
          console.log('All direct API attempts failed');
          throw err;
        }
      } else {
        // Use the regular login function from AuthContext
        await login(email, password);
      }
    } catch (err) {
      console.error('Login error:', err);
      let errorMessage = 'An error occurred during login. Please try again.';
      
      if (err.response) {
        console.log('Error response data:', JSON.stringify(err.response.data));
        if (err.response.data.non_field_errors) {
          errorMessage = err.response.data.non_field_errors.join(', ');
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else if (typeof err.response.data === 'object') {
          // Get all error messages
          errorMessage = Object.entries(err.response.data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join('; ');
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            GDPR Compliance Tool
          </Typography>
          <Typography component="h2" variant="h6" align="center" sx={{ mb: 3 }}>
            Log In
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
            
            <FormControlLabel
              control={
                <Checkbox
                  value="advanced"
                  color="primary"
                  checked={showAdvanced}
                  onChange={(e) => setShowAdvanced(e.target.checked)}
                />
              }
              label="Advanced debugging mode"
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={isLoading}
            >
              {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
            
            {/* Default test credentials info */}
            <Typography variant="body2" color="text.secondary" align="center">
              Default: admin@example.com / password
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
