import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const PredictionsScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Predictions Screen</Text>
      {/* Content for Predictions will go here */}
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

export default PredictionsScreen;

