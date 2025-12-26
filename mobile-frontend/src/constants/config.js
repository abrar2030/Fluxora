/**
 * Application configuration constants
 * These values can be overridden by environment variables
 */

// Default API configuration
export const API_CONFIG = {
  // For development, use local machine IP when testing on physical device
  // For emulator/simulator, localhost works
  BASE_URL: __DEV__
    ? process.env.EXPO_PUBLIC_API_URL || "http://10.0.2.2:8000" // Android emulator localhost alias
    : process.env.EXPO_PUBLIC_API_URL || "https://api.fluxora.com",
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
};

// App configuration
export const APP_CONFIG = {
  VERSION: "1.0.0",
  NAME: "Fluxora Mobile",
  THEME: "light", // 'light' or 'dark'
};

// Feature flags
export const FEATURES = {
  ENABLE_NOTIFICATIONS: true,
  ENABLE_OFFLINE_MODE: true,
  ENABLE_ANALYTICS: true,
};

// Chart configuration
export const CHART_CONFIG = {
  DEFAULT_POINTS: 30,
  REFRESH_INTERVAL: 30000, // 30 seconds
  MAX_DATA_POINTS: 100,
};
