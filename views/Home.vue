<template>
  <div class="home">
    <div class="search-section">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Rechercher un livre..." 
        class="search-input"
      >
      <select v-model="filterGenre" class="filter-select">
        <option value="">Tous les genres</option>
        <option v-for="genre in genres" :key="genre" :value="genre">
          {{ genre }}
        </option>
      </select>
    </div>

    <div class="books-grid">
      <div v-for="book in filteredBooks" :key="book.id" class="book-card">
        <div class="book-cover">
          <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title">
          <i v-else class="fas fa-book fa-3x"></i>
        </div>
        <div class="book-info">
          <h3>{{ book.title }}</h3>
          <p class="author">{{ book.author }}</p>
          <p class="genre">{{ book.genre || 'Genre non spécifié' }}</p>
          <div class="availability" :class="{ available: book.isAvailable }">
            {{ book.isAvailable ? 'Disponible' : 'Indisponible' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 2rem;
}

.search-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input, .filter-select {
  padding: 0.8rem;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input {
  flex: 1;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}

.book-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
  overflow: hidden;
}

.book-card:hover {
  transform: translateY(-5px);
}

.book-cover {
  height: 200px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  padding: 1rem;
}

.author {
  color: #666;
  margin: 0.5rem 0;
}

.genre {
  font-size: 0.9rem;
  color: #888;
}

.availability {
  margin-top: 1rem;
  padding: 0.5rem;
  text-align: center;
  border-radius: 4px;
  font-weight: bold;
}

.availability.available {
  background: #e3f2fd;
  color: #1976d2;
}
</style>
