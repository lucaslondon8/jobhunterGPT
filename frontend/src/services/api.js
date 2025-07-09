const API_URL = 'http://localhost:8000/api';

const request = async (endpoint, options = {}) => {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Accept': 'application/json',
    ...options.headers,
  };

  if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || 'An API error occurred');
  }
  return response.json();
};

// --- Auth Endpoints ---
export const loginUser = (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return request('/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
    });
};
export const registerUser = (email, password) => request('/users/register', { method: 'POST', body: JSON.stringify({ email, password }) });
export const getCurrentUser = () => request('/users/me');

// --- Job Endpoints ---
export const uploadCv = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return request('/upload-cv', { method: 'POST', body: formData });
};
export const discoverJobs = () => request('/discover-jobs', { method: 'POST' });
export const getMatchedJobs = () => request('/jobs/matches');
