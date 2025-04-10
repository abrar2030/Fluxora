import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { usePredictions } from '../utils/hooks';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Predictions = () => {
  const [formData, setFormData] = useState({
    meterId: '',
    startDate: '',
    endDate: '',
    interval: 'hourly',
    features: []
  });
  
  const [showResults, setShowResults] = useState(false);
  const { predictions, loading, error, fetchPredictions } = usePredictions();
  
  // Chart data state
  const [chartData, setChartData] = useState({
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    datasets: [
      {
        label: 'Predicted Consumption',
        data: [30, 25, 35, 55, 60, 45, 35, 28, 40, 58, 62, 48],
        borderColor: 'rgb(14, 165, 233)',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Confidence Interval (Upper)',
        data: [33, 28, 39, 60, 65, 49, 38, 31, 44, 63, 67, 52],
        borderColor: 'rgba(20, 184, 166, 0.5)',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
      },
      {
        label: 'Confidence Interval (Lower)',
        data: [27, 22, 31, 50, 55, 41, 32, 25, 36, 53, 57, 44],
        borderColor: 'rgba(20, 184, 166, 0.5)',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
      },
    ],
  });
  
  // Chart options
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Energy Consumption Prediction',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'kWh',
        },
      },
    },
  };
  
  // Available features for prediction
  const availableFeatures = [
    { id: 'temperature', name: 'Temperature' },
    { id: 'humidity', name: 'Humidity' },
    { id: 'occupancy', name: 'Occupancy' },
    { id: 'day_type', name: 'Day Type (Weekday/Weekend)' },
    { id: 'holiday', name: 'Holiday' },
  ];
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  // Handle checkbox changes
  const handleFeatureToggle = (featureId) => {
    const updatedFeatures = formData.features.includes(featureId)
      ? formData.features.filter(id => id !== featureId)
      : [...formData.features, featureId];
    
    setFormData({
      ...formData,
      features: updatedFeatures
    });
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Prepare context features object
    const contextFeatures = {};
    formData.features.forEach(featureId => {
      // In a real app, we would have actual values for these features
      // For now, we'll use dummy values
      if (featureId === 'temperature') contextFeatures.temperature = [22, 23, 24, 25, 26, 25, 24, 23, 22, 21, 20, 19];
      if (featureId === 'humidity') contextFeatures.humidity = [45, 48, 50, 52, 55, 58, 60, 62, 60, 58, 55, 50];
      if (featureId === 'occupancy') contextFeatures.occupancy = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0];
      if (featureId === 'day_type') contextFeatures.day_type = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]; // 1 for weekday, 0 for weekend
      if (featureId === 'holiday') contextFeatures.holiday = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]; // 1 for holiday, 0 for non-holiday
    });
    
    try {
      // Call the API to get predictions
      const result = await fetchPredictions(
        formData.meterId,
        formData.startDate,
        formData.endDate,
        formData.interval,
        contextFeatures
      );
      
      // If we got a result, update the chart data
      if (result) {
        // Format the data for the chart
        const timestamps = result.timestamps || [];
        const predictedValues = result.predictions || [];
        const confidenceIntervals = result.confidence_intervals || [];
        
        // Create formatted labels (e.g., "Apr 10, 14:00")
        const formattedLabels = timestamps.map(ts => {
          const date = new Date(ts);
          return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        });
        
        // Create upper and lower confidence bounds
        const upperBounds = confidenceIntervals.map(interval => interval[1]);
        const lowerBounds = confidenceIntervals.map(interval => interval[0]);
        
        // Update chart data
        setChartData({
          labels: formattedLabels,
          datasets: [
            {
              label: 'Predicted Consumption',
              data: predictedValues,
              borderColor: 'rgb(14, 165, 233)',
              backgroundColor: 'rgba(14, 165, 233, 0.1)',
              fill: true,
              tension: 0.4,
            },
            {
              label: 'Confidence Interval (Upper)',
              data: upperBounds,
              borderColor: 'rgba(20, 184, 166, 0.5)',
              backgroundColor: 'transparent',
              borderDash: [5, 5],
              tension: 0.4,
            },
            {
              label: 'Confidence Interval (Lower)',
              data: lowerBounds,
              borderColor: 'rgba(20, 184, 166, 0.5)',
              backgroundColor: 'transparent',
              borderDash: [5, 5],
              tension: 0.4,
            },
          ],
        });
      }
      
      setShowResults(true);
    } catch (err) {
      console.error('Error generating prediction:', err);
      // In a real app, we would show an error message to the user
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Energy Predictions</h1>
      </div>
      
      {/* Prediction form */}
      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Prediction</h2>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="meterId" className="label">Meter ID</label>
              <select
                id="meterId"
                name="meterId"
                value={formData.meterId}
                onChange={handleInputChange}
                className="input"
                required
              >
                <option value="">Select a meter</option>
                <option value="building_a">Building A</option>
                <option value="building_b">Building B</option>
                <option value="building_c">Building C</option>
                <option value="building_d">Building D</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="interval" className="label">Prediction Interval</label>
              <select
                id="interval"
                name="interval"
                value={formData.interval}
                onChange={handleInputChange}
                className="input"
                required
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="startDate" className="label">Start Date</label>
              <input
                type="date"
                id="startDate"
                name="startDate"
                value={formData.startDate}
                onChange={handleInputChange}
                className="input"
                required
              />
            </div>
            
            <div>
              <label htmlFor="endDate" className="label">End Date</label>
              <input
                type="date"
                id="endDate"
                name="endDate"
                value={formData.endDate}
                onChange={handleInputChange}
                className="input"
                required
              />
            </div>
          </div>
          
          <div className="mt-6">
            <label className="label">Context Features</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {availableFeatures.map((feature) => (
                <div key={feature.id} className="flex items-center">
                  <input
                    type="checkbox"
                    id={feature.id}
                    checked={formData.features.includes(feature.id)}
                    onChange={() => handleFeatureToggle(feature.id)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor={feature.id} className="ml-2 text-sm text-gray-700">
                    {feature.name}
                  </label>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </>
              ) : (
                'Generate Prediction'
              )}
            </button>
          </div>
        </form>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Prediction results */}
      {showResults && (
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Prediction Results</h2>
          <div className="mb-6">
            <Line data={chartData} options={chartOptions} />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Average Consumption</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">
                {predictions ? 
                  (predictions.predictions.reduce((a, b) => a + b, 0) / predictions.predictions.length).toFixed(1) + ' kWh' : 
                  '42.5 kWh'}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Peak Consumption</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">
                {predictions ? 
                  Math.max(...predictions.predictions).toFixed(1) + ' kWh' : 
                  '62.0 kWh'}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Total Consumption</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">
                {predictions ? 
                  predictions.predictions.reduce((a, b) => a + b, 0).toFixed(1) + ' kWh' : 
                  '510.0 kWh'}
              </p>
            </div>
          </div>
          
          <div className="mt-6 flex justify-end space-x-3">
            <button className="btn btn-outline flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Export Results
            </button>
            <button className="btn btn-primary flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Save Prediction
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Predictions;
