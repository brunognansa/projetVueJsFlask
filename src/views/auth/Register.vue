<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const prenom = ref('');
const nom = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref('');
const showPassword = ref(false);

const register = async () => {
  // Basic validation
  if (!prenom.value || !nom.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Veuillez remplir tous les champs';
    return;
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = 'Les mots de passe ne correspondent pas';
    return;
  }
  
  if (password.value.length < 8) {
    error.value = 'Le mot de passe doit contenir au moins 8 caractères';
    return;
  }
  
  loading.value = true;
  error.value = '';
  
  try {
    const success = await authStore.register({
      prenom: prenom.value,
      nom: nom.value,
      email: email.value,
      mot_de_passe: password.value
    });
    
    if (success) {
      // Redirect to login page with success message
      router.push({ 
        path: '/login', 
        query: { 
          message: 'Inscription réussie ! Vous pouvez maintenant vous connecter.' 
        } 
      });
    } else {
      error.value = authStore.getError || 'Une erreur est survenue lors de l\'inscription';
    }
  } catch (err) {
    error.value = err.message || 'Une erreur est survenue lors de l\'inscription';
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
    <div class="col-md-8 col-lg-6">
      <div class="card shadow">
        <div class="card-header bg-primary text-white">
          <h4 class="mb-0">Inscription</h4>
        </div>
        <div class="card-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          
          <form @submit.prevent="register">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="prenom" class="form-label">Prénom</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="prenom" 
                  v-model="prenom" 
                  placeholder="Votre prénom" 
                  required
                  :disabled="loading"
                >
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="nom" class="form-label">Nom</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="nom" 
                  v-model="nom" 
                  placeholder="Votre nom" 
                  required
                  :disabled="loading"
                >
              </div>
            </div>
            
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
                  placeholder="Minimum 8 caractères" 
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
              <div class="form-text">Le mot de passe doit contenir au moins 8 caractères.</div>
            </div>
            
            <div class="mb-3">
              <label for="confirmPassword" class="form-label">Confirmer le mot de passe</label>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                class="form-control" 
                id="confirmPassword" 
                v-model="confirmPassword" 
                placeholder="Confirmez votre mot de passe" 
                required
                :disabled="loading"
              >
            </div>
            
            <div class="d-grid gap-2">
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                {{ loading ? 'Inscription en cours...' : 'S\'inscrire' }}
              </button>
            </div>
          </form>
          
          <div class="mt-3 text-center">
            <p>Vous avez déjà un compte ? <router-link to="/login">Connectez-vous</router-link></p>
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