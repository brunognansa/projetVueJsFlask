<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBooksStore } from '../stores/books';
import { useAuthStore } from '../stores/auth';
import LoginModal from '../components/modals/LoginModal.vue';
import RegisterModal from '../components/modals/RegisterModal.vue';
import BookDetailModal from '../components/modals/BookDetailModal.vue';

const router = useRouter();
const booksStore = useBooksStore();
const authStore = useAuthStore();

const featuredBooks = ref([]);
const loading = ref(true);
const error = ref('');
const searchTerm = ref('');

const isAuthenticated = computed(() => authStore.isAuthenticated);

// Modal states
const showLoginModal = ref(false);
const showRegisterModal = ref(false);
const showBookDetailModal = ref(false);
const selectedBookId = ref(null);

onMounted(async () => {
  try {
    // Fetch books for the featured section
    await booksStore.fetchBooks(1, 4);
    featuredBooks.value = booksStore.getBooks;
  } catch (err) {
    error.value = 'Erreur lors du chargement des livres';
  } finally {
    loading.value = false;
  }
});

const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`);
};

const openBookDetailModal = (bookId) => {
  selectedBookId.value = bookId;
  showBookDetailModal.value = true;
};

const goToBookList = () => {
  router.push('/books');
};

const openLoginModal = () => {
  showLoginModal.value = true;
};

const openRegisterModal = () => {
  showRegisterModal.value = true;
};

const switchToRegister = () => {
  showLoginModal.value = false;
  showRegisterModal.value = true;
};

const switchToLogin = () => {
  showRegisterModal.value = false;
  showLoginModal.value = true;
};

const closeModals = () => {
  showLoginModal.value = false;
  showRegisterModal.value = false;
  showBookDetailModal.value = false;
};

const handleSearch = () => {
  if (searchTerm.value.trim()) {
    router.push({
      path: '/books',
      query: { search: searchTerm.value }
    });
  }
};
</script>

<template>
  <div>
    <!-- Hero Section -->
    <div class="bg-primary text-white py-5 mb-5 rounded">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="display-4 fw-bold">Bibliothèque Universelle</h1>
            <p class="lead">Découvrez notre vaste collection de livres et gérez vos emprunts facilement.</p>
            <div class="mt-4">
              <button @click="goToBookList" class="btn btn-light btn-lg me-2">
                <i class="bi bi-book me-2"></i> Explorer le catalogue
              </button>
              <button v-if="!isAuthenticated" @click="openRegisterModal" class="btn btn-outline-light btn-lg">
                <i class="bi bi-person-plus me-2"></i> S'inscrire
              </button>
            </div>
          </div>
          <div class="col-md-4 d-none d-md-block">
            <img src="@/assets/logo.svg" alt="Library Logo" class="img-fluid" style="max-height: 200px;">
          </div>
        </div>
      </div>
    </div>

    <!-- Search Section -->
    <div class="container mb-5">
      <div class="card shadow-sm">
        <div class="card-body p-4">
          <h2 class="h4 mb-4">Rechercher un livre</h2>
          <form @submit.prevent="handleSearch" class="row g-3">
            <div class="col-sm-8 col-md-9 col-lg-10">
              <input 
                type="text" 
                class="form-control form-control-lg" 
                placeholder="Titre, auteur, ISBN..." 
                v-model="searchTerm"
              >
            </div>
            <div class="col-sm-4 col-md-3 col-lg-2">
              <button type="submit" class="btn btn-primary btn-lg w-100">
                <i class="bi bi-search me-2 d-none d-sm-inline"></i> Rechercher
              </button>
            </div>
          </form>

          <div class="mt-3 d-flex flex-wrap gap-2 align-items-center">
            <span class="text-muted small">Suggestions :</span>
            <div class="d-flex flex-wrap gap-2">
              <a href="#" @click.prevent="searchTerm = 'Romans'; handleSearch()" class="badge bg-light text-dark text-decoration-none">Romans</a>
              <a href="#" @click.prevent="searchTerm = 'Science-fiction'; handleSearch()" class="badge bg-light text-dark text-decoration-none">Science-fiction</a>
              <a href="#" @click.prevent="searchTerm = 'Histoire'; handleSearch()" class="badge bg-light text-dark text-decoration-none">Histoire</a>
              <a href="#" @click.prevent="searchTerm = 'Informatique'; handleSearch()" class="badge bg-light text-dark text-decoration-none">Informatique</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Featured Books Section -->
    <div class="container mb-5">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="mb-0">Notre catalogue</h2>
        <button @click="goToBookList" class="btn btn-outline-primary">
          <i class="bi bi-grid me-2"></i> Voir tout
        </button>
      </div>

      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Chargement...</span>
        </div>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else-if="featuredBooks.length === 0" class="alert alert-info" role="alert">
        Aucun livre disponible pour le moment.
      </div>

      <div v-else class="row">
        <div v-for="book in featuredBooks" :key="book.id" class="col-6 col-sm-6 col-md-4 col-lg-3 mb-4">
          <div class="card h-100 shadow-sm">
            <div class="h-48 bg-light d-flex align-items-center justify-content-center">
              <i class="bi bi-book text-primary" style="font-size: 3rem;"></i>
            </div>
            <div class="card-body">
              <h5 class="card-title text-truncate">{{ book.titre }}</h5>
              <h6 class="card-subtitle mb-2 text-muted text-truncate">{{ book.auteur }}</h6>
              <p class="card-text small">
                <span class="text-muted">ISBN: {{ book.isbn }}</span>
              </p>
              <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2">
                <span class="badge" :class="book.disponible > 0 ? 'bg-success' : 'bg-danger'">
                  {{ book.disponible > 0 ? 'Disponible' : 'Indisponible' }}
                </span>
                <div class="d-flex gap-2">
                  <button @click="openBookDetailModal(book.id)" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-info-circle d-inline d-sm-none"></i>
                    <span class="d-none d-sm-inline"><i class="bi bi-info-circle me-1"></i> Détails</span>
                  </button>
                  <button 
                    v-if="isAuthenticated && book.disponible > 0" 
                    @click="openBookDetailModal(book.id)" 
                    class="btn btn-sm btn-success"
                  >
                    <i class="bi bi-book d-inline d-sm-none"></i>
                    <span class="d-none d-sm-inline">Emprunter</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="text-center mt-4">
        <button @click="goToBookList" class="btn btn-outline-primary px-4 py-2">
          Voir plus de livres
        </button>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="bg-light py-5 mb-5 rounded">
      <div class="container">
        <h2 class="text-center mb-4">Comment ça marche</h2>

        <div class="row g-4">
          <div class="col-sm-6 col-md-4">
            <div class="card h-100 border-0 bg-transparent shadow-sm">
              <div class="card-body text-center p-4">
                <div class="bg-white rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 70px; height: 70px;">
                  <i class="bi bi-person-plus text-primary" style="font-size: 1.75rem;"></i>
                </div>
                <h5 class="card-title">1. Créez un compte</h5>
                <p class="card-text">Inscrivez-vous gratuitement avec votre email et informations personnelles.</p>
              </div>
            </div>
          </div>

          <div class="col-sm-6 col-md-4">
            <div class="card h-100 border-0 bg-transparent shadow-sm">
              <div class="card-body text-center p-4">
                <div class="bg-white rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 70px; height: 70px;">
                  <i class="bi bi-search text-primary" style="font-size: 1.75rem;"></i>
                </div>
                <h5 class="card-title">2. Trouvez un livre</h5>
                <p class="card-text">Parcourez notre catalogue ou utilisez notre moteur de recherche.</p>
              </div>
            </div>
          </div>

          <div class="col-sm-12 col-md-4">
            <div class="card h-100 border-0 bg-transparent shadow-sm">
              <div class="card-body text-center p-4">
                <div class="bg-white rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 70px; height: 70px;">
                  <i class="bi bi-book text-primary" style="font-size: 1.75rem;"></i>
                </div>
                <h5 class="card-title">3. Empruntez et lisez</h5>
                <p class="card-text">Empruntez le livre et profitez de votre lecture pendant 3 semaines.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Call to Action Section -->
    <div class="container mb-5">
      <div class="card bg-primary text-white">
        <div class="card-body text-center py-4">
          <h3 class="card-title">Prêt à commencer ?</h3>
          <p class="card-text">Rejoignez notre bibliothèque dès aujourd'hui et accédez à des milliers de livres.</p>
          <div v-if="!isAuthenticated" class="mt-3">
            <button @click="openLoginModal" class="btn btn-light me-2">Se connecter</button>
            <button @click="openRegisterModal" class="btn btn-outline-light">S'inscrire</button>
          </div>
          <div v-else class="mt-3">
            <button @click="goToBookList" class="btn btn-light">Parcourir le catalogue</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <LoginModal 
      :show="showLoginModal" 
      @close="closeModals" 
      @switch-to-register="switchToRegister"
    />

    <RegisterModal 
      :show="showRegisterModal" 
      @close="closeModals" 
      @switch-to-login="switchToLogin"
    />

    <BookDetailModal 
      :show="showBookDetailModal" 
      :book-id="selectedBookId" 
      @close="closeModals"
    />
  </div>
</template>

<style scoped>
.card {
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
