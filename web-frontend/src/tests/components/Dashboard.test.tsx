import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Dashboard } from '../../components/Dashboard';
import { DataProvider } from '../../contexts/DataContext';

const mockData = {
  loading: false,
  error: null,
  data: {
    consumption: [100, 120, 110, 130],
    production: [80, 90, 85, 95],
    timestamps: ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']
  },
  fetchData: jest.fn(),
  refreshData: jest.fn()
};

jest.mock('../../contexts/DataContext', () => ({
  useData: () => mockData
}));

describe('Dashboard Component', () => {
  beforeEach(() => {
    mockData.fetchData.mockClear();
    mockData.refreshData.mockClear();
  });

  it('renders dashboard correctly', () => {
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    expect(screen.getByText('Energy Dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('consumption-chart')).toBeInTheDocument();
    expect(screen.getByTestId('production-chart')).toBeInTheDocument();
  });

  it('handles loading state', () => {
    mockData.loading = true;
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('handles error state', () => {
    mockData.error = new Error('Failed to fetch data');
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    expect(screen.getByText('Error: Failed to fetch data')).toBeInTheDocument();
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('refreshes data when refresh button is clicked', async () => {
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    const refreshButton = screen.getByTestId('refresh-button');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockData.refreshData).toHaveBeenCalled();
    });
  });

  it('updates chart when date range is changed', async () => {
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    const dateRangePicker = screen.getByTestId('date-range-picker');
    fireEvent.change(dateRangePicker, {
      target: { value: '2024-01-01,2024-01-31' }
    });

    await waitFor(() => {
      expect(mockData.fetchData).toHaveBeenCalledWith({
        startDate: '2024-01-01',
        endDate: '2024-01-31'
      });
    });
  });

  it('displays correct summary statistics', () => {
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    expect(screen.getByText('Total Consumption')).toBeInTheDocument();
    expect(screen.getByText('Total Production')).toBeInTheDocument();
    expect(screen.getByText('Net Energy')).toBeInTheDocument();
  });

  it('handles empty data state', () => {
    mockData.data = { consumption: [], production: [], timestamps: [] };
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    expect(screen.getByText('No data available')).toBeInTheDocument();
  });

  it('updates charts when data changes', async () => {
    const { rerender } = render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    // Update mock data
    mockData.data = {
      consumption: [150, 160, 170],
      production: [100, 110, 120],
      timestamps: ['2024-01-05', '2024-01-06', '2024-01-07']
    };

    rerender(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    await waitFor(() => {
      const consumptionChart = screen.getByTestId('consumption-chart');
      expect(consumptionChart).toHaveAttribute('data-updated', 'true');
    });
  });

  it('handles chart export', async () => {
    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    const exportButton = screen.getByTestId('export-button');
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(screen.getByText('Export successful')).toBeInTheDocument();
    });
  });

  it('handles chart export error', async () => {
    // Mock chart export to fail
    jest.spyOn(global, 'Blob').mockImplementationOnce(() => {
      throw new Error('Export failed');
    });

    render(
      <DataProvider>
        <Dashboard />
      </DataProvider>
    );

    const exportButton = screen.getByTestId('export-button');
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(screen.getByText('Export failed')).toBeInTheDocument();
    });
  });
});
