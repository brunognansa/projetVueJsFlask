import { defineStore } from 'pinia';
import axios from 'axios';

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    userProfile: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      par_page: 10,
      total: 0,
      pages: 0,
      a_suivant: false,
      a_precedent: false
    }
  }),
  
  getters: {
    getUsers: (state) => state.users,
    getUserProfile: (state) => state.userProfile,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    getPagination: (state) => state.pagination
  },
  
  actions: {
    async fetchUserProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/users/profile`);
        
        if (response.data.statut === 'succes') {
          this.userProfile = response.data.utilisateur;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement du profil';
      } finally {
        this.loading = false;
      }
    },
    
    async updateUserProfile(userData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.put(`http://localhost:5000/users/profile`, userData);
        
        if (response.data.statut === 'succes') {
          this.userProfile = response.data.utilisateur;
          
          // Update user in localStorage if it exists
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            const user = JSON.parse(storedUser);
            const updatedUser = { ...user, ...response.data.utilisateur };
            localStorage.setItem('user', JSON.stringify(updatedUser));
          }
          
          return response.data.utilisateur;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la mise à jour du profil';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    // Admin actions
    async fetchUsers(page = 1, perPage = 10) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/users`, {
          params: {
            page: page,
            par_page: perPage
          }
        });
        
        if (response.data.statut === 'succes') {
          this.users = response.data.utilisateurs;
          this.pagination = response.data.pagination;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement des utilisateurs';
      } finally {
        this.loading = false;
      }
    },
    
    async updateUserRole(userId, isAdmin) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.put(`http://localhost:5000/users/${userId}/role`, {
          est_admin: isAdmin
        });
        
        if (response.data.statut === 'succes') {
          // Update user in the users array if it exists
          const index = this.users.findIndex(user => user.id === userId);
          if (index !== -1) {
            this.users[index] = response.data.utilisateur;
          }
          
          return response.data.utilisateur;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la mise à jour du rôle';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async updateUserStatus(userId, isActive) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.put(`http://localhost:5000/users/${userId}/status`, {
          est_actif: isActive
        });
        
        if (response.data.statut === 'succes') {
          // Update user in the users array if it exists
          const index = this.users.findIndex(user => user.id === userId);
          if (index !== -1) {
            this.users[index] = response.data.utilisateur;
          }
          
          return response.data.utilisateur;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la mise à jour du statut';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});