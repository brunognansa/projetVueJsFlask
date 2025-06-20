import axios from 'axios';
import router from '../router';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to add auth token to requests
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token_acces');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  response => {
    return response;
  },
  async error => {
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't already tried to refresh the token
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Get the refresh token
        const refreshToken = localStorage.getItem('token_rafraichissement');
        
        if (!refreshToken) {
          // No refresh token, redirect to login
          router.push('/login');
          return Promise.reject(error);
        }
        
        // Try to refresh the token
        const response = await axios.post('http://localhost:5000/auth/refresh', {}, {
          headers: {
            'Authorization': `Bearer ${refreshToken}`
          }
        });
        
        if (response.data.statut === 'succes') {
          // Store the new token
          const newToken = response.data.token_acces;
          localStorage.setItem('token_acces', newToken);
          
          // Update the original request with the new token
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          
          // Retry the original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh token is invalid or expired, logout the user
        localStorage.removeItem('user');
        localStorage.removeItem('token_acces');
        localStorage.removeItem('token_rafraichissement');
        
        // Redirect to login
        router.push('/login');
        
        return Promise.reject(refreshError);
      }
    }
    
    // Handle other errors
    if (error.response) {
      // Server responded with an error status code
      console.error('API Error:', error.response.data);
      
      // Handle specific error codes
      switch (error.response.status) {
        case 403:
          // Forbidden - user doesn't have permission
          router.push('/');
          break;
        case 404:
          // Not found
          console.error('Resource not found');
          break;
        case 500:
          // Server error
          console.error('Server error');
          break;
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received:', error.request);
    } else {
      // Something else happened while setting up the request
      console.error('Error setting up request:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;