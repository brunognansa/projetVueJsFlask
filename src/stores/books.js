import { defineStore } from 'pinia';
import axios from 'axios';

export const useBooksStore = defineStore('books', {
  state: () => ({
    books: [],
    book: null,
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
    getBooks: (state) => state.books,
    getBook: (state) => state.book,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    getPagination: (state) => state.pagination
  },
  
  actions: {
    async fetchBooks(page = 1, perPage = 10) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/books`, {
          params: {
            page: page,
            par_page: perPage
          }
        });
        
        if (response.data.statut === 'succes') {
          this.books = response.data.livres;
          this.pagination = response.data.pagination;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement des livres';
      } finally {
        this.loading = false;
      }
    },
    
    async fetchBookById(id) {
      this.loading = true;
      this.error = null;
      this.book = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/books/${id}`);
        
        if (response.data.statut === 'succes') {
          this.book = response.data.livre;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors du chargement du livre';
      } finally {
        this.loading = false;
      }
    },
    
    async searchBooks(term, page = 1, perPage = 10) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`http://localhost:5000/books/search`, {
          params: {
            terme: term,
            page: page,
            par_page: perPage
          }
        });
        
        if (response.data.statut === 'succes') {
          this.books = response.data.livres;
          this.pagination = response.data.pagination;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la recherche de livres';
      } finally {
        this.loading = false;
      }
    },
    
    async createBook(bookData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`http://localhost:5000/books`, bookData);
        
        if (response.data.statut === 'succes') {
          return response.data.livre;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la création du livre';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async updateBook(id, bookData) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.put(`http://localhost:5000/books/${id}`, bookData);
        
        if (response.data.statut === 'succes') {
          // Update the book in the store if it's currently loaded
          if (this.book && this.book.id === id) {
            this.book = response.data.livre;
          }
          
          // Update the book in the books array if it exists
          const index = this.books.findIndex(book => book.id === id);
          if (index !== -1) {
            this.books[index] = response.data.livre;
          }
          
          return response.data.livre;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la mise à jour du livre';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    async deleteBook(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await axios.delete(`http://localhost:5000/books/${id}`);
        
        if (response.data.statut === 'succes') {
          // Remove the book from the books array if it exists
          this.books = this.books.filter(book => book.id !== id);
          
          // Clear the book if it's currently loaded
          if (this.book && this.book.id === id) {
            this.book = null;
          }
          
          return true;
        }
      } catch (error) {
        this.error = error.response?.data?.message || 'Une erreur est survenue lors de la suppression du livre';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});