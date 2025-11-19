import axios from 'axios';

// Replace with your actual backend API URL
// Consider making this configurable, e.g., via settings or environment variables
const API_BASE_URL = 'http://localhost:8000'; // Placeholder URL - NEEDS TO BE UPDATED FOR ACTUAL DEPLOYMENT

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // Add a timeout for requests
});

// Interceptor for logging or error handling (optional)
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API call error:', error.response || error.message || error);
    // Optionally re-throw or handle specific errors globally
    return Promise.reject(error);
  }
);

export const getHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error fetching health status:', error);
    // Re-throw a more specific error or a generic one
    throw new Error('Failed to fetch health status from backend.');
  }
};

export const postPredictions = async (payload) => {
  try {
    // Ensure payload matches the PredictionRequest schema expected by the backend
    const response = await apiClient.post('/predict', payload);
    return response.data; // Should return PredictionResponse
  } catch (error) {
    console.error('Error posting predictions:', error);
    // Check for specific backend validation errors if possible
    if (error.response && error.response.data && error.response.data.detail) {
        // FastAPI validation errors often come in `detail`
        throw new Error(`Prediction failed: ${JSON.stringify(error.response.data.detail)}`);
    }
    throw new Error('Failed to get predictions from backend.');
  }
};

// New function to fetch summary data (example)
export const getSummary = async () => {
  try {
    // Assuming a '/summary' endpoint exists on the backend
    const response = await apiClient.get('/summary');
    return response.data; // Adjust based on actual response structure
  } catch (error) {
    console.error('Error fetching summary data:', error);
    // Return null or default data, or re-throw
    // For now, let's return a placeholder or throw
    // throw new Error('Failed to fetch summary data from backend.');
    console.warn('Using placeholder summary data as /summary endpoint failed or is not implemented.');
    return {
        totalPredictions: 125,
        averageAccuracy: 0.92,
        lastPredictionTime: new Date().toLocaleTimeString()
    }; // Placeholder data
  }
};


// Add other API calls as needed (e.g., for fetching historical data for charts)




// New function to fetch historical data (example)
export const getHistoricalData = async (params) => {
  try {
    // Assuming a 	'/historical_data' endpoint exists
    // Params could include time range, meter_id etc.
    const response = await apiClient.get(	'/historical_data	', { params });
    return response.data; // Adjust based on actual response structure
  } catch (error) {
    console.error(	'Error fetching historical data:	', error);
    // Return null or default data, or re-throw
    console.warn(	'Using placeholder historical data as /historical_data endpoint failed or is not implemented.	');
    // Return placeholder data matching the chart format
    return {
        lineData: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{ data: [25, 40, 30, 55, 45, 60] }]
        },
        barData: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [{ data: [30, 50, 35, 70, 90, 50, 60] }]
        }
    }; // Placeholder data
  }
};
