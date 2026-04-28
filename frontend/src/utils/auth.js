/**
 * Authentication Utilities
 */

export const isAuthenticated = () => {
  const token = localStorage.getItem('token');
  return !!token;
};

export const getToken = () => {
  return localStorage.getItem('token');
};

export const getUser = () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch (e) {
    return null;
  }
};

export const getRole = () => {
  const user = getUser();
  return user?.role || null;
};

export const isAdmin = () => {
  return getRole() === 'admin';
};

export const isCitizen = () => {
  return getRole() === 'citizen';
};

export const isVendor = () => {
  return getRole() === 'vendor';
};

export const isGovernment = () => {
  return getRole() === 'government';
};

export const setAuth = (token, user) => {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
};

export const clearAuth = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const login = (token, user) => {
  setAuth(token, user);
};

export const logout = () => {
  clearAuth();
};

export const requireAuth = (navigate) => {
  if (!isAuthenticated()) {
    navigate('/login');
    return false;
  }
  return true;
};

export const requireRole = (role, navigate) => {
  if (!requireAuth(navigate)) {
    return false;
  }
  if (getRole() !== role) {
    navigate('/unauthorized');
    return false;
  }
  return true;
};