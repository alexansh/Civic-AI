/**
 * API Service - Centralized API communication
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  logout: () => api.post('/auth/logout'),
};

// Complaint APIs
export const complaintsAPI = {
  getAll: (params) => api.get('/complaints/', { params }),
  getById: (id) => api.get(`/complaints/${id}`),
  create: (data) => api.post('/complaints/', data),
  update: (id, data) => api.put(`/complaints/${id}`, data),
  delete: (id) => api.delete(`/complaints/${id}`),
  updateStatus: (id, data) => api.put(`/complaints/${id}/status`, data),
  getNearbyVendors: (id) => api.get(`/complaints/nearby-vendors/${id}`),
};

// Vendor APIs
export const vendorAPI = {
  getDashboard: () => api.get('/vendor/dashboard'),
  getAvailableComplaints: () => api.get('/vendor/complaints/available'),
  getMyTasks: (params) => api.get('/vendor/complaints/my-tasks', { params }),
  acceptComplaint: (id) => api.post(`/vendor/complaints/${id}/accept`),
  submitEstimate: (id, data) => api.post(`/vendor/complaints/${id}/estimate`, data),
  markComplete: (id, data) => api.post(`/vendor/complaints/${id}/complete`, data),
  updateAvailability: (data) => api.put('/vendor/availability', data),
  getProfile: () => api.get('/vendor/profile'),
};

// Government APIs
export const governmentAPI = {
  getDashboard: () => api.get('/government/dashboard'),
  getComplaints: (params) => api.get('/government/complaints', { params }),
  getComplaint: (id) => api.get(`/government/complaints/${id}`),
  assignComplaint: (id, data) => api.post(`/government/complaints/${id}/assign`, data),
  startWork: (id) => api.post(`/government/complaints/${id}/start`),
  resolveComplaint: (id, data) => api.post(`/government/complaints/${id}/resolve`, data),
  rejectComplaint: (id, data) => api.post(`/government/complaints/${id}/reject`, data),
  getStatistics: () => api.get('/government/statistics'),
  getProfile: () => api.get('/government/profile'),
};

// Admin APIs
export const adminAPI = {
  getDashboard: () => api.get('/admin/dashboard'),
  getUsers: (params) => api.get('/admin/users', { params }),
  verifyUser: (id) => api.post(`/admin/users/${id}/verify`),
  deactivateUser: (id, data) => api.post(`/admin/users/${id}/deactivate`, data),
  getVendors: (params) => api.get('/admin/vendors', { params }),
  verifyVendorLicense: (id, data) => api.post(`/admin/vendors/${id}/verify-license`, data),
  getGovernmentBodies: (params) => api.get('/admin/government-bodies', { params }),
  createGovernmentBody: (data) => api.post('/admin/government-bodies', data),
  getAllComplaints: (params) => api.get('/admin/complaints', { params }),
  assignComplaint: (id, data) => api.put(`/admin/complaints/${id}/assign`, data),
  getAuditLogs: (params) => api.get('/admin/audit-logs', { params }),
  getStatistics: () => api.get('/admin/statistics'),
};

// AI APIs
export const aiAPI = {
  classifyImage: (formData) => api.post('/ai/classify-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  classifyText: (data) => api.post('/ai/classify-text', data),
  predictPriority: (data) => api.post('/ai/predict-priority', data),
  validateIssue: (data) => api.post('/ai/validate-issue', data),
  suggestCategory: (data) => api.post('/ai/category-suggestion', data),
};

export default api;
