import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints for predictions
export const predictionService = {
  // Get predictions for a specific meter and time range
  getPredictions: async (meterId, startDate, endDate, interval, features) => {
    try {
      const response = await api.post('/predict', {
        timestamps: generateTimestamps(startDate, endDate, interval),
        meter_ids: Array.isArray(meterId) ? meterId : [meterId],
        context_features: features || {}
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching predictions:', error);
      throw error;
    }
  },
  
  // Health check endpoint
  checkHealth: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking API health:', error);
      throw error;
    }
  }
};

// Helper function to generate timestamps based on interval
function generateTimestamps(startDate, endDate, interval = 'hourly') {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const timestamps = [];
  
  let current = new Date(start);
  
  while (current <= end) {
    timestamps.push(current.toISOString());
    
    // Increment based on interval
    if (interval === 'hourly') {
      current = new Date(current.setHours(current.getHours() + 1));
    } else if (interval === 'daily') {
      current = new Date(current.setDate(current.getDate() + 1));
    } else if (interval === 'weekly') {
      current = new Date(current.setDate(current.getDate() + 7));
    } else if (interval === 'monthly') {
      current = new Date(current.setMonth(current.getMonth() + 1));
    }
  }
  
  return timestamps;
}

export default api;
