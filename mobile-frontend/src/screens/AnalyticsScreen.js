import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Dimensions, ScrollView } from 'react-native';
import { Appbar, Card, Text, Title, Paragraph, ActivityIndicator, useTheme } from 'react-native-paper';
import { LineChart, BarChart } from 'react-native-chart-kit';

// Get screen width for chart responsiveness
const screenWidth = Dimensions.get('window').width;

// Placeholder data - Replace with actual data fetched from API
const lineChartData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      data: [
        Math.random() * 100,
        Math.random() * 100,
        Math.random() * 100,
        Math.random() * 100,
        Math.random() * 100,
        Math.random() * 100,
      ],
    },
  ],
};

const barChartData = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      data: [20, 45, 28, 80, 99, 43, 50],
    },
  ],
};

const AnalyticsScreen = ({ navigation }) => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true); // Simulate loading
  const [error, setError] = useState(null);

  // Simulate data fetching
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
      // setError('Failed to load analytics data.'); // Uncomment to test error state
    }, 1500); // Simulate 1.5 second load time
    return () => clearTimeout(timer);
  }, []);

  const chartConfig = {
    backgroundColor: theme.colors.surface, // Use theme color
    backgroundGradientFrom: theme.colors.surface, // Use theme color
    backgroundGradientTo: theme.colors.backdrop, // Use theme color
    decimalPlaces: 2, // optional, defaults to 2dp
    color: (opacity = 1) => `rgba(${theme.dark ? '255, 255, 255' : '0, 0, 0'}, ${opacity})`, // Use theme text color
    labelColor: (opacity = 1) => `rgba(${theme.dark ? '255, 255, 255' : '0, 0, 0'}, ${opacity})`, // Use theme text color
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: theme.colors.primary, // Use theme primary color
    },
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Analytics" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {loading ? (
          <ActivityIndicator animating={true} size="large" style={styles.loader} color={theme.colors.primary} />
        ) : error ? (
          <Card style={styles.card}><Card.Content><Paragraph style={styles.errorText}>{error}</Paragraph></Card.Content></Card>
        ) : (
          <>
            <Card style={styles.card}>
              <Card.Content>
                <Title>Energy Consumption Trend (Monthly)</Title>
                <LineChart
                  data={lineChartData}
                  width={screenWidth - 60} // Adjust width based on padding
                  height={220}
                  chartConfig={chartConfig}
                  bezier // Makes the line smooth
                  style={styles.chart}
                />
              </Card.Content>
            </Card>

            <Card style={styles.card}>
              <Card.Content>
                <Title>Peak Usage Times (Weekly)</Title>
                 <BarChart
                    data={barChartData}
                    width={screenWidth - 60}
                    height={220}
                    yAxisLabel="kWh "
                    chartConfig={chartConfig}
                    verticalLabelRotation={30}
                    style={styles.chart}
                  />
              </Card.Content>
            </Card>

            <Card style={styles.card}>
              <Card.Content>
                <Title>Model Performance Metrics</Title>
                <Paragraph style={styles.placeholderText}>
                  (Placeholder: Display key metrics like MAE, RMSE for the prediction model.)
                </Paragraph>
                {/* Add actual metric display here */}
              </Card.Content>
            </Card>
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    flex: 1,
    padding: 15,
  },
  card: {
    marginBottom: 15,
    elevation: 3,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  loader: {
    marginTop: 50,
  },
   errorText: {
    color: 'red',
    textAlign: 'center',
    fontSize: 16,
  },
  placeholderText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 10,
    fontStyle: 'italic',
  },
});

export default AnalyticsScreen;

