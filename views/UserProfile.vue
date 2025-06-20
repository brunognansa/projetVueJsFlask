<template>
  <div class="user-profile">
    // ...existing code...
    <div class="loan-history">
      <h3>Historique des emprunts</h3>
      <table>
        <thead>
          <tr>
            <th>Livre</th>
            <th>Date d'emprunt</th>
            <th>Date de retour</th>
            <th>Statut</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in loanHistory" :key="loan.id">
            <td>{{ loan.book.title }}</td>
            <td>{{ formatDate(loan.borrowed_date) }}</td>
            <td>{{ formatDate(loan.return_date) }}</td>
            <td>{{ loan.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.loan-history {
  margin-top: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.5rem;
  border: 1px solid #ddd;
  text-align: left;
}

th {
  background-color: #f5f5f5;
}
</style>
