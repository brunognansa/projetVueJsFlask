<script setup>
import { computed } from 'vue';
import { useAuthStore } from './stores/auth';
import NavBar from './components/layout/NavBar.vue';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const isAdmin = computed(() => authStore.isAdmin);
</script>

<template>
  <div class="app-container">
    <NavBar />

    <main class="container py-4">
      <!-- Loading indicator -->
      <div v-if="$route.meta.loading" class="text-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Chargement...</span>
        </div>
      </div>

      <!-- Router view -->
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer class="bg-light py-3 mt-auto">
      <div class="container text-center">
        <p class="mb-0">© {{ new Date().getFullYear() }} Système de Gestion de Bibliothèque</p>
      </div>
    </footer>
  </div>
</template>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
