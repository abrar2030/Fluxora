import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const AnalyticsScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Analytics Screen</Text>
      {/* Content for Analytics will go here */}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
  },
});

export default AnalyticsScreen;

