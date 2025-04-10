import React, { useState } from 'react';

const Settings = () => {
  const [generalSettings, setGeneralSettings] = useState({
    apiEndpoint: 'http://localhost:8000',
    refreshInterval: '5',
    theme: 'light',
    notifications: true
  });
  
  const [modelSettings, setModelSettings] = useState({
    defaultModel: 'xgboost',
    confidenceInterval: '95',
    predictionHorizon: '24',
    featureStore: true
  });
  
  const [monitoringSettings, setMonitoringSettings] = useState({
    driftThreshold: '0.25',
    performanceMonitoring: true,
    alertEmails: 'admin@example.com',
    logLevel: 'info'
  });
  
  const handleGeneralChange = (e) => {
    const { name, value, type, checked } = e.target;
    setGeneralSettings({
      ...generalSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleModelChange = (e) => {
    const { name, value, type, checked } = e.target;
    setModelSettings({
      ...modelSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleMonitoringChange = (e) => {
    const { name, value, type, checked } = e.target;
    setMonitoringSettings({
      ...monitoringSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleSaveSettings = (e) => {
    e.preventDefault();
    // In a real app, this would save settings to backend
    alert('Settings saved successfully!');
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
      </div>
      
      <form onSubmit={handleSaveSettings}>
        {/* General Settings */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">General Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="apiEndpoint" className="label">API Endpoint</label>
              <input
                type="text"
                id="apiEndpoint"
                name="apiEndpoint"
                value={generalSettings.apiEndpoint}
                onChange={handleGeneralChange}
                className="input"
              />
            </div>
            
            <div>
              <label htmlFor="refreshInterval" className="label">Dashboard Refresh Interval (minutes)</label>
              <input
                type="number"
                id="refreshInterval"
                name="refreshInterval"
                value={generalSettings.refreshInterval}
                onChange={handleGeneralChange}
                min="1"
                max="60"
                className="input"
              />
            </div>
            
            <div>
              <label htmlFor="theme" className="label">Theme</label>
              <select
                id="theme"
                name="theme"
                value={generalSettings.theme}
                onChange={handleGeneralChange}
                className="input"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System Default</option>
              </select>
            </div>
            
            <div className="flex items-center mt-8">
              <input
                type="checkbox"
                id="notifications"
                name="notifications"
                checked={generalSettings.notifications}
                onChange={handleGeneralChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="notifications" className="ml-2 text-sm text-gray-700">
                Enable Browser Notifications
              </label>
            </div>
          </div>
        </div>
        
        {/* Model Settings */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Model Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="defaultModel" className="label">Default Model Type</label>
              <select
                id="defaultModel"
                name="defaultModel"
                value={modelSettings.defaultModel}
                onChange={handleModelChange}
                className="input"
              >
                <option value="xgboost">XGBoost</option>
                <option value="lstm">LSTM</option>
                <option value="prophet">Prophet</option>
              </select>
            </div>
            
            <div>
              <label htmlFor="confidenceInterval" className="label">Confidence Interval (%)</label>
              <input
                type="number"
                id="confidenceInterval"
                name="confidenceInterval"
                value={modelSettings.confidenceInterval}
                onChange={handleModelChange}
                min="50"
                max="99"
                className="input"
              />
            </div>
            
            <div>
              <label htmlFor="predictionHorizon" className="label">Default Prediction Horizon (hours)</label>
              <input
                type="number"
                id="predictionHorizon"
                name="predictionHorizon"
                value={modelSettings.predictionHorizon}
                onChange={handleModelChange}
                min="1"
                max="168"
                className="input"
              />
            </div>
            
            <div className="flex items-center mt-8">
              <input
                type="checkbox"
                id="featureStore"
                name="featureStore"
                checked={modelSettings.featureStore}
                onChange={handleModelChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="featureStore" className="ml-2 text-sm text-gray-700">
                Use Feature Store for Online Features
              </label>
            </div>
          </div>
        </div>
        
        {/* Monitoring Settings */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Monitoring Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="driftThreshold" className="label">Data Drift Threshold</label>
              <input
                type="number"
                id="driftThreshold"
                name="driftThreshold"
                value={monitoringSettings.driftThreshold}
                onChange={handleMonitoringChange}
                min="0.01"
                max="1.0"
                step="0.01"
                className="input"
              />
            </div>
            
            <div>
              <label htmlFor="alertEmails" className="label">Alert Email Recipients</label>
              <input
                type="text"
                id="alertEmails"
                name="alertEmails"
                value={monitoringSettings.alertEmails}
                onChange={handleMonitoringChange}
                className="input"
                placeholder="Comma-separated email addresses"
              />
            </div>
            
            <div>
              <label htmlFor="logLevel" className="label">Log Level</label>
              <select
                id="logLevel"
                name="logLevel"
                value={monitoringSettings.logLevel}
                onChange={handleMonitoringChange}
                className="input"
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </select>
            </div>
            
            <div className="flex items-center mt-8">
              <input
                type="checkbox"
                id="performanceMonitoring"
                name="performanceMonitoring"
                checked={monitoringSettings.performanceMonitoring}
                onChange={handleMonitoringChange}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="performanceMonitoring" className="ml-2 text-sm text-gray-700">
                Enable Performance Monitoring
              </label>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button type="button" className="btn btn-outline">
            Reset to Defaults
          </button>
          <button type="submit" className="btn btn-primary">
            Save Settings
          </button>
        </div>
      </form>
    </div>
  );
};

export default Settings;
