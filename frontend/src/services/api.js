import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
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

export const getDataSourcesStatus = async () => {
  const res = await api.get('/data-sources/status');
  return res.data;
};

export const triggerSimulation = async (mode = 'DEMO', scenario = 'normal') => {
  const res = await api.post('/simulate', { mode, scenario });
  return res.data;
};

export const switchToLiveMode = async () => {
  const res = await api.post('/simulate', { mode: 'LIVE', scenario: 'normal' });
  return res.data;
};

export default api;
