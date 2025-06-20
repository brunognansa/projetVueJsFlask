<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const showPassword = ref(false);

const login = async () => {
  if (!email.value || !password.value) {
    error.value = 'Veuillez remplir tous les champs';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    const success = await authStore.login({
      email: email.value,
      mot_de_passe: password.value
    });
    
    if (success) {
      // Redirect to the intended page or home
      const redirectPath = route.query.redirect || '/';
      router.push(redirectPath);
    } else {
      error.value = authStore.getError || 'Une erreur est survenue lors de la connexion';
    }
  } catch (err) {
    error.value = err.message || 'Une erreur est survenue lors de la connexion';
  } finally {
    loading.value = false;
  }
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};
</script>

<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
      <div class="card shadow">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">Connexion</h4>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          
          <form @submit.prevent="login">
            <div class="mb-3">
              <label for="email" class="form-label">Email</label>
              <input 
                type="email" 
                class="form-control" 
                id="email" 
                v-model="email" 
                placeholder="votre@email.com" 
                required
                :disabled="loading"
              >
            </div>
            
            <div class="mb-3">
              <label for="password" class="form-label">Mot de passe</label>
              <div class="input-group">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-control" 
                  id="password" 
                  v-model="password" 
                  placeholder="Votre mot de passe" 
                  required
                  :disabled="loading"
                >
                <button 
                  class="btn btn-outline-secondary" 
                  type="button" 
                  @click="togglePasswordVisibility"
                >
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                  {{ showPassword ? 'Masquer' : 'Afficher' }}
                </button>
              </div>
            </div>
            
            <div class="d-grid gap-2">
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                {{ loading ? 'Connexion en cours...' : 'Se connecter' }}
              </button>
            </div>
          </form>
          
          <div class="mt-3 text-center">
            <p>Vous n'avez pas de compte ? <router-link to="/register">Inscrivez-vous</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  margin-top: 2rem;
}
</style>