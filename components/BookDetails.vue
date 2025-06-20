<template>
  <div class="book-details">
    <div class="book-cover">
      <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title">
      <i v-else class="fas fa-book fa-5x"></i>
    </div>
    
    <div class="book-info">
      <h2>{{ book.title }}</h2>
      <div class="categories-tags">
        <span 
          v-for="category in book.categories" 
          :key="category.id" 
          class="category-tag"
        >
          {{ category.nom }}
        </span>
      </div>
      <p class="genre">Genre: {{ book.genre || 'Non spécifié' }}</p>
      <p class="description">{{ book.description || 'Description non disponible' }}</p>
      
      <div class="rating">
        <star-rating v-model="rating" @rating-selected="submitRating"/>
        <div class="comments">
          <h3>Commentaires</h3>
          <div v-for="comment in comments" :key="comment.id">
            <p>{{ comment.text }}</p>
          </div>
          <textarea v-model="newComment" placeholder="Ajouter un commentaire"></textarea>
          <button @click="submitComment">Envoyer</button>
        </div>
      </div>

      <div class="reservation">
        <button @click="makeReservation" :disabled="!isAvailable">
          Réserver
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.book-details {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  padding: 2rem;
}

.book-cover {
  text-align: center;
}

.book-cover img {
  max-width: 100%;
  height: auto;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.book-info {
  padding: 1rem;
}

.genre {
  color: #666;
  font-style: italic;
}

.description {
  margin: 1rem 0;
  line-height: 1.6;
}

.rating {
  margin: 1rem 0;
}

.comments {
  margin-top: 2rem;
}

.categories-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 1rem 0;
}

.category-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.875rem;
}

.reservation button {
  background-color: #4CAF50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.reservation button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
