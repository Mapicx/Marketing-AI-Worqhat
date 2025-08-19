import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // Adjust this to match your FastAPI backend URL

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ForecastRequest {
  customers_file: File;
  campaign_history_file: File;
}

export interface ImageGenerationRequest {
  prompt: string;
}

export interface SloganGenerationRequest {
  context: string;
}

export interface RAGProcessRequest {
  youtube_url: string;
}

export interface RAGQueryRequest {
  question: string;
}

// Forecast API
export const runForecast = async (data: ForecastRequest) => {
  const formData = new FormData();
  formData.append('customers_file', data.customers_file);
  formData.append('campaign_history_file', data.campaign_history_file);
  
  const response = await api.post('/forecast', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Image Generation API
export const generateImage = async (data: ImageGenerationRequest) => {
  const response = await api.post('/img', data);
  return response.data;
};

// Slogan Generation API
export const generateSlogan = async (data: SloganGenerationRequest) => {
  const response = await api.post('/slogan', data);
  return response.data;
};

// RAG APIs
export const processVideo = async (data: RAGProcessRequest) => {
  const response = await api.post('/rag/process', data);
  return response.data;
};

export const queryVideo = async (data: RAGQueryRequest) => {
  const response = await api.post('/rag/query', data);
  return response.data;
};

export default api;