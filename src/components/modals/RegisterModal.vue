<script setup>
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'switch-to-login']);

const router = useRouter();
const authStore = useAuthStore();

const prenom = ref('');
const nom = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const acceptTerms = ref(false);
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
  
  if (!acceptTerms.value) {
    error.value = 'Vous devez accepter les conditions d\'utilisation';
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
      // Close modal and switch to login
      emit('close');
      emit('switch-to-login');
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

const switchToLogin = () => {
  emit('switch-to-login');
};

const closeModal = () => {
  emit('close');
};

// Reset form when modal is closed
const resetForm = () => {
  prenom.value = '';
  nom.value = '';
  email.value = '';
  password.value = '';
  confirmPassword.value = '';
  acceptTerms.value = false;
  error.value = '';
};

// Watch for show prop changes to reset form
watch(() => props.show, (newVal) => {
  if (!newVal) {
    resetForm();
  }
});
</script>

<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Inscription</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>
          
          <form @submit.prevent="register">
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="firstName" class="form-label">Prénom</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="firstName" 
                  v-model="prenom" 
                  placeholder="Votre prénom" 
                  required
                  :disabled="loading"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label for="lastName" class="form-label">Nom</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="lastName" 
                  v-model="nom" 
                  placeholder="Votre nom" 
                  required
                  :disabled="loading"
                >
              </div>
            </div>
            
            <div class="mb-3">
              <label for="registerEmail" class="form-label">Email</label>
              <input 
                type="email" 
                class="form-control" 
                id="registerEmail" 
                v-model="email" 
                placeholder="votre@email.com" 
                required
                :disabled="loading"
              >
            </div>
            
            <div class="mb-3">
              <label for="registerPassword" class="form-label">Mot de passe</label>
              <div class="input-group">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-control" 
                  id="registerPassword" 
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
            
            <div class="mb-3 form-check">
              <input 
                type="checkbox" 
                class="form-check-input" 
                id="acceptTerms" 
                v-model="acceptTerms"
                :disabled="loading"
              >
              <label class="form-check-label" for="acceptTerms">
                J'accepte les <a href="#" class="text-decoration-none">conditions d'utilisation</a>
              </label>
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
            <p class="mb-0">Déjà un compte? <a href="#" @click.prevent="switchToLogin" class="text-decoration-none">Se connecter</a></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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