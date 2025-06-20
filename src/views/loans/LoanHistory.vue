<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useLoansStore } from '../../stores/loans';

const router = useRouter();
const loansStore = useLoansStore();

const loanHistory = computed(() => loansStore.getLoanHistory);
const pagination = computed(() => loansStore.getPagination);
const loading = computed(() => loansStore.isLoading);
const error = ref('');

const currentPage = ref(1);

// Load loan history on component mount
onMounted(async () => {
  await loadLoanHistory();
});

// Load loan history
const loadLoanHistory = async () => {
  error.value = '';
  
  try {
    await loansStore.fetchLoanHistory(currentPage.value);
  } catch (err) {
    error.value = 'Erreur lors du chargement de l\'historique des emprunts';
  }
};

// Navigate to book details
const viewBookDetails = (bookId) => {
  router.push(`/books/${bookId}`);
};

// Format date
const formatDate = (dateString) => {
  return dateString ? new Date(dateString).toLocaleDateString() : 'N/A';
};

// Calculate loan duration in days
const calculateLoanDuration = (borrowDate, returnDate) => {
  const start = new Date(borrowDate);
  const end = returnDate ? new Date(returnDate) : new Date();
  const diffTime = Math.abs(end - start);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

// Get status class based on whether the loan was returned on time
const getStatusClass = (loan) => {
  if (!loan.est_retourne) return 'bg-secondary';
  if (loan.est_en_retard) return 'bg-danger';
  return 'bg-success';
};

// Get status text
const getStatusText = (loan) => {
  if (!loan.est_retourne) return 'En cours';
  if (loan.est_en_retard) return `Retourné en retard (${loan.jours_de_retard} jour(s))`;
  return 'Retourné à temps';
};

// Handle pagination
const changePage = async (page) => {
  currentPage.value = page;
  await loadLoanHistory();
  window.scrollTo(0, 0);
};
</script>

<template>
  <div>
    <h1 class="mb-4">Historique des Emprunts</h1>
    
    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <!-- No Loan History -->
    <div v-else-if="loanHistory.length === 0" class="alert alert-info" role="alert">
      <p class="mb-0">
        <i class="bi bi-info-circle me-2"></i>
        Vous n'avez aucun historique d'emprunt.
      </p>
      <router-link to="/books" class="btn btn-primary mt-3">
        Parcourir le catalogue
      </router-link>
    </div>
    
    <!-- Loan History List -->
    <div v-else>
      <div class="card shadow-sm mb-4">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Livre</th>
                <th>Date d'emprunt</th>
                <th>Date de retour prévue</th>
                <th>Date de retour effective</th>
                <th>Durée</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in loanHistory" :key="loan.id">
                <td>
                  <a href="#" @click.prevent="viewBookDetails(loan.livre_id)" class="text-decoration-none">
                    {{ loan.livre_titre || 'Livre #' + loan.livre_id }}
                  </a>
                </td>
                <td>{{ formatDate(loan.date_emprunt) }}</td>
                <td>{{ formatDate(loan.date_retour_prevue) }}</td>
                <td>{{ formatDate(loan.date_retour_effective) }}</td>
                <td>{{ calculateLoanDuration(loan.date_emprunt, loan.date_retour_effective) }} jour(s)</td>
                <td>
                  <span class="badge" :class="getStatusClass(loan)">
                    {{ getStatusText(loan) }}
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
            <div class="col-md-4">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ loanHistory.length }}</h3>
                  <p class="text-muted">Emprunts totaux</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ loanHistory.filter(loan => loan.est_retourne && !loan.est_en_retard).length }}</h3>
                  <p class="text-muted">Retournés à temps</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="card border-0 bg-light">
                <div class="card-body text-center">
                  <h3 class="mb-0">{{ loanHistory.filter(loan => loan.est_en_retard).length }}</h3>
                  <p class="text-muted">Retournés en retard</p>
                </div>
              </div>
            </div>
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
</style>