<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBooksStore } from '../../stores/books';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const booksStore = useBooksStore();
const authStore = useAuthStore();

const loading = ref(false);
const error = ref('');
const success = ref('');

// Form data
const bookData = ref({
  titre: '',
  auteur: '',
  isbn: '',
  date_publication: '',
  quantite: 1
});

// Form validation
const formErrors = ref({
  titre: '',
  auteur: '',
  isbn: '',
  date_publication: '',
  quantite: ''
});

// Check if user is admin
const isAdmin = computed(() => authStore.isAdmin);

// Redirect non-admin users
onMounted(() => {
  if (!isAdmin.value) {
    router.push('/');
  }
});

// Validate form
const validateForm = () => {
  let isValid = true;
  formErrors.value = {
    titre: '',
    auteur: '',
    isbn: '',
    date_publication: '',
    quantite: ''
  };
  
  // Validate title
  if (!bookData.value.titre.trim()) {
    formErrors.value.titre = 'Le titre est requis';
    isValid = false;
  } else if (bookData.value.titre.length < 2) {
    formErrors.value.titre = 'Le titre doit contenir au moins 2 caractères';
    isValid = false;
  }
  
  // Validate author
  if (!bookData.value.auteur.trim()) {
    formErrors.value.auteur = 'L\'auteur est requis';
    isValid = false;
  } else if (bookData.value.auteur.length < 2) {
    formErrors.value.auteur = 'L\'auteur doit contenir au moins 2 caractères';
    isValid = false;
  }
  
  // Validate ISBN
  if (!bookData.value.isbn.trim()) {
    formErrors.value.isbn = 'L\'ISBN est requis';
    isValid = false;
  } else if (bookData.value.isbn.length < 10 || bookData.value.isbn.length > 20) {
    formErrors.value.isbn = 'L\'ISBN doit contenir entre 10 et 20 caractères';
    isValid = false;
  }
  
  // Validate publication date (optional)
  if (bookData.value.date_publication) {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(bookData.value.date_publication)) {
      formErrors.value.date_publication = 'La date doit être au format YYYY-MM-DD';
      isValid = false;
    }
  }
  
  // Validate quantity
  if (!bookData.value.quantite) {
    formErrors.value.quantite = 'La quantité est requise';
    isValid = false;
  } else if (bookData.value.quantite < 1) {
    formErrors.value.quantite = 'La quantité doit être au moins 1';
    isValid = false;
  }
  
  return isValid;
};

// Create book
const createBook = async () => {
  if (!validateForm()) {
    return;
  }
  
  loading.value = true;
  error.value = '';
  success.value = '';
  
  try {
    const book = await booksStore.createBook(bookData.value);
    
    if (book) {
      success.value = 'Livre ajouté avec succès';
      
      // Reset form
      bookData.value = {
        titre: '',
        auteur: '',
        isbn: '',
        date_publication: '',
        quantite: 1
      };
      
      // Redirect to book details after a short delay
      setTimeout(() => {
        router.push(`/books/${book.id}`);
      }, 1500);
    }
  } catch (err) {
    error.value = booksStore.getError || 'Une erreur est survenue lors de la création du livre';
  } finally {
    loading.value = false;
  }
};

// Cancel and go back
const cancel = () => {
  router.back();
};
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Ajouter un Livre</h1>
      <button @click="cancel" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Retour
      </button>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <!-- Success Message -->
    <div v-if="success" class="alert alert-success" role="alert">
      {{ success }}
    </div>
    
    <!-- Book Form -->
    <div class="card shadow-sm">
      <div class="card-body">
        <form @submit.prevent="createBook">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="titre" class="form-label">Titre <span class="text-danger">*</span></label>
              <input 
                type="text" 
                class="form-control" 
                :class="{ 'is-invalid': formErrors.titre }"
                id="titre" 
                v-model="bookData.titre" 
                required
                :disabled="loading"
              >
              <div class="invalid-feedback">{{ formErrors.titre }}</div>
            </div>
            
            <div class="col-md-6 mb-3">
              <label for="auteur" class="form-label">Auteur <span class="text-danger">*</span></label>
              <input 
                type="text" 
                class="form-control" 
                :class="{ 'is-invalid': formErrors.auteur }"
                id="auteur" 
                v-model="bookData.auteur" 
                required
                :disabled="loading"
              >
              <div class="invalid-feedback">{{ formErrors.auteur }}</div>
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="isbn" class="form-label">ISBN <span class="text-danger">*</span></label>
              <input 
                type="text" 
                class="form-control" 
                :class="{ 'is-invalid': formErrors.isbn }"
                id="isbn" 
                v-model="bookData.isbn" 
                required
                :disabled="loading"
              >
              <div class="invalid-feedback">{{ formErrors.isbn }}</div>
              <div class="form-text">Format: ISBN-10 ou ISBN-13</div>
            </div>
            
            <div class="col-md-6 mb-3">
              <label for="date_publication" class="form-label">Date de publication</label>
              <input 
                type="date" 
                class="form-control" 
                :class="{ 'is-invalid': formErrors.date_publication }"
                id="date_publication" 
                v-model="bookData.date_publication" 
                :disabled="loading"
              >
              <div class="invalid-feedback">{{ formErrors.date_publication }}</div>
              <div class="form-text">Format: YYYY-MM-DD</div>
            </div>
          </div>
          
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="quantite" class="form-label">Quantité <span class="text-danger">*</span></label>
              <input 
                type="number" 
                class="form-control" 
                :class="{ 'is-invalid': formErrors.quantite }"
                id="quantite" 
                v-model.number="bookData.quantite" 
                min="1"
                required
                :disabled="loading"
              >
              <div class="invalid-feedback">{{ formErrors.quantite }}</div>
            </div>
          </div>
          
          <div class="d-flex justify-content-between mt-4">
            <button 
              type="button" 
              class="btn btn-outline-secondary" 
              @click="cancel"
              :disabled="loading"
            >
              Annuler
            </button>
            
            <button 
              type="submit" 
              class="btn btn-primary" 
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ loading ? 'Création en cours...' : 'Ajouter le livre' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-label {
  font-weight: 500;
}
</style>