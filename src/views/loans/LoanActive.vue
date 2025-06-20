<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useLoansStore } from '../../stores/loans';

const router = useRouter();
const loansStore = useLoansStore();

const activeLoans = computed(() => loansStore.getActiveLoans);
const pagination = computed(() => loansStore.getPagination);
const loading = computed(() => loansStore.isLoading);
const error = ref('');

const currentPage = ref(1);
const returnLoading = ref(false);
const returnError = ref('');
const returnSuccess = ref('');
const loanToReturn = ref(null);
const showReturnConfirm = ref(false);

// Load active loans on component mount
onMounted(async () => {
  await loadActiveLoans();
});

// Load active loans
const loadActiveLoans = async () => {
  error.value = '';
  
  try {
    await loansStore.fetchActiveLoans(currentPage.value);
  } catch (err) {
    error.value = 'Erreur lors du chargement des emprunts actifs';
  }
};

// Show return confirmation dialog
const confirmReturn = (loan) => {
  loanToReturn.value = loan;
  showReturnConfirm.value = true;
  returnError.value = '';
  returnSuccess.value = '';
};

// Cancel return
const cancelReturn = () => {
  showReturnConfirm.value = false;
  loanToReturn.value = null;
};

// Return a book
const returnBook = async () => {
  if (!loanToReturn.value) return;
  
  returnLoading.value = true;
  returnError.value = '';
  returnSuccess.value = '';
  
  try {
    await loansStore.returnBook(loanToReturn.value.id);
    returnSuccess.value = 'Livre retourné avec succès';
    
    // Reload active loans after a short delay
    setTimeout(async () => {
      await loadActiveLoans();
      showReturnConfirm.value = false;
      loanToReturn.value = null;
    }, 1500);
  } catch (err) {
    returnError.value = loansStore.getError || 'Une erreur est survenue lors du retour du livre';
  } finally {
    returnLoading.value = false;
  }
};

// Navigate to book details
const viewBookDetails = (bookId) => {
  router.push(`/books/${bookId}`);
};

// Calculate days remaining
const getDaysRemaining = (dueDate) => {
  const today = new Date();
  const due = new Date(dueDate);
  const diffTime = due - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

// Get status class based on days remaining
const getStatusClass = (dueDate) => {
  const daysRemaining = getDaysRemaining(dueDate);
  
  if (daysRemaining < 0) return 'bg-danger';
  if (daysRemaining <= 3) return 'bg-warning';
  return 'bg-success';
};

// Format date
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString();
};

// Handle pagination
const changePage = async (page) => {
  currentPage.value = page;
  await loadActiveLoans();
  window.scrollTo(0, 0);
};
</script>

<template>
  <div>
    <h1 class="mb-4">Mes Emprunts Actifs</h1>
    
    <!-- Loading Indicator -->
    <div v-if="loading && !returnLoading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <!-- No Active Loans -->
    <div v-else-if="activeLoans.length === 0" class="alert alert-info" role="alert">
      <p class="mb-0">
        <i class="bi bi-info-circle me-2"></i>
        Vous n'avez aucun emprunt actif.
      </p>
      <router-link to="/books" class="btn btn-primary mt-3">
        Parcourir le catalogue
      </router-link>
    </div>
    
    <!-- Active Loans List -->
    <div v-else>
      <div class="card shadow-sm mb-4">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Livre</th>
                <th>Date d'emprunt</th>
                <th>Date de retour prévue</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in activeLoans" :key="loan.id">
                <td>
                  <a href="#" @click.prevent="viewBookDetails(loan.livre_id)" class="text-decoration-none">
                    {{ loan.livre_titre || 'Livre #' + loan.livre_id }}
                  </a>
                </td>
                <td>{{ formatDate(loan.date_emprunt) }}</td>
                <td>{{ formatDate(loan.date_retour_prevue) }}</td>
                <td>
                  <span class="badge" :class="getStatusClass(loan.date_retour_prevue)">
                    <span v-if="getDaysRemaining(loan.date_retour_prevue) < 0">
                      En retard de {{ Math.abs(getDaysRemaining(loan.date_retour_prevue)) }} jour(s)
                    </span>
                    <span v-else-if="getDaysRemaining(loan.date_retour_prevue) === 0">
                      À retourner aujourd'hui
                    </span>
                    <span v-else>
                      {{ getDaysRemaining(loan.date_retour_prevue) }} jour(s) restant(s)
                    </span>
                  </span>
                </td>
                <td>
                  <button @click="confirmReturn(loan)" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-arrow-return-left me-1"></i> Retourner
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Pagination -->
      <nav v-if="pagination.pages > 1" aria-label="Page navigation">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: !pagination.a_precedent }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)" aria-label="Previous">
              <span aria-hidden="true">&laquo;</span>
            </a>
          </li>
          
          <li 
            v-for="page in pagination.pages" 
            :key="page" 
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          
          <li class="page-item" :class="{ disabled: !pagination.a_suivant }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)" aria-label="Next">
              <span aria-hidden="true">&raquo;</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
    
    <!-- Return Confirmation Modal -->
    <div v-if="showReturnConfirm" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirmer le retour</h5>
            <button type="button" class="btn-close" @click="cancelReturn" :disabled="returnLoading"></button>
          </div>
          <div class="modal-body">
            <div v-if="returnError" class="alert alert-danger" role="alert">
              {{ returnError }}
            </div>
            
            <div v-if="returnSuccess" class="alert alert-success" role="alert">
              {{ returnSuccess }}
            </div>
            
            <p v-if="!returnSuccess">
              Êtes-vous sûr de vouloir retourner ce livre ?
            </p>
            <p v-if="loanToReturn && !returnSuccess" class="fw-bold">
              {{ loanToReturn.livre_titre || 'Livre #' + loanToReturn.livre_id }}
            </p>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="cancelReturn"
              :disabled="returnLoading || returnSuccess"
            >
              Annuler
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="returnBook"
              :disabled="returnLoading || returnSuccess"
            >
              <span v-if="returnLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ returnLoading ? 'Traitement en cours...' : 'Confirmer le retour' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}

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
</style>