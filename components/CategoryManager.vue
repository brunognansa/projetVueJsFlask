<template>
  <div class="category-manager">
    <div class="category-header">
      <h2>Gestion des Catégories</h2>
      <button v-if="isAdmin" @click="showAddForm = true" class="add-button">
        <i class="fas fa-plus"></i> Nouvelle Catégorie
      </button>
    </div>

    <div v-if="showAddForm" class="category-form">
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Nom de la catégorie</label>
          <input v-model="form.nom" required type="text" class="form-input">
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="form.description" class="form-input"></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="submit-button">Enregistrer</button>
          <button type="button" @click="showAddForm = false" class="cancel-button">
            Annuler
          </button>
        </div>
      </form>
    </div>

    <div class="categories-list">
      <div v-for="category in categories" :key="category.id" class="category-item">
        <div class="category-content">
          <h3>{{ category.nom }}</h3>
          <p>{{ category.description }}</p>
        </div>
        <div v-if="isAdmin" class="category-actions">
          <button @click="editCategory(category)" class="edit-button">
            <i class="fas fa-edit"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="pagination">
      <button 
        :disabled="!pagination?.a_precedent" 
        @click="changePage(pagination.page - 1)"
      >
        Précédent
      </button>
      <span>Page {{ pagination?.page }} sur {{ pagination?.pages }}</span>
      <button 
        :disabled="!pagination?.a_suivant" 
        @click="changePage(pagination.page + 1)"
      >
        Suivant
      </button>
    </div>
  </div>
</template>

<style scoped>
.category-manager {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.add-button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.categories-list {
  display: grid;
  gap: 1rem;
}

.category-item {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 2rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  align-items: center;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.pagination button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}
</style>
