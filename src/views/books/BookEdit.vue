<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBooksStore } from '../../stores/books';
import { useAuthStore } from '../../stores/auth';

const route = useRoute();
const router = useRouter();
const booksStore = useBooksStore();
const authStore = useAuthStore();

const bookId = computed(() => Number(route.params.id));
const loading = ref(false);
const fetchLoading = ref(true);
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

// Load book data on component mount
onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/');
    return;
  }
  
  await loadBookData();
});

// Watch for changes in book ID
watch(() => route.params.id, async () => {
  await loadBookData();
});

// Load book data
const loadBookData = async () => {
  error.value = '';
  fetchLoading.value = true;
  
  try {
    await booksStore.fetchBookById(bookId.value);
    const book = booksStore.getBook;
    
    if (!book) {
      error.value = 'Livre non trouvé';
      return;
    }
    
    // Initialize form with book data
    bookData.value = {
      titre: book.titre,
      auteur: book.auteur,
      isbn: book.isbn,
      date_publication: book.date_publication ? book.date_publication.split('T')[0] : '',
      quantite: book.quantite
    };
  } catch (err) {
    error.value = 'Erreur lors du chargement des données du livre';
  } finally {
    fetchLoading.value = false;
  }
};

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

// Update book
const updateBook = async () => {
  if (!validateForm()) {
    return;
  }
  
  loading.value = true;
  error.value = '';
  success.value = '';
  
  try {
    const book = await booksStore.updateBook(bookId.value, bookData.value);
    
    if (book) {
      success.value = 'Livre mis à jour avec succès';
      
      // Redirect to book details after a short delay
      setTimeout(() => {
        router.push(`/books/${book.id}`);
      }, 1500);
    }
  } catch (err) {
    error.value = booksStore.getError || 'Une erreur est survenue lors de la mise à jour du livre';
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
      <h1>Modifier un Livre</h1>
      <button @click="cancel" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-1"></i> Retour
      </button>
    </div>
    
    <!-- Loading Indicator -->
    <div v-if="fetchLoading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <p class="mb-0">{{ error }}</p>
      <button @click="cancel" class="btn btn-outline-danger mt-3">
        Retour
      </button>
    </div>
    
    <!-- Success Message -->
    <div v-else-if="success" class="alert alert-success" role="alert">
      {{ success }}
    </div>
    
    <!-- Book Form -->
    <div v-else class="card shadow-sm">
      <div class="card-body">
        <form @submit.prevent="updateBook">
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
              {{ loading ? 'Mise à jour en cours...' : 'Mettre à jour le livre' }}
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