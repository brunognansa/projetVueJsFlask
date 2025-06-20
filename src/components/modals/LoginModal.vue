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

const emit = defineEmits(['close', 'switch-to-register']);

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const rememberMe = ref(false);
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
      // Close modal and redirect to home
      emit('close');
      router.push('/');
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

const switchToRegister = () => {
  emit('switch-to-register');
};

const closeModal = () => {
  emit('close');
};

// Reset form when modal is closed
const resetForm = () => {
  email.value = '';
  password.value = '';
  rememberMe.value = false;
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
          <h5 class="modal-title">Connexion</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>

        <div class="modal-body">
          <div v-if="error" class="alert alert-danger" role="alert">
            {{ error }}
          </div>

          <form @submit.prevent="login">
            <div class="mb-3">
              <label for="loginEmail" class="form-label">Email</label>
              <input 
                type="email" 
                class="form-control" 
                id="loginEmail" 
                v-model="email" 
                placeholder="votre@email.com" 
                required
                :disabled="loading"
              >
            </div>

            <div class="mb-3">
              <label for="loginPassword" class="form-label">Mot de passe</label>
              <div class="input-group">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-control" 
                  id="loginPassword" 
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
                </button>
              </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mb-3">
              <div class="form-check">
                <input 
                  type="checkbox" 
                  class="form-check-input" 
                  id="rememberMe" 
                  v-model="rememberMe"
                >
                <label class="form-check-label" for="rememberMe">Se souvenir de moi</label>
              </div>
              <a href="#" class="text-decoration-none">Mot de passe oublié?</a>
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
            <p class="mb-0">Vous n'avez pas de compte? <a href="#" @click.prevent="switchToRegister" class="text-decoration-none">S'inscrire</a></p>
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
