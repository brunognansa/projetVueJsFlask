import { defineStore } from 'pinia';
import axios from 'axios';

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [],
    loading: false,
    pagination: null,
    error: null
  }),

  actions: {
    async fetchCategories(page = 1) {
      this.loading = true;
      try {
        const response = await axios.get(`/api/categories?page=${page}`);
        this.categories = response.data.categories;
        this.pagination = response.data.pagination;
      } catch (error) {
        this.error = error.response?.data?.message || 'Erreur lors du chargement des catégories';
      } finally {
        this.loading = false;
      }
    },

    async createCategory(categoryData) {
      try {
        const response = await axios.post('/api/categories', categoryData);
        this.categories.push(response.data.categorie);
        return { success: true, data: response.data.categorie };
      } catch (error) {
        return { success: false, error: error.response?.data?.message };
      }
    },

    async updateCategory(categoryId, categoryData) {
      try {
        const response = await axios.put(`/api/categories/${categoryId}`, categoryData);
        const index = this.categories.findIndex(c => c.id === categoryId);
        if (index !== -1) {
          this.categories[index] = response.data.categorie;
        }
        return { success: true, data: response.data.categorie };
      } catch (error) {
        return { success: false, error: error.response?.data?.message };
      }
    }
  }
});
