import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/';
console.log('API URL:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      console.log(`Adding token to request: ${config.url}`);
      // Make sure we use 'Token' format, not 'Bearer'
      config.headers.Authorization = `Token ${token}`;
    } else {
      console.log(`Request without token: ${config.url}`);
    }
    
    // Log all request data for debugging
    if (config.data) {
      console.log('Request data:', JSON.stringify(config.data).slice(0, 500));
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptors for debugging
api.interceptors.response.use(
  (response) => {
    console.log(`API Response from ${response.config.url}:`, 
                 response.status, 
                 response.data ? '[data available]' : '[no data]');
    
    // For debugging authentication issues
    if (response.config.url.includes('auth/login')) {
      console.log('Authentication response:', JSON.stringify(response.data));
    }
    
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`API Error from ${error.config.url}:`, 
                   error.response.status, 
                   error.response.data);
                   
      // Handle 401 errors by clearing token and redirecting
      if (error.response.status === 401) {
        console.error('Authentication error. Clearing token.');
        localStorage.removeItem('token');
      }
    } else {
      console.error('API Error without response:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;