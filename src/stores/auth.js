import { defineStore } from 'pinia';
import axios from 'axios';
import router from '../router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token_acces') || null,
    refreshToken: localStorage.getItem('token_rafraichissement') || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user && state.user.est_admin,
    getUser: (state) => state.user,
    getError: (state) => state.error
  },
  
  actions: {
    async login(credentials) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.post('http://localhost:5000/auth/login', credentials);
        
        if (response.data.statut === 'succes') {
          this.user = response.data.utilisateur;
          this.token = response.data.tokens.token_acces;
          this.refreshToken = response.data.tokens.token_rafraichissement;
          
          // Store in localStorage
          localStorage.setItem('user', JSON.stringify(this.user));
          localStorage.setItem('token_acces', this.token);
          localStorage.setItem('token_rafraichissement', this.refreshToken);
          
          // Set default Authorization header for all requests
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
          
          // Redirect to home or intended page
          const redirectPath = router.currentRoute.value.query.redirect || '/';
          router.push(redirectPath);
          
          return true;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la connexion';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async register(userData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.post('http://localhost:5000/auth/register', userData);
        
        if (response.data.statut === 'succes') {
          // Redirect to login page after successful registration
          router.push('/login');
          return true;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de l\'inscription';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async logout() {
      this.loading = true;
      
      try {
        // Call logout API if token exists
        if (this.token) {
          await axios.post('http://localhost:5000/auth/logout', {}, {
            headers: {
              'Authorization': `Bearer ${this.token}`
            }
          });
        }
      } catch (error) {
        console.error('Erreur lors de la déconnexion:', error);
      } finally {
        // Clear state and localStorage regardless of API call result
        this.user = null;
        this.token = null;
        this.refreshToken = null;
        
        localStorage.removeItem('user');
        localStorage.removeItem('token_acces');
        localStorage.removeItem('token_rafraichissement');
        
        // Remove Authorization header
        delete axios.defaults.headers.common['Authorization'];
        
        // Redirect to login page
        router.push('/login');
        
        this.loading = false;
      }
    },
    
    async refreshAccessToken() {
      try {
        if (!this.refreshToken) {
          throw new Error('No refresh token available');
        }
        
        const response = await axios.post('http://localhost:5000/auth/refresh', {}, {
          headers: {
            'Authorization': `Bearer ${this.refreshToken}`
          }
        });
        
        if (response.data.statut === 'succes') {
          this.token = response.data.token_acces;
          localStorage.setItem('token_acces', this.token);
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
          return this.token;
        }
      } catch (error) {
        // If refresh token is invalid or expired, logout the user
        this.logout();
        throw error;
      }
    },
    
    async changePassword(passwordData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.post('http://localhost:5000/auth/change-password', passwordData, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        });
        
        if (response.data.statut === 'succes') {
          return true;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du changement de mot de passe';
        return false;
      } finally {
        this.loading = false;
      }
    }
  }
});