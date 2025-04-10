import React, { useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Monitoring = () => {
  const [activeTab, setActiveTab] = useState('performance');
  const [timeRange, setTimeRange] = useState('7d');
  
  // Performance monitoring data
  const performanceData = {
    labels: ['Apr 3', 'Apr 4', 'Apr 5', 'Apr 6', 'Apr 7', 'Apr 8', 'Apr 9', 'Apr 10'],
    datasets: [
      {
        label: 'RMSE',
        data: [0.085, 0.082, 0.079, 0.081, 0.078, 0.076, 0.075, 0.074],
        borderColor: 'rgb(14, 165, 233)',
        backgroundColor: 'rgba(14, 165, 233, 0.1)',
        fill: true,
        tension: 0.4,
        yAxisID: 'y',
      },
      {
        label: 'Latency (ms)',
        data: [120, 115, 125, 118, 122, 119, 117, 116],
        borderColor: 'rgb(20, 184, 166)',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
        yAxisID: 'y1',
      },
    ],
  };
  
  // Data drift monitoring data
  const driftData = {
    labels: ['Apr 3', 'Apr 4', 'Apr 5', 'Apr 6', 'Apr 7', 'Apr 8', 'Apr 9', 'Apr 10'],
    datasets: [
      {
        label: 'Feature Drift Score',
        data: [0.12, 0.14, 0.13, 0.18, 0.22, 0.19, 0.17, 0.15],
        backgroundColor: 'rgb(14, 165, 233)',
        borderRadius: 4,
      },
    ],
  };
  
  // Chart options
  const performanceOptions = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Model Performance Metrics',
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'RMSE',
        },
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Latency (ms)',
        },
      },
    },
  };
  
  const driftOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Feature Drift Detection',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1.0,
        title: {
          display: true,
          text: 'Drift Score',
        },
      },
    },
  };
  
  // Alert data
  const alerts = [
    {
      id: 1,
      type: 'drift',
      severity: 'medium',
      message: 'Feature drift detected in temperature data',
      timestamp: '2025-04-07 14:23:45',
      status: 'active',
    },
    {
      id: 2,
      type: 'performance',
      severity: 'low',
      message: 'Slight increase in prediction latency',
      timestamp: '2025-04-06 09:15:22',
      status: 'resolved',
    },
    {
      id: 3,
      type: 'system',
      severity: 'high',
      message: 'API endpoint intermittent failures',
      timestamp: '2025-04-05 18:42:10',
      status: 'resolved',
    },
  ];
  
  // Render severity badge
  const renderSeverityBadge = (severity) => {
    if (severity === 'high') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
          High
        </span>
      );
    } else if (severity === 'medium') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
          Medium
        </span>
      );
    } else {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
          Low
        </span>
      );
    }
  };
  
  // Render status badge
  const renderStatusBadge = (status) => {
    if (status === 'active') {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
          Active
        </span>
      );
    } else {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
          Resolved
        </span>
      );
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900">Monitoring</h1>
        <div className="flex space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="input py-1 px-3"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <button className="btn btn-primary flex items-center">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            Configure Alerts
          </button>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`${
              activeTab === 'performance'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            onClick={() => setActiveTab('performance')}
          >
            Performance Monitoring
          </button>
          <button
            className={`${
              activeTab === 'drift'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            onClick={() => setActiveTab('drift')}
          >
            Data Drift Detection
          </button>
          <button
            className={`${
              activeTab === 'alerts'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            onClick={() => setActiveTab('alerts')}
          >
            Alerts
          </button>
        </nav>
      </div>
      
      {/* Performance Monitoring Tab */}
      {activeTab === 'performance' && (
        <div className="card">
          <div className="mb-6">
            <Line data={performanceData} options={performanceOptions} />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Current RMSE</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">0.074</p>
              <p className="text-sm text-green-600">-1.3% from previous period</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Average Latency</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">116 ms</p>
              <p className="text-sm text-green-600">-0.9% from previous period</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">API Uptime</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">99.98%</p>
              <p className="text-sm text-green-600">+0.02% from previous period</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Requests/Hour</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">1,245</p>
              <p className="text-sm text-green-600">+5.2% from previous period</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Data Drift Tab */}
      {activeTab === 'drift' && (
        <div className="card">
          <div className="mb-6">
            <Bar data={driftData} options={driftOptions} />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Current Drift Score</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">0.15</p>
              <p className="text-sm text-green-600">-11.8% from previous period</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Drift Threshold</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">0.25</p>
              <p className="text-sm text-gray-500">Alert triggered above threshold</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Feature with Highest Drift</h3>
              <p className="mt-1 text-2xl font-semibold text-gray-900">Temperature</p>
              <p className="text-sm text-yellow-600">Score: 0.22 (Apr 7)</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Alerts Tab */}
      {activeTab === 'alerts' && (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Alert Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Severity
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Message
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {alert.type.charAt(0).toUpperCase() + alert.type.slice(1)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {renderSeverityBadge(alert.severity)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {alert.message}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {alert.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {renderStatusBadge(alert.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button className="text-primary-600 hover:text-primary-900">
                          View Details
                        </button>
                        {alert.status === 'active' && (
                          <button className="text-green-600 hover:text-green-900">
                            Resolve
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
    </div>
  );
};

export default Monitoring;
