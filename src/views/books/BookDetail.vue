<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBooksStore } from '../../stores/books';
import { useLoansStore } from '../../stores/loans';
import { useAuthStore } from '../../stores/auth';

const route = useRoute();
const router = useRouter();
const booksStore = useBooksStore();
const loansStore = useLoansStore();
const authStore = useAuthStore();

const bookId = computed(() => Number(route.params.id));
const book = computed(() => booksStore.getBook);
const loading = computed(() => booksStore.isLoading);
const error = ref('');

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);

// Borrowing state
const showBorrowForm = ref(false);
const borrowLoading = ref(false);
const borrowError = ref('');
const borrowSuccess = ref('');
const loanDuration = ref(14); // Default loan duration in days

// Load book details on component mount or when book ID changes
onMounted(async () => {
  await loadBookDetails();

  // Check if we should show the borrow form based on query params
  if (route.query.action === 'borrow' && isAuthenticated.value) {
    showBorrowForm.value = true;
  }
});

watch(() => route.params.id, async () => {
  await loadBookDetails();
});

const loadBookDetails = async () => {
  error.value = '';

  try {
    await booksStore.fetchBookById(bookId.value);

    if (!book.value) {
      error.value = 'Livre non trouvé';
    }
  } catch (err) {
    error.value = 'Erreur lors du chargement des détails du livre';
  }
};

const borrowBook = async () => {
  if (!isAuthenticated.value) {
    router.push({ 
      path: '/login', 
      query: { redirect: route.fullPath }
    });
    return;
  }

  borrowLoading.value = true;
  borrowError.value = '';
  borrowSuccess.value = '';

  try {
    const loanData = {
      livre_id: bookId.value,
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

const editBook = () => {
  router.push(`/books/${bookId.value}/edit`);
};

const goBack = () => {
  router.back();
};
</script>

<template>
  <div>
    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <p class="mb-0">{{ error }}</p>
      <button @click="goBack" class="btn btn-outline-danger mt-3">
        Retour
      </button>
    </div>

    <!-- Book Details -->
    <div v-else-if="book" class="row">
      <div class="col-lg-8 order-1 order-lg-0">
        <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start mb-4 gap-3">
          <div>
            <h1 class="mb-1 text-break">{{ book.titre }}</h1>
            <h5 class="text-muted text-break">{{ book.auteur }}</h5>
          </div>
          <button @click="goBack" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-1"></i> <span class="d-none d-sm-inline">Retour</span>
          </button>
        </div>

        <div class="card shadow-sm mb-4">
          <div class="card-body">
            <div class="row mb-3">
              <div class="col-sm-6 mb-3 mb-sm-0">
                <p><strong>ISBN:</strong> <span class="text-break">{{ book.isbn }}</span></p>
                <p class="mb-0 mb-sm-3"><strong>Date de publication:</strong> {{ book.date_publication ? new Date(book.date_publication).toLocaleDateString() : 'Non spécifiée' }}</p>
              </div>
              <div class="col-sm-6">
                <p>
                  <strong>Disponibilité:</strong> 
                  <span class="badge" :class="book.disponible > 0 ? 'bg-success' : 'bg-danger'">
                    {{ book.disponible > 0 ? `${book.disponible}/${book.quantite} disponible(s)` : 'Indisponible' }}
                  </span>
                </p>
                <p class="mb-0"><strong>Ajouté le:</strong> {{ new Date(book.cree_le).toLocaleDateString() }}</p>
              </div>
            </div>

            <div class="d-flex flex-column flex-sm-row justify-content-between gap-2 mt-4">
              <button 
                v-if="isAdmin" 
                @click="editBook" 
                class="btn btn-outline-primary"
              >
                <i class="bi bi-pencil me-1"></i> Modifier
              </button>

              <button 
                v-if="isAuthenticated && book.disponible > 0 && !showBorrowForm" 
                @click="showBorrowForm = true" 
                class="btn btn-success"
                :class="{ 'ms-auto': isAdmin }"
              >
                <i class="bi bi-book me-1"></i> Emprunter
              </button>
            </div>
          </div>
        </div>

        <!-- Borrow Form -->
        <div v-if="showBorrowForm" class="card shadow-sm mb-4">
          <div class="card-header bg-light">
            <h5 class="mb-0">Emprunter ce livre</h5>
          </div>
          <div class="card-body">
            <div v-if="borrowError" class="alert alert-danger" role="alert">
              {{ borrowError }}
            </div>

            <div v-if="borrowSuccess" class="alert alert-success" role="alert">
              {{ borrowSuccess }}
            </div>

            <form v-if="!borrowSuccess" @submit.prevent="borrowBook">
              <div class="row mb-3">
                <div class="col-sm-8 col-md-6">
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
              </div>

              <div class="d-flex flex-column flex-sm-row justify-content-between gap-2">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary" 
                  @click="showBorrowForm = false"
                  :disabled="borrowLoading"
                >
                  <i class="bi bi-x-circle me-1 d-inline d-sm-none"></i>
                  <span class="d-none d-sm-inline">Annuler</span>
                  <span class="d-inline d-sm-none">Fermer</span>
                </button>

                <button 
                  type="submit" 
                  class="btn btn-success" 
                  :disabled="borrowLoading"
                >
                  <span v-if="borrowLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <i v-if="!borrowLoading" class="bi bi-check-circle me-1 d-inline d-sm-none"></i>
                  <span class="d-none d-sm-inline">{{ borrowLoading ? 'Traitement en cours...' : 'Confirmer l\'emprunt' }}</span>
                  <span class="d-inline d-sm-none">{{ borrowLoading ? 'Traitement...' : 'Confirmer' }}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="col-lg-4 order-0 order-lg-1 mb-4 mb-lg-0">
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-light">
            <h5 class="mb-0">Informations</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-6 col-sm-4 col-lg-12 mb-2">
                <div class="d-flex align-items-center">
                  <i class="bi bi-info-circle me-2 text-primary"></i>
                  <div>
                    <strong>Statut:</strong><br>
                    <span v-if="book.disponible > 0" class="text-success">Disponible</span>
                    <span v-else class="text-danger">Indisponible</span>
                  </div>
                </div>
              </div>

              <div class="col-6 col-sm-4 col-lg-12 mb-2">
                <div class="d-flex align-items-center">
                  <i class="bi bi-book me-2 text-primary"></i>
                  <div>
                    <strong>Exemplaires:</strong><br>
                    {{ book.quantite }}
                  </div>
                </div>
              </div>

              <div class="col-12 col-sm-4 col-lg-12 mb-0">
                <div class="d-flex align-items-center">
                  <i class="bi bi-calendar me-2 text-primary"></i>
                  <div>
                    <strong>Durée maximale:</strong><br>
                    30 jours
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!isAuthenticated" class="card shadow-sm mb-4 bg-light">
          <div class="card-body">
            <h5 class="card-title">Vous souhaitez emprunter ce livre ?</h5>
            <p class="card-text">Connectez-vous ou créez un compte pour emprunter des livres.</p>
            <div class="d-flex flex-column flex-sm-row gap-2">
              <router-link to="/login" class="btn btn-primary flex-grow-1">Se connecter</router-link>
              <router-link to="/register" class="btn btn-outline-primary flex-grow-1">S'inscrire</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge {
  font-size: 0.9rem;
  padding: 0.4rem 0.6rem;
}
</style>
