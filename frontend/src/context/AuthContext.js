import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      console.log('Found token in localStorage, attempting to validate...');
      api.get('users/me/')
        .then(response => {
          console.log('User validation successful:', response.data);
          setUser(response.data);
          setIsAuthenticated(true);
        })
        .catch((error) => {
          console.error('Token validation failed:', error);
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      console.log('No token found in localStorage');
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      console.log(`Attempting login for user: ${email}`);
      // Debug: log the full URL being used
      console.log('Login URL:', `${api.defaults.baseURL}auth/login/`);
      
      // Use the email as the username - this is what the server expects
      const response = await api.post('auth/login/', { username: email, password });
      console.log('Login successful, response:', response.data);
      
      // Store the token
      if (response.data.key) {
        console.log('Storing token:', response.data.key);
        localStorage.setItem('token', response.data.key);
      } else {
        console.warn('No token received in login response:', response.data);
      }
      
      setUser(response.data.user);
      setIsAuthenticated(true);
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response);
      if (error.response) {
        console.error('Error status:', error.response.status);
        console.error('Error data:', error.response.data);
      }
      throw error;
    }
  };

  const logout = async () => {
    try {
      console.log('Attempting logout...');
      await api.post('auth/logout/');
      console.log('Logout API call successful');
    } catch (error) {
      console.error('Logout error', error);
    } finally {
      console.log('Removing token and user data');
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};