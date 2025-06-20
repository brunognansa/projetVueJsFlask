<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useBooksStore } from '../../stores/books';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const booksStore = useBooksStore();
const authStore = useAuthStore();

const books = computed(() => booksStore.getBooks);
const pagination = computed(() => booksStore.getPagination);
const loading = computed(() => booksStore.isLoading);
const error = computed(() => booksStore.getError);

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);

const currentPage = ref(1);
const searchTerm = ref('');
const isSearching = ref(false);

// Load books on component mount
onMounted(async () => {
  await loadBooks();
});

// Watch for page changes
watch(currentPage, async () => {
  await loadBooks();
});

// Load books with optional search term
const loadBooks = async () => {
  if (isSearching.value && searchTerm.value) {
    await booksStore.searchBooks(searchTerm.value, currentPage.value);
  } else {
    await booksStore.fetchBooks(currentPage.value);
  }

  // Scroll to top after loading new page
  window.scrollTo(0, 0);
};

// Handle search
const handleSearch = async () => {
  currentPage.value = 1;

  if (searchTerm.value.trim()) {
    isSearching.value = true;
    await booksStore.searchBooks(searchTerm.value, currentPage.value);
  } else {
    isSearching.value = false;
    await booksStore.fetchBooks(currentPage.value);
  }
};

// Clear search
const clearSearch = async () => {
  searchTerm.value = '';
  isSearching.value = false;
  currentPage.value = 1;
  await booksStore.fetchBooks(currentPage.value);
};

// Navigate to book details
const viewBookDetails = (bookId) => {
  router.push(`/books/${bookId}`);
};

// Navigate to book edit page (admin only)
const editBook = (bookId) => {
  router.push(`/books/${bookId}/edit`);
};

// Navigate to create book page (admin only)
const createBook = () => {
  router.push('/books/create');
};

// Borrow a book
const borrowBook = async (bookId) => {
  try {
    // Navigate to book details page with borrow action
    router.push({
      path: `/books/${bookId}`,
      query: { action: 'borrow' }
    });
  } catch (err) {
    console.error('Error navigating to borrow book:', err);
  }
};
</script>

<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h2">Catalogue de Livres</h1>
      <button v-if="isAdmin" @click="createBook" class="btn btn-primary">
        <i class="bi bi-plus-circle me-2"></i> Ajouter un livre
      </button>
    </div>

    <!-- Search and Filter Section -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-sm-12 col-md-8">
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Rechercher par titre, auteur ou ISBN..." 
                v-model="searchTerm"
                @keyup.enter="handleSearch"
              >
              <button class="btn btn-primary" type="button" @click="handleSearch">
                <i class="bi bi-search me-1 d-none d-sm-inline"></i> Rechercher
              </button>
            </div>
          </div>
          <div class="col-sm-12 col-md-4">
            <div class="d-flex flex-column flex-sm-row gap-2">
              <div class="input-group flex-grow-1">
                <label class="input-group-text" for="sortOrder">
                  <i class="bi bi-sort-alpha-down"></i>
                </label>
                <select class="form-select" id="sortOrder">
                  <option selected>Trier par</option>
                  <option value="title">Titre A-Z</option>
                  <option value="author">Auteur A-Z</option>
                  <option value="date">Date d'ajout</option>
                </select>
              </div>
              <button class="btn btn-outline-primary" type="button">
                <i class="bi bi-filter me-1 d-none d-sm-inline"></i> Filtres
              </button>
            </div>
          </div>
        </div>

        <div v-if="isSearching" class="mt-3">
          <div class="alert alert-info mb-0">
            <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center">
              <div>
                <i class="bi bi-search me-2"></i>
                Résultats de recherche pour: <strong>{{ searchTerm }}</strong>
              </div>
              <button class="btn btn-sm btn-outline-info mt-2 mt-sm-0" @click="clearSearch">
                <i class="bi bi-x-circle me-1"></i> Effacer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

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

    <!-- No Books Found -->
    <div v-else-if="books.length === 0" class="alert alert-info" role="alert">
      <p class="mb-0">
        <i class="bi bi-info-circle me-2"></i>
        {{ isSearching ? 'Aucun livre ne correspond à votre recherche.' : 'Aucun livre disponible pour le moment.' }}
      </p>
    </div>

    <!-- Books Grid -->
    <div v-else class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4 mb-4">
      <div v-for="book in books" :key="book.id" class="col">
        <div class="card h-100 shadow-sm hover-card">
          <div class="bg-light d-flex align-items-center justify-content-center p-3" style="height: 160px;">
            <i class="bi bi-book-half text-primary" style="font-size: 3.5rem;"></i>
          </div>
          <div class="card-body">
            <h5 class="card-title text-truncate">{{ book.titre }}</h5>
            <h6 class="card-subtitle mb-2 text-muted text-truncate">{{ book.auteur }}</h6>

            <div class="mb-2">
              <span class="badge" :class="book.disponible > 0 ? 'bg-success' : 'bg-danger'">
                {{ book.disponible > 0 ? `Disponible (${book.disponible}/${book.quantite})` : 'Indisponible' }}
              </span>
            </div>

            <p class="card-text small">
              <span class="text-muted">ISBN: {{ book.isbn }}</span>
            </p>
          </div>

          <div class="card-footer bg-transparent">
            <div class="d-flex flex-column flex-sm-row justify-content-between gap-2">
              <button @click="viewBookDetails(book.id)" class="btn btn-sm btn-outline-primary">
                <i class="bi bi-info-circle d-inline d-sm-none"></i>
                <span class="d-none d-sm-inline"><i class="bi bi-info-circle me-1"></i> Détails</span>
              </button>

              <div class="d-flex gap-2 justify-content-between">
                <button 
                  v-if="isAdmin" 
                  @click="editBook(book.id)" 
                  class="btn btn-sm btn-outline-secondary"
                >
                  <i class="bi bi-pencil"></i>
                </button>

                <button 
                  v-if="isAuthenticated && book.disponible > 0" 
                  @click="borrowBook(book.id)" 
                  class="btn btn-sm btn-success"
                >
                  <i class="bi bi-book d-inline d-sm-none"></i>
                  <span class="d-none d-sm-inline">Emprunter</span>
                </button>
                <button 
                  v-else-if="!isAuthenticated" 
                  class="btn btn-sm btn-secondary"
                  disabled
                >
                  <i class="bi bi-lock d-inline d-sm-none"></i>
                  <span class="d-none d-sm-inline">Indisponible</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="books.length > 0 && pagination.pages > 1" aria-label="Page navigation">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: !pagination.a_precedent }">
          <a class="page-link" href="#" @click.prevent="currentPage--" aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
          </a>
        </li>

        <li 
          v-for="page in pagination.pages" 
          :key="page" 
          class="page-item" 
          :class="{ active: page === currentPage }"
        >
          <a class="page-link" href="#" @click.prevent="currentPage = page">{{ page }}</a>
        </li>

        <li class="page-item" :class="{ disabled: !pagination.a_suivant }">
          <a class="page-link" href="#" @click.prevent="currentPage++" aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
          </a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<style scoped>
.card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(0,0,0,0.1);
}

.hover-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
}

.card-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge {
  font-size: 0.8rem;
  padding: 0.4rem 0.6rem;
}
</style>
