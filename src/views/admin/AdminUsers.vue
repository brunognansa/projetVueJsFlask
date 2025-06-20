<script setup>
import { ref, computed, onMounted } from 'vue';
import { useUsersStore } from '../../stores/users';
import { useAuthStore } from '../../stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();
const usersStore = useUsersStore();
const authStore = useAuthStore();

const users = computed(() => usersStore.getUsers);
const pagination = computed(() => usersStore.getPagination);
const loading = computed(() => usersStore.isLoading);
const error = ref('');
const success = ref('');

const currentPage = ref(1);

// User action state
const selectedUser = ref(null);
const actionType = ref('');
const actionLoading = ref(false);
const actionError = ref('');
const showConfirmModal = ref(false);

// Check if user is admin
const isAdmin = computed(() => authStore.isAdmin);

// Redirect non-admin users
onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/');
    return;
  }
  
  await loadUsers();
});

// Load users
const loadUsers = async () => {
  error.value = '';
  
  try {
    await usersStore.fetchUsers(currentPage.value);
  } catch (err) {
    error.value = 'Erreur lors du chargement des utilisateurs';
  }
};

// Format date
const formatDate = (dateString) => {
  return dateString ? new Date(dateString).toLocaleDateString() : 'Jamais';
};

// Show confirmation modal for user action
const confirmAction = (user, type) => {
  selectedUser.value = user;
  actionType.value = type;
  actionError.value = '';
  showConfirmModal.value = true;
};

// Cancel action
const cancelAction = () => {
  showConfirmModal.value = false;
  selectedUser.value = null;
  actionType.value = '';
};

// Execute user action
const executeAction = async () => {
  if (!selectedUser.value || !actionType.value) return;
  
  actionLoading.value = true;
  actionError.value = '';
  
  try {
    if (actionType.value === 'toggleAdmin') {
      await usersStore.updateUserRole(
        selectedUser.value.id, 
        !selectedUser.value.est_admin
      );
      success.value = `Rôle de ${selectedUser.value.prenom} ${selectedUser.value.nom} mis à jour avec succès`;
    } else if (actionType.value === 'toggleActive') {
      await usersStore.updateUserStatus(
        selectedUser.value.id, 
        !selectedUser.value.est_actif
      );
      success.value = `Statut de ${selectedUser.value.prenom} ${selectedUser.value.nom} mis à jour avec succès`;
    }
    
    // Close modal after a short delay
    setTimeout(() => {
      showConfirmModal.value = false;
      selectedUser.value = null;
      actionType.value = '';
      
      // Clear success message after a delay
      setTimeout(() => {
        success.value = '';
      }, 3000);
    }, 1000);
  } catch (err) {
    actionError.value = usersStore.getError || 'Une erreur est survenue lors de la mise à jour de l\'utilisateur';
  } finally {
    actionLoading.value = false;
  }
};

// Handle pagination
const changePage = async (page) => {
  currentPage.value = page;
  await loadUsers();
  window.scrollTo(0, 0);
};

// Get action confirmation message
const getActionConfirmationMessage = () => {
  if (!selectedUser.value || !actionType.value) return '';
  
  if (actionType.value === 'toggleAdmin') {
    return selectedUser.value.est_admin
      ? `Retirer les droits d'administrateur de ${selectedUser.value.prenom} ${selectedUser.value.nom} ?`
      : `Donner les droits d'administrateur à ${selectedUser.value.prenom} ${selectedUser.value.nom} ?`;
  } else if (actionType.value === 'toggleActive') {
    return selectedUser.value.est_actif
      ? `Désactiver le compte de ${selectedUser.value.prenom} ${selectedUser.value.nom} ?`
      : `Activer le compte de ${selectedUser.value.prenom} ${selectedUser.value.nom} ?`;
  }
  
  return '';
};

// Get action button text
const getActionButtonText = () => {
  if (!selectedUser.value || !actionType.value) return '';
  
  if (actionType.value === 'toggleAdmin') {
    return selectedUser.value.est_admin
      ? 'Retirer les droits d\'administrateur'
      : 'Donner les droits d\'administrateur';
  } else if (actionType.value === 'toggleActive') {
    return selectedUser.value.est_actif
      ? 'Désactiver le compte'
      : 'Activer le compte';
  }
  
  return '';
};
</script>

<template>
  <div>
    <h1 class="mb-4">Gestion des Utilisateurs</h1>
    
    <!-- Success Message -->
    <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ success }}
      <button type="button" class="btn-close" @click="success = ''"></button>
    </div>
    
    <!-- Loading Indicator -->
    <div v-if="loading && !actionLoading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <!-- No Users -->
    <div v-else-if="users.length === 0" class="alert alert-info" role="alert">
      <p class="mb-0">
        <i class="bi bi-info-circle me-2"></i>
        Aucun utilisateur trouvé.
      </p>
    </div>
    
    <!-- Users List -->
    <div v-else>
      <div class="card shadow-sm mb-4">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Nom</th>
                <th>Email</th>
                <th>Date d'inscription</th>
                <th>Dernière connexion</th>
                <th>Statut</th>
                <th>Rôle</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.prenom }} {{ user.nom }}</td>
                <td>{{ user.email }}</td>
                <td>{{ formatDate(user.cree_le) }}</td>
                <td>{{ formatDate(user.derniere_connexion) }}</td>
                <td>
                  <span 
                    class="badge" 
                    :class="user.est_actif ? 'bg-success' : 'bg-danger'"
                  >
                    {{ user.est_actif ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td>
                  <span 
                    class="badge" 
                    :class="user.est_admin ? 'bg-info' : 'bg-secondary'"
                  >
                    {{ user.est_admin ? 'Administrateur' : 'Utilisateur' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button 
                      class="btn btn-sm btn-outline-primary" 
                      @click="confirmAction(user, 'toggleAdmin')"
                    >
                      <i :class="user.est_admin ? 'bi bi-person' : 'bi bi-person-fill-gear'"></i>
                    </button>
                    <button 
                      class="btn btn-sm" 
                      :class="user.est_actif ? 'btn-outline-danger' : 'btn-outline-success'" 
                      @click="confirmAction(user, 'toggleActive')"
                    >
                      <i :class="user.est_actif ? 'bi bi-lock-fill' : 'bi bi-unlock-fill'"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Pagination -->
      <nav v-if="pagination.pages > 1" aria-label="Page navigation">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: !pagination.a_precedent }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)" aria-label="Previous">
              <span aria-hidden="true">&laquo;</span>
            </a>
          </li>
          
          <li 
            v-for="page in pagination.pages" 
            :key="page" 
            class="page-item" 
            :class="{ active: page === currentPage }"
          >
            <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
          </li>
          
          <li class="page-item" :class="{ disabled: !pagination.a_suivant }">
            <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)" aria-label="Next">
              <span aria-hidden="true">&raquo;</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
    
    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirmation</h5>
            <button type="button" class="btn-close" @click="cancelAction" :disabled="actionLoading"></button>
          </div>
          <div class="modal-body">
            <div v-if="actionError" class="alert alert-danger" role="alert">
              {{ actionError }}
            </div>
            
            <p>{{ getActionConfirmationMessage() }}</p>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="cancelAction"
              :disabled="actionLoading"
            >
              Annuler
            </button>
            <button 
              type="button" 
              class="btn" 
              :class="actionType === 'toggleActive' && selectedUser?.est_actif ? 'btn-danger' : 'btn-primary'"
              @click="executeAction"
              :disabled="actionLoading"
            >
              <span v-if="actionLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ actionLoading ? 'Traitement en cours...' : getActionButtonText() }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.badge {
  font-size: 0.85rem;
  padding: 0.4rem 0.6rem;
}

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