import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const listHcps = () => api.get('/api/hcps/');
export const createHcp = (payload) => api.post('/api/hcps/', payload);

export const createInteraction = (payload) => api.post('/api/interactions/', payload);
export const listInteractions = (hcpId) =>
  api.get('/api/interactions/', { params: hcpId ? { hcp_id: hcpId } : {} });
export const editInteractionNL = (interactionId, instruction) =>
  api.post(`/api/interactions/${interactionId}/edit-nl`, null, { params: { instruction } });
export const summarizeInteraction = (interactionId) =>
  api.post(`/api/interactions/${interactionId}/summarize`);

export const sendChatMessage = (payload) => api.post('/api/chat/', payload);
