import React, { useState, useEffect } from 'react';
import { predictionService } from '../utils/api';

// Custom hook for making predictions
export const usePredictions = () => {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPredictions = async (meterId, startDate, endDate, interval, features) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await predictionService.getPredictions(meterId, startDate, endDate, interval, features);
      setPredictions(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to fetch predictions');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    predictions,
    loading,
    error,
    fetchPredictions
  };
};

// Custom hook for API health check
export const useApiHealth = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await predictionService.checkHealth();
      setHealth(data);
      return data;
    } catch (err) {
      setError(err.message || 'Failed to check API health');
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return {
    health,
    loading,
    error,
    checkHealth
  };
};
