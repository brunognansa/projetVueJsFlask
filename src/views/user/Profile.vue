<script setup>
import { ref, onMounted, computed } from 'vue';
import { useUsersStore } from '../../stores/users';
import { useAuthStore } from '../../stores/auth';

const usersStore = useUsersStore();
const authStore = useAuthStore();

const user = computed(() => usersStore.getUserProfile);
const loading = computed(() => usersStore.isLoading);
const error = ref('');
const success = ref('');

// Form data
const formData = ref({
  prenom: '',
  nom: '',
  email: ''
});

// Password change form
const passwordForm = ref({
  mot_de_passe_actuel: '',
  nouveau_mot_de_passe: '',
  confirmer_mot_de_passe: ''
});

const showPassword = ref(false);
const passwordLoading = ref(false);
const passwordError = ref('');
const passwordSuccess = ref('');

onMounted(async () => {
  try {
    await usersStore.fetchUserProfile();
    
    // Initialize form with user data
    if (user.value) {
      formData.value = {
        prenom: user.value.prenom,
        nom: user.value.nom,
        email: user.value.email
      };
    }
  } catch (err) {
    error.value = 'Erreur lors du chargement du profil';
  }
});

const updateProfile = async () => {
  error.value = '';
  success.value = '';
  
  try {
    await usersStore.updateUserProfile(formData.value);
    success.value = 'Profil mis à jour avec succès';
  } catch (err) {
    error.value = usersStore.getError || 'Erreur lors de la mise à jour du profil';
  }
};

const changePassword = async () => {
  passwordError.value = '';
  passwordSuccess.value = '';
  
  // Validation
  if (!passwordForm.value.mot_de_passe_actuel || !passwordForm.value.nouveau_mot_de_passe || !passwordForm.value.confirmer_mot_de_passe) {
    passwordError.value = 'Veuillez remplir tous les champs';
    return;
  }
  
  if (passwordForm.value.nouveau_mot_de_passe !== passwordForm.value.confirmer_mot_de_passe) {
    passwordError.value = 'Les nouveaux mots de passe ne correspondent pas';
    return;
  }
  
  if (passwordForm.value.nouveau_mot_de_passe.length < 8) {
    passwordError.value = 'Le nouveau mot de passe doit contenir au moins 8 caractères';
    return;
  }
  
  passwordLoading.value = true;
  
  try {
    const success = await authStore.changePassword({
      mot_de_passe_actuel: passwordForm.value.mot_de_passe_actuel,
      nouveau_mot_de_passe: passwordForm.value.nouveau_mot_de_passe
    });
    
    if (success) {
      passwordSuccess.value = 'Mot de passe changé avec succès';
      // Reset form
      passwordForm.value = {
        mot_de_passe_actuel: '',
        nouveau_mot_de_passe: '',
        confirmer_mot_de_passe: ''
      };
    } else {
      passwordError.value = authStore.getError || 'Erreur lors du changement de mot de passe';
    }
  } catch (err) {
    passwordError.value = err.message || 'Erreur lors du changement de mot de passe';
  } finally {
    passwordLoading.value = false;
  }
};

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};
</script>

<template>
  <div>
    <h1 class="mb-4">Mon Profil</h1>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>
    
    <div v-else class="row">
      <!-- Profile Information -->
      <div class="col-md-6 mb-4">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Informations Personnelles</h5>
          </div>
          <div class="card-body">
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>
            
            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label for="prenom" class="form-label">Prénom</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="prenom" 
                  v-model="formData.prenom" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="nom" class="form-label">Nom</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="nom" 
                  v-model="formData.nom" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email" 
                  v-model="formData.email" 
                  required
                >
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-primary" 
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Mettre à jour le profil
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Change Password -->
      <div class="col-md-6 mb-4">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0">Changer le Mot de Passe</h5>
          </div>
          <div class="card-body">
            <div v-if="passwordError" class="alert alert-danger" role="alert">
              {{ passwordError }}
            </div>
            <div v-if="passwordSuccess" class="alert alert-success" role="alert">
              {{ passwordSuccess }}
            </div>
            
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label for="currentPassword" class="form-label">Mot de passe actuel</label>
                <div class="input-group">
                  <input 
                    :type="showPassword ? 'text' : 'password'" 
                    class="form-control" 
                    id="currentPassword" 
                    v-model="passwordForm.mot_de_passe_actuel" 
                    required
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
              
              <div class="mb-3">
                <label for="newPassword" class="form-label">Nouveau mot de passe</label>
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-control" 
                  id="newPassword" 
                  v-model="passwordForm.nouveau_mot_de_passe" 
                  required
                >
                <div class="form-text">Le mot de passe doit contenir au moins 8 caractères.</div>
              </div>
              
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirmer le nouveau mot de passe</label>
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  class="form-control" 
                  id="confirmPassword" 
                  v-model="passwordForm.confirmer_mot_de_passe" 
                  required
                >
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-primary" 
                  :disabled="passwordLoading"
                >
                  <span v-if="passwordLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Changer le mot de passe
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Account Information -->
      <div class="col-12 mb-4">
        <div class="card shadow">
          <div class="card-header bg-light">
            <h5 class="mb-0">Informations du Compte</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Date d'inscription:</strong> {{ user?.cree_le ? new Date(user.cree_le).toLocaleDateString() : 'N/A' }}</p>
                <p><strong>Dernière connexion:</strong> {{ user?.derniere_connexion ? new Date(user.derniere_connexion).toLocaleDateString() : 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Statut du compte:</strong> <span class="badge bg-success" v-if="user?.est_actif">Actif</span><span class="badge bg-danger" v-else>Inactif</span></p>
                <p><strong>Rôle:</strong> <span class="badge bg-info" v-if="user?.est_admin">Administrateur</span><span class="badge bg-secondary" v-else>Utilisateur</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  margin-bottom: 1.5rem;
}
</style>