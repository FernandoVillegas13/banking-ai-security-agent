import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeTransaction = async (transactionData) => {
  const response = await api.post('/analize', transactionData);
  return response.data;
};

export const getPendingHITL = async () => {
  const response = await api.get('/hitl/pending');
  return response.data;
};

export const getHITLTransaction = async (transactionId) => {
  const response = await api.get(`/hitl/${transactionId}`);
  return response.data;
};

export const reviewTransaction = async (transactionId, decision, reviewerNotes) => {
  const response = await api.post(`/hitl/${transactionId}/review`, {
    decision,
    reviewer_notes: reviewerNotes,
  });
  return response.data;
};

export const getTransaction = async (transactionId) => {
  const response = await api.get(`/transaction/${transactionId}`);
  return response.data;
};

export const getAllTransactions = async (limit = null) => {
  const url = limit ? `/transactions?limit=${limit}` : '/transactions';
  const response = await api.get(url);
  return response.data;
};

export default api;
