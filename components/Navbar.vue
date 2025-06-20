<template>
  <nav class="navbar">
    <div class="nav-brand">
      <router-link to="/" class="logo">
        <i class="fas fa-book-reader"></i>
        Bibliothèque
      </router-link>
    </div>

    <div class="nav-links">
      <router-link to="/" class="nav-link">Accueil</router-link>
      <router-link to="/catalogue" class="nav-link">Catalogue</router-link>
      <router-link v-if="isAuthenticated" to="/mes-emprunts" class="nav-link">
        Mes Emprunts
      </router-link>
    </div>

    <div class="nav-auth">
      <template v-if="isAuthenticated">
        <div class="user-menu">
          <button @click="toggleDropdown" class="user-button">
            <i class="fas fa-user-circle"></i>
            {{ username }}
          </button>
          <div v-if="showDropdown" class="dropdown-menu">
            <router-link to="/profile" class="dropdown-item">
              Mon Profil
            </router-link>
            <button @click="logout" class="dropdown-item">
              Déconnexion
            </button>
          </div>
        </div>
      </template>
      <template v-else>
        <router-link to="/login" class="auth-button login">
          Connexion
        </router-link>
        <router-link to="/register" class="auth-button register">
          S'inscrire
        </router-link>
      </template>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background: #fff;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand .logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: #2c3e50;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
}

.nav-link:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: #3498db;
  transition: width 0.3s ease;
}

.nav-link:hover:after {
  width: 100%;
}

.auth-button {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
}

.login {
  color: #3498db;
  border: 2px solid #3498db;
  margin-right: 1rem;
}

.register {
  background: #3498db;
  color: white;
}

.user-menu {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 0.5rem 0;
  min-width: 200px;
}

.dropdown-item {
  display: block;
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #2c3e50;
}

.dropdown-item:hover {
  background: #f8f9fa;
}
</style>
