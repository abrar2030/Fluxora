import axios from 'axios';

// Replace with your actual backend API URL
const API_BASE_URL = 'http://localhost:8000'; // Placeholder URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error fetching health status:', error);
    throw error;
  }
};

export const postPredictions = async (data) => {
  try {
    // Ensure data matches the PredictionRequest schema expected by the backend
    const response = await apiClient.post('/predict', data);
    return response.data; // Should return PredictionResponse
  } catch (error) {
    console.error('Error posting predictions:', error);
    throw error;
  }
};

// Add other API calls as needed

