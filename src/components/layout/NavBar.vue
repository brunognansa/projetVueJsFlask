<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);
const user = computed(() => authStore.getUser);

const logout = async () => {
  await authStore.logout();
  router.push('/login');
};
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow">
    <div class="container">
      <router-link class="navbar-brand d-flex align-items-center" to="/">
        <i class="bi bi-book-half me-2 fs-4"></i>
        <span class="fw-bold">Bibliothèque Universelle</span>
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" 
              aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mx-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">
              <i class="bi bi-house me-1"></i> Accueil
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/books">
              <i class="bi bi-journal-richtext me-1"></i> Catalogue
            </router-link>
          </li>

          <!-- Links for authenticated users -->
          <template v-if="isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/loans/active">
                <i class="bi bi-bookmark me-1"></i> Mes Emprunts
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/loans/history">
                <i class="bi bi-clock-history me-1"></i> Historique
              </router-link>
            </li>
          </template>

          <!-- Admin links -->
          <template v-if="isAdmin">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" id="adminDropdown" role="button" 
                 data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi bi-gear me-1"></i> Administration
              </a>
              <ul class="dropdown-menu" aria-labelledby="adminDropdown">
                <li>
                  <router-link class="dropdown-item" to="/books/create">
                    <i class="bi bi-plus-circle me-2"></i> Ajouter un Livre
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/users">
                    <i class="bi bi-people me-2"></i> Gestion des Utilisateurs
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/loans">
                    <i class="bi bi-list-check me-2"></i> Gestion des Emprunts
                  </router-link>
                </li>
              </ul>
            </li>
          </template>

          <li class="nav-item">
            <a class="nav-link" href="#about">
              <i class="bi bi-info-circle me-1"></i> À propos
            </a>
          </li>
        </ul>

        <!-- User menu or login/register buttons -->
        <div class="d-flex align-items-center">
          <template v-if="isAuthenticated">
            <div class="dropdown">
              <button class="btn btn-outline-light dropdown-toggle d-flex align-items-center" type="button" id="userDropdown" 
                     data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi bi-person-circle me-2"></i>
                <span class="d-none d-sm-inline">{{ user?.prenom }} {{ user?.nom }}</span>
                <span class="d-inline d-sm-none">Profil</span>
              </button>
              <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person me-2"></i> Mon Profil
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/loans/active">
                    <i class="bi bi-book me-2"></i> Mes Emprunts
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right me-2"></i> Déconnexion
                  </a>
                </li>
              </ul>
            </div>
          </template>
          <template v-else>
            <div class="d-none d-sm-block">
              <router-link to="/login" class="btn btn-outline-light me-2">
                Connexion
              </router-link>
              <router-link to="/register" class="btn btn-light">
                Inscription
              </router-link>
            </div>
            <div class="d-sm-none">
              <div class="dropdown">
                <button class="btn btn-outline-light dropdown-toggle" type="button" id="loginDropdown" 
                       data-bs-toggle="dropdown" aria-expanded="false">
                  <i class="bi bi-person-circle"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="loginDropdown">
                  <li>
                    <router-link class="dropdown-item" to="/login">
                      <i class="bi bi-box-arrow-in-right me-2"></i> Connexion
                    </router-link>
                  </li>
                  <li>
                    <router-link class="dropdown-item" to="/register">
                      <i class="bi bi-person-plus me-2"></i> Inscription
                    </router-link>
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  margin-bottom: 1rem;
}
</style>
