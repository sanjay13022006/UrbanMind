import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
});

export const getCityStatus = async () => {
  const res = await api.get('/city/status');
  return res.data;
};

export const getLocations = async () => {
  const res = await api.get('/locations');
  return res.data;
};

export const getLocationDetail = async (id) => {
  const res = await api.get(`/location/${id}`);
  return res.data;
};

export const getPredictions = async () => {
  const res = await api.get('/predictions');
  return res.data;
};

export const getAlerts = async () => {
  const res = await api.get('/alerts');
  return res.data;
};

export const getAnalytics = async () => {
  const res = await api.get('/analytics');
  return res.data;
};

export const triggerSimulation = async (scenario = 'normal') => {
  const res = await api.post('/simulate', { scenario });
  return res.data;
};

export default api;
