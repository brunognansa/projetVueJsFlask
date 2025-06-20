<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useLoansStore } from '../../stores/loans';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const loansStore = useLoansStore();
const authStore = useAuthStore();

const allLoans = computed(() => loansStore.getAllLoans);
const pagination = computed(() => loansStore.getPagination);
const loading = computed(() => loansStore.isLoading);
const error = ref('');
const success = ref('');

const currentPage = ref(1);
const activeOnly = ref(false);

// Return action state
const loanToReturn = ref(null);
const returnLoading = ref(false);
const returnError = ref('');
const showReturnConfirm = ref(false);

// Check if user is admin
const isAdmin = computed(() => authStore.isAdmin);

// Redirect non-admin users
onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/');
    return;
  }
  
  await loadLoans();
});

// Load loans
const loadLoans = async () => {
  error.value = '';
  
  try {
    await loansStore.fetchAllLoans(currentPage.value, 10, activeOnly.value);
  } catch (err) {
    error.value = 'Erreur lors du chargement des emprunts';
  }
};

// Toggle active only filter
const toggleActiveOnly = async () => {
  activeOnly.value = !activeOnly.value;
  currentPage.value = 1;
  await loadLoans();
};

// Format date
const formatDate = (dateString) => {
  return dateString ? new Date(dateString).toLocaleDateString() : 'N/A';
};

// Calculate days remaining
const getDaysRemaining = (dueDate) => {
  const today = new Date();
  const due = new Date(dueDate);
  const diffTime = due - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

// Get status class based on days remaining and return status
const getStatusClass = (loan) => {
  if (loan.est_retourne) return 'bg-success';
  
  const daysRemaining = getDaysRemaining(loan.date_retour_prevue);
  
  if (daysRemaining < 0) return 'bg-danger';
  if (daysRemaining <= 3) return 'bg-warning';
  return 'bg-info';
};

// Get status text
const getStatusText = (loan) => {
  if (loan.est_retourne) {
    return `Retourné le ${formatDate(loan.date_retour_effective)}`;
  }
  
  const daysRemaining = getDaysRemaining(loan.date_retour_prevue);
  
  if (daysRemaining < 0) {
    return `En retard de ${Math.abs(daysRemaining)} jour(s)`;
  }
  if (daysRemaining === 0) {
    return 'À retourner aujourd\'hui';
  }
  return `${daysRemaining} jour(s) restant(s)`;
};

// Show return confirmation dialog
const confirmReturn = (loan) => {
  loanToReturn.value = loan;
  showReturnConfirm.value = true;
  returnError.value = '';
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
  
  try {
    await loansStore.returnBook(loanToReturn.value.id);
    success.value = 'Livre retourné avec succès';
    
    // Reload loans after a short delay
    setTimeout(async () => {
      await loadLoans();
      showReturnConfirm.value = false;
      loanToReturn.value = null;
      
      // Clear success message after a delay
      setTimeout(() => {
        success.value = '';
      }, 3000);
    }, 1000);
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

// Handle pagination
const changePage = async (page) => {
  currentPage.value = page;
  await loadLoans();
  window.scrollTo(0, 0);
};
</script>

<template>
  <div>
    <h1 class="mb-4">Gestion des Emprunts</h1>
    
    <!-- Success Message -->
    <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ success }}
      <button type="button" class="btn-close" @click="success = ''"></button>
    </div>
    
    <!-- Filter Controls -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="form-check form-switch">
          <input 
            class="form-check-input" 
            type="checkbox" 
            id="activeOnlySwitch" 
            v-model="activeOnly" 
            @change="toggleActiveOnly"
          >
          <label class="form-check-label" for="activeOnlySwitch">
            Afficher uniquement les emprunts actifs
          </label>
        </div>
      </div>
    </div>
    
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
    
    <!-- No Loans -->
    <div v-else-if="allLoans.length === 0" class="alert alert-info" role="alert">
      <p class="mb-0">
        <i class="bi bi-info-circle me-2"></i>
        Aucun emprunt trouvé.
      </p>
    </div>
    
    <!-- Loans List -->
    <div v-else>
      <div class="card shadow-sm mb-4">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Utilisateur</th>
                <th>Livre</th>
                <th>Date d'emprunt</th>
                <th>Date de retour prévue</th>
                <th>Statut</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in allLoans" :key="loan.id">
                <td>{{ loan.id }}</td>
                <td>
                  {{ loan.utilisateur_nom || 'Utilisateur #' + loan.utilisateur_id }}
                </td>
                <td>
                  <a href="#" @click.prevent="viewBookDetails(loan.livre_id)" class="text-decoration-none">
                    {{ loan.livre_titre || 'Livre #' + loan.livre_id }}
                  </a>
                </td>
                <td>{{ formatDate(loan.date_emprunt) }}</td>
                <td>{{ formatDate(loan.date_retour_prevue) }}</td>
                <td>
                  <span class="badge" :class="getStatusClass(loan)">
                    {{ getStatusText(loan) }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="!loan.est_retourne" 
                    @click="confirmReturn(loan)" 
                    class="btn btn-sm btn-outline-primary"
                  >
                    <i class="bi bi-arrow-return-left me-1"></i> Retourner
                  </button>
                  <span v-else class="text-muted">
                    <i class="bi bi-check-circle me-1"></i> Retourné
                  </span>
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
      
      <!-- Statistics -->
      <div class="card shadow-sm mt-4">
        <div class="card-header bg-light">
          <h5 class="mb-0">Statistiques</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-3">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ allLoans.length }}</h3>
                  <p class="text-muted">Emprunts affichés</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-3">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ allLoans.filter(loan => !loan.est_retourne).length }}</h3>
                  <p class="text-muted">Emprunts actifs</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-3">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ allLoans.filter(loan => !loan.est_retourne && getDaysRemaining(loan.date_retour_prevue) < 0).length }}</h3>
                  <p class="text-muted">Emprunts en retard</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-3">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ allLoans.filter(loan => loan.est_retourne).length }}</h3>
                  <p class="text-muted">Emprunts retournés</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
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
            
            <p>Êtes-vous sûr de vouloir marquer ce livre comme retourné ?</p>
            <p v-if="loanToReturn" class="fw-bold">
              {{ loanToReturn.livre_titre || 'Livre #' + loanToReturn.livre_id }}
              <span class="text-muted">
                (emprunté par {{ loanToReturn.utilisateur_nom || 'Utilisateur #' + loanToReturn.utilisateur_id }})
              </span>
            </p>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="cancelReturn"
              :disabled="returnLoading"
            >
              Annuler
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="returnBook"
              :disabled="returnLoading"
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