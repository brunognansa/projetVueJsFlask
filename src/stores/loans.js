import { defineStore } from 'pinia';
import axios from 'axios';

export const useLoansStore = defineStore('loans', {
  state: () => ({
    activeLoans: [],
    loanHistory: [],
    allLoans: [], // For admin
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
    getActiveLoans: (state) => state.activeLoans,
    getLoanHistory: (state) => state.loanHistory,
    getAllLoans: (state) => state.allLoans,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    getPagination: (state) => state.pagination
  },
  
  actions: {
    async fetchActiveLoans(page = 1, perPage = 10) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/loans/active`, {
          params: {
            page: page,
            par_page: perPage
          }
        });
        
        if (response.data.statut === 'succes') {
          this.activeLoans = response.data.emprunts;
          this.pagination = response.data.pagination;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement des emprunts actifs';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchLoanHistory(page = 1, perPage = 10) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/loans/history`, {
          params: {
            page: page,
            par_page: perPage
          }
        });
        
        if (response.data.statut === 'succes') {
          this.loanHistory = response.data.emprunts;
          this.pagination = response.data.pagination;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement de l\'historique des emprunts';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchAllLoans(page = 1, perPage = 10, activeOnly = false) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/loans`, {
          params: {
            page: page,
            par_page: perPage,
            actif_seulement: activeOnly
          }
        });
        
        if (response.data.statut === 'succes') {
          this.allLoans = response.data.emprunts;
          this.pagination = response.data.pagination;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement des emprunts';
      } finally {
        this.loading = false;
      }
    },
    
    async borrowBook(loanData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`http://localhost:5000/loans`, loanData);
        
        if (response.data.statut === 'succes') {
          // Add the new loan to active loans if they're loaded
          if (this.activeLoans.length > 0) {
            this.activeLoans = [response.data.emprunt, ...this.activeLoans];
          }
          
          return response.data.emprunt;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de l\'emprunt du livre';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async returnBook(loanId) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.patch(`http://localhost:5000/loans/${loanId}/return`);
        
        if (response.data.statut === 'succes') {
          // Update the loan in active loans if it exists
          const index = this.activeLoans.findIndex(loan => loan.id === loanId);
          if (index !== -1) {
            // Remove from active loans
            this.activeLoans.splice(index, 1);
            
            // Add to history if it's loaded
            if (this.loanHistory.length > 0) {
              this.loanHistory = [response.data.emprunt, ...this.loanHistory];
            }
          }
          
          // Update in all loans if they're loaded (for admin)
          const allIndex = this.allLoans.findIndex(loan => loan.id === loanId);
          if (allIndex !== -1) {
            this.allLoans[allIndex] = response.data.emprunt;
          }
          
          return response.data.emprunt;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du retour du livre';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});