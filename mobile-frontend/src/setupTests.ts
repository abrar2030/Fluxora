import '@testing-library/jest-native/extend-expect';

// Mock the native modules
jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');
jest.mock('react-native/Libraries/EventEmitter/NativeEventEmitter');

// Mock the Dimensions API
jest.mock('react-native/Libraries/Utilities/Dimensions', () => ({
  get: jest.fn().mockReturnValue({ width: 375, height: 812 }),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
}));

// Mock the Platform API
jest.mock('react-native/Libraries/Utilities/Platform', () => ({
  OS: 'ios',
  select: jest.fn(obj => obj.ios),
}));

// Mock the InteractionManager
jest.mock('react-native/Libraries/Interaction/InteractionManager', () => ({
  runAfterInteractions: jest.fn(callback => callback()),
})); 