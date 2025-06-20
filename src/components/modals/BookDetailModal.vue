<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBooksStore } from '../../stores/books';
import { useLoansStore } from '../../stores/loans';
import { useAuthStore } from '../../stores/auth';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  bookId: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['close']);

const router = useRouter();
const booksStore = useBooksStore();
const loansStore = useLoansStore();
const authStore = useAuthStore();

const book = ref(null);
const loading = ref(false);
const error = ref('');

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);

// Borrowing state
const showBorrowForm = ref(false);
const borrowLoading = ref(false);
const borrowError = ref('');
const borrowSuccess = ref('');
const loanDuration = ref(14); // Default loan duration in days

// Load book details when bookId changes
watch(() => props.bookId, async (newVal) => {
  if (newVal && props.show) {
    await loadBookDetails();
  }
});

// Load book details when modal is shown
watch(() => props.show, async (newVal) => {
  if (newVal && props.bookId) {
    await loadBookDetails();
  } else {
    // Reset state when modal is closed
    book.value = null;
    error.value = '';
    showBorrowForm.value = false;
    borrowError.value = '';
    borrowSuccess.value = '';
  }
});

const loadBookDetails = async () => {
  if (!props.bookId) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    await booksStore.fetchBookById(props.bookId);
    book.value = booksStore.getBook;
    
    if (!book.value) {
      error.value = 'Livre non trouvé';
    }
  } catch (err) {
    error.value = 'Erreur lors du chargement des détails du livre';
  } finally {
    loading.value = false;
  }
};

const borrowBook = async () => {
  if (!isAuthenticated.value) {
    emit('close');
    router.push('/login');
    return;
  }
  
  borrowLoading.value = true;
  borrowError.value = '';
  borrowSuccess.value = '';
  
  try {
    const loanData = {
      livre_id: props.bookId,
      duree_emprunt: loanDuration.value
    };
    
    const loan = await loansStore.borrowBook(loanData);
    
    if (loan) {
      borrowSuccess.value = `Livre emprunté avec succès. Date de retour prévue: ${new Date(loan.date_retour_prevue).toLocaleDateString()}`;
      showBorrowForm.value = false;
      
      // Reload book details to update availability
      await loadBookDetails();
    }
  } catch (err) {
    borrowError.value = loansStore.getError || 'Une erreur est survenue lors de l\'emprunt du livre';
  } finally {
    borrowLoading.value = false;
  }
};

const viewBookDetails = () => {
  emit('close');
  router.push(`/books/${props.bookId}`);
};

const editBook = () => {
  emit('close');
  router.push(`/books/${props.bookId}/edit`);
};

const closeModal = () => {
  emit('close');
};
</script>

<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Détails du livre</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        
        <div class="modal-body">
          <!-- Loading Indicator -->
          <div v-if="loading" class="text-center my-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Chargement...</span>
            </div>
          </div>
          
          <!-- Error Message -->
          <div v-else-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          
          <!-- Book Details -->
          <div v-else-if="book" class="row">
            <div class="col-md-4">
              <div class="bg-light rounded d-flex align-items-center justify-content-center p-4" style="height: 200px;">
                <i class="bi bi-book-fill text-primary" style="font-size: 5rem;"></i>
              </div>
            </div>
            
            <div class="col-md-8">
              <h4 class="mb-1">{{ book.titre }}</h4>
              <p class="text-muted mb-3">{{ book.auteur }}</p>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <p class="mb-1"><strong>ISBN:</strong> {{ book.isbn }}</p>
                  <p class="mb-1"><strong>Date de publication:</strong> {{ book.date_publication ? new Date(book.date_publication).toLocaleDateString() : 'Non spécifiée' }}</p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1">
                    <strong>Disponibilité:</strong> 
                    <span class="badge" :class="book.disponible > 0 ? 'bg-success' : 'bg-danger'">
                      {{ book.disponible > 0 ? `${book.disponible}/${book.quantite} disponible(s)` : 'Indisponible' }}
                    </span>
                  </p>
                  <p class="mb-1"><strong>Genre:</strong> Non spécifié</p>
                </div>
              </div>
              
              <div v-if="!showBorrowForm && !borrowSuccess">
                <h5 class="mb-2">Description</h5>
                <p class="text-muted">Aucune description disponible pour ce livre.</p>
                
                <div class="d-flex mt-4">
                  <button @click="viewBookDetails" class="btn btn-outline-primary me-2">
                    <i class="bi bi-info-circle me-1"></i> Plus de détails
                  </button>
                  
                  <button 
                    v-if="isAdmin" 
                    @click="editBook" 
                    class="btn btn-outline-secondary me-2"
                  >
                    <i class="bi bi-pencil me-1"></i> Modifier
                  </button>
                  
                  <button 
                    v-if="isAuthenticated && book.disponible > 0" 
                    @click="showBorrowForm = true" 
                    class="btn btn-success"
                  >
                    <i class="bi bi-book me-1"></i> Emprunter
                  </button>
                </div>
              </div>
              
              <!-- Borrow Form -->
              <div v-if="showBorrowForm" class="mt-3">
                <div v-if="borrowError" class="alert alert-danger" role="alert">
                  {{ borrowError }}
                </div>
                
                <form @submit.prevent="borrowBook">
                  <div class="mb-3">
                    <label for="loanDuration" class="form-label">Durée de l'emprunt (jours)</label>
                    <select 
                      id="loanDuration" 
                      class="form-select" 
                      v-model="loanDuration"
                      :disabled="borrowLoading"
                    >
                      <option value="7">7 jours</option>
                      <option value="14">14 jours</option>
                      <option value="21">21 jours</option>
                      <option value="30">30 jours</option>
                    </select>
                    <div class="form-text">
                      Date de retour prévue: {{ new Date(Date.now() + loanDuration * 24 * 60 * 60 * 1000).toLocaleDateString() }}
                    </div>
                  </div>
                  
                  <div class="d-flex justify-content-between">
                    <button 
                      type="button" 
                      class="btn btn-outline-secondary" 
                      @click="showBorrowForm = false"
                      :disabled="borrowLoading"
                    >
                      Annuler
                    </button>
                    
                    <button 
                      type="submit" 
                      class="btn btn-success" 
                      :disabled="borrowLoading"
                    >
                      <span v-if="borrowLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      {{ borrowLoading ? 'Traitement en cours...' : 'Confirmer l\'emprunt' }}
                    </button>
                  </div>
                </form>
              </div>
              
              <!-- Borrow Success Message -->
              <div v-if="borrowSuccess" class="alert alert-success mt-3" role="alert">
                {{ borrowSuccess }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1050;
  width: 100%;
  height: 100%;
  overflow: hidden;
  outline: 0;
}

.badge {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}
</style>