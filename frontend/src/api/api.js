import axios from 'axios';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 45000,
});

export const checkHealth = async () => {
  try {
    const res = await client.get('/health');
    return res.data;
  } catch (error) {
    return { status: 'offline', error: error.message };
  }
};

export const uploadAndAnalyze = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await client.post('/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const getAnalysisStatus = async (analysisId) => {
  const res = await client.get(`/analysis/${analysisId}/status`);
  return res.data;
};

export const getAnalysisDetails = async (analysisId) => {
  const res = await client.get(`/analysis/${analysisId}`);
  return res.data;
};

export const triggerDemoMode = async () => {
  const res = await client.post('/demo');
  return res.data;
};

export const getArtifactUrl = (analysisId, filename) => {
  return `${API_BASE}/analysis/${analysisId}/artifact/${filename}`;
};

export const getReportUrl = (analysisId, format = 'pdf') => {
  return `${API_BASE}/analysis/${analysisId}/report?format=${format}`;
};
