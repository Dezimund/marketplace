import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const MEDIA_URL = process.env.REACT_APP_MEDIA_URL || 'http://localhost:8000';

export const getImageUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `${MEDIA_URL}${path}`;
};

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email, password) => api.post('/auth/login/', { email, password }),
  register: (data) => api.post('/auth/register/', data),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
};

export const productsAPI = {
  getAll: (params) => api.get('/products/', { params }),
  getBySlug: (slug) => api.get(`/products/${slug}/`),
  getRecommended: () => api.get('/products/recommended/'),
  getBestsellers: () => api.get('/products/bestsellers/'),
  getNew: () => api.get('/products/new/'),
  getSale: () => api.get('/products/sale/'),
  getPopular: () => api.get('/products/popular/'),
  getRelated: (slug) => api.get(`/products/${slug}/related/`),
  search: (query) => api.get('/products/', { params: { search: query } }),
};

export const categoriesAPI = {
  getAll: () => api.get('/categories/'),
  getBySlug: (slug) => api.get(`/categories/${slug}/`),
  getProducts: (slug) => api.get(`/categories/${slug}/products/`),
};

export const cartAPI = {
  get: () => api.get('/cart/'),
  add: (productId, quantity = 1, sizeId = null) =>
    api.post('/cart/add/', {
      product_id: productId,
      quantity: quantity,
      product_size_id: sizeId
    }),
  update: (itemId, quantity) =>
    api.patch(`/cart/update/${itemId}/`, { quantity }),
  remove: (itemId) => api.delete(`/cart/remove/${itemId}/`),
  clear: () => api.delete('/cart/clear/'),
  getCount: () => api.get('/cart/count/'),
};

export const usersAPI = {
  getById: (id) => api.get(`/users/${id}/`),
  getProducts: (userId) => api.get(`/users/${userId}/products/`),
};

export const ordersAPI = {
  getAll: () => api.get('/orders/'),
  getById: (id) => api.get(`/orders/${id}/`),
  create: (data) => api.post('/orders/checkout/', data),
};

export default api;