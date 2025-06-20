import { createRouter, createWebHistory } from 'vue-router';

// Lazy-loaded route components
const Home = () => import('../views/Home.vue');
const Login = () => import('../views/auth/Login.vue');
const Register = () => import('../views/auth/Register.vue');
const Profile = () => import('../views/user/Profile.vue');
const BookList = () => import('../views/books/BookList.vue');
const BookDetail = () => import('../views/books/BookDetail.vue');
const BookCreate = () => import('../views/books/BookCreate.vue');
const BookEdit = () => import('../views/books/BookEdit.vue');
const LoanActive = () => import('../views/loans/LoanActive.vue');
const LoanHistory = () => import('../views/loans/LoanHistory.vue');
const AdminUsers = () => import('../views/admin/AdminUsers.vue');
const AdminLoans = () => import('../views/admin/AdminLoans.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Accueil' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: 'Connexion', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: 'Inscription', guest: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: 'Mon Profil', requiresAuth: true }
  },
  {
    path: '/books',
    name: 'BookList',
    component: BookList,
    meta: { title: 'Catalogue de Livres' , requireAuth : false , requyiresAdmin: false  }
  },
  {
    path: '/books/:id',
    name: 'BookDetail',
    component: BookDetail,
    meta: { title: 'Détails du Livre' }
  },
  {
    path: '/books/create',
    name: 'BookCreate',
    component: BookCreate,
    meta: { title: 'Ajouter un Livre', requiresAuth: false, requiresAdmin: false }
  },
  {
    path: '/books/:id/edit',
    name: 'BookEdit',
    component: BookEdit,
    meta: { title: 'Modifier un Livre', requiresAuth: false, requiresAdmin: false }
  },
  {
    path: '/loans/active',
    name: 'LoanActive',
    component: LoanActive,
    meta: { title: 'Mes Emprunts Actifs', requiresAuth: false }
  },
  {
    path: '/loans/history',
    name: 'LoanHistory',
    component: LoanHistory,
    meta: { title: 'Historique des Emprunts', requiresAuth: false }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { title: 'Gestion des Utilisateurs', requiresAuth: true, requiresAdmin: false }
  },
  {
    path: '/admin/loans',
    name: 'AdminLoans',
    component: AdminLoans,
    meta: { title: 'Gestion des Emprunts', requiresAuth: true, requiresAdmin: false  }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guards
router.beforeEach((to, from, next) => {
  // Set document title
  document.title = `${to.meta.title || 'Bibliothèque'} | Système de Gestion de Bibliothèque`;
  
  // Check if the route requires authentication
  const isAuthenticated = !!localStorage.getItem('token_acces');
  
  // Get user data from localStorage
  const userData = localStorage.getItem('user');
  const user = userData ? JSON.parse(userData) : null;
  const isAdmin = user && user.est_admin;
  
  // Routes that require authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      next({ name: 'Home' }); // Redirect non-admin users
    } else {
      next();
    }
  } 
  // Routes for guests only (login, register)
  else if (to.matched.some(record => record.meta.guest)) {
    if (isAuthenticated) {
      next({ name: 'Home' });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;