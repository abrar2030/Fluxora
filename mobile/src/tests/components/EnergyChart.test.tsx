import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react-native';
import { describe, expect, it, jest } from '@jest/globals';
import { EnergyChart } from '../../components/EnergyChart';

const mockData = {
  consumption: [100, 120, 110, 130],
  production: [80, 90, 85, 95],
  timestamps: ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']
};

describe('EnergyChart Component', () => {
  it('renders chart correctly', () => {
    render(<EnergyChart data={mockData} />);

    expect(screen.getByTestId('energy-chart')).toBeTruthy();
    expect(screen.getByText('Energy Consumption')).toBeTruthy();
    expect(screen.getByText('Energy Production')).toBeTruthy();
  });

  it('handles empty data', () => {
    const emptyData = {
      consumption: [],
      production: [],
      timestamps: []
    };

    render(<EnergyChart data={emptyData} />);

    expect(screen.getByText('No data available')).toBeTruthy();
  });

  it('handles data updates', () => {
    const { rerender } = render(<EnergyChart data={mockData} />);

    const newData = {
      consumption: [150, 160, 170],
      production: [100, 110, 120],
      timestamps: ['2024-01-05', '2024-01-06', '2024-01-07']
    };

    rerender(<EnergyChart data={newData} />);

    expect(screen.getByTestId('energy-chart')).toBeTruthy();
  });

  it('handles chart interaction', () => {
    render(<EnergyChart data={mockData} />);

    const chart = screen.getByTestId('energy-chart');
    fireEvent.press(chart);

    expect(screen.getByTestId('chart-tooltip')).toBeTruthy();
  });

  it('displays correct legend', () => {
    render(<EnergyChart data={mockData} />);

    expect(screen.getByTestId('consumption-legend')).toBeTruthy();
    expect(screen.getByTestId('production-legend')).toBeTruthy();
  });

  it('handles chart zoom', () => {
    render(<EnergyChart data={mockData} />);

    const chart = screen.getByTestId('energy-chart');
    fireEvent.pinch(chart, {
      scale: 2,
      velocity: 1
    });

    expect(screen.getByTestId('zoom-controls')).toBeTruthy();
  });

  it('handles chart pan', () => {
    render(<EnergyChart data={mockData} />);

    const chart = screen.getByTestId('energy-chart');
    fireEvent.panGesture(chart, {
      translationX: 100,
      translationY: 0
    });

    expect(screen.getByTestId('pan-indicator')).toBeTruthy();
  });

  it('displays correct time range', () => {
    render(<EnergyChart data={mockData} />);

    expect(screen.getByText('2024-01-01')).toBeTruthy();
    expect(screen.getByText('2024-01-04')).toBeTruthy();
  });

  it('handles chart refresh', () => {
    const onRefresh = jest.fn();
    render(<EnergyChart data={mockData} onRefresh={onRefresh} />);

    const refreshButton = screen.getByTestId('refresh-button');
    fireEvent.press(refreshButton);

    expect(onRefresh).toHaveBeenCalled();
  });

  it('handles chart export', () => {
    const onExport = jest.fn();
    render(<EnergyChart data={mockData} onExport={onExport} />);

    const exportButton = screen.getByTestId('export-button');
    fireEvent.press(exportButton);

    expect(onExport).toHaveBeenCalled();
  });
});
