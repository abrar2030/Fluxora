import axios from 'axios';
import mockDataService from './dataService';

// For static deployment, we'll use mock data directly
// No actual API calls will be attempted in production
const api = {
  getHealthStatus: async () => {
    return {
      status: 'healthy',
      version: '1.0.0-static'
    };
  },
  
  getPredictions: async (data) => {
    return mockDataService.generatePredictionData(24);
  }
};

export const getHealthStatus = api.getHealthStatus;
export const getPredictions = api.getPredictions;

export default api;
