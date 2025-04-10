import React, { useState } from 'react';

const Models = () => {
  const [activeTab, setActiveTab] = useState('models');
  
  // Sample model data
  const models = [
    { 
      id: 1, 
      name: 'XGBoost Energy Predictor', 
      version: '2.3.0', 
      type: 'XGBoost', 
      accuracy: '94.2%', 
      status: 'active',
      created: '2025-03-15',
      lastUsed: '2025-04-10'
    },
    { 
      id: 2, 
      name: 'LSTM Time Series Model', 
      version: '1.5.2', 
      type: 'LSTM', 
      accuracy: '92.8%', 
      status: 'inactive',
      created: '2025-02-20',
      lastUsed: '2025-03-25'
    },
    { 
      id: 3, 
      name: 'Prophet Forecaster', 
      version: '1.1.0', 
      type: 'Prophet', 
      accuracy: '91.5%', 
      status: 'inactive',
      created: '2025-01-10',
      lastUsed: '2025-02-15'
    },
  ];
  
  // Sample training history
  const trainingHistory = [
    { 
      id: 1, 
      modelName: 'XGBoost Energy Predictor', 
      version: '2.3.0', 
      startTime: '2025-03-15 09:23:45', 
      endTime: '2025-03-15 10:45:12', 
      status: 'completed',
      metrics: {
        accuracy: '94.2%',
        rmse: '0.0842',
        mae: '0.0625'
      }
    },
    { 
      id: 2, 
      modelName: 'XGBoost Energy Predictor', 
      version: '2.2.0', 
      startTime: '2025-02-28 14:10:22', 
      endTime: '2025-02-28 15:30:45', 
      status: 'completed',
      metrics: {
        accuracy: '93.8%',
        rmse: '0.0875',
        mae: '0.0642'
      }
    },
    { 
      id: 3, 
      modelName: 'LSTM Time Series Model', 
      version: '1.5.2', 
      startTime: '2025-02-20 08:15:33', 
      endTime: '2025-02-20 11:45:10', 
      status: 'completed',
      metrics: {
        accuracy: '92.8%',
        rmse: '0.0912',
        mae: '0.0701'
      }
    },
  ];
  
  // Render status badge
  const renderStatusBadge = (status) => {
    if (status === 'active') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
          Active
        </span>
      );
    } else if (status === 'inactive') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
          Inactive
        </span>
      );
    } else if (status === 'completed') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
          Completed
        </span>
      );
    } else if (status === 'failed') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
          Failed
        </span>
      );
    } else {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
          In Progress
        </span>
      );
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Models</h1>
        <button className="btn btn-primary flex items-center">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Train New Model
        </button>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`${
              activeTab === 'models'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            onClick={() => setActiveTab('models')}
          >
            Models
          </button>
          <button
            className={`${
              activeTab === 'training'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            onClick={() => setActiveTab('training')}
          >
            Training History
          </button>
        </nav>
      </div>
      
      {/* Models Tab */}
      {activeTab === 'models' && (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Version
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Accuracy
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Used
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {models.map((model) => (
                  <tr key={model.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {model.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.version}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.accuracy}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {renderStatusBadge(model.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.created}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {model.lastUsed}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button className="text-primary-600 hover:text-primary-900">
                          View
                        </button>
                        {model.status === 'inactive' && (
                          <button className="text-green-600 hover:text-green-900">
                            Activate
                          </button>
                        )}
                        {model.status === 'active' && (
                          <button className="text-gray-600 hover:text-gray-900">
                            Deactivate
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Training History Tab */}
      {activeTab === 'training' && (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Version
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Start Time
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    End Time
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Metrics
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {trainingHistory.map((training) => (
                  <tr key={training.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {training.modelName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {training.version}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {training.startTime}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {training.endTime}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {renderStatusBadge(training.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex flex-col">
                        <span>Accuracy: {training.metrics.accuracy}</span>
                        <span>RMSE: {training.metrics.rmse}</span>
                        <span>MAE: {training.metrics.mae}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button className="text-primary-600 hover:text-primary-900">
                          View Logs
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Models;
