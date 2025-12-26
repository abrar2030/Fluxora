# Fluxora Mobile Frontend

## Overview

The Fluxora Mobile Frontend is a React Native application built with Expo that provides mobile access to the Fluxora energy forecasting and optimization platform.

## Features

- ✅ Real-time energy consumption dashboard
- ✅ Energy prediction interface
- ✅ Analytics and visualizations
- ✅ User settings and preferences
- ✅ Offline support with AsyncStorage
- ✅ Authentication and user management
- ✅ Push notifications (configurable)

## Tech Stack

- **Framework**: React Native with Expo SDK 52
- **UI Library**: React Native Paper
- **Navigation**: React Navigation v7 (Drawer Navigator)
- **Charts**: React Native Chart Kit
- **State Management**: React Context API + AsyncStorage
- **HTTP Client**: Axios
- **Testing**: Jest + React Native Testing Library

## Prerequisites

- Node.js 16+ (LTS recommended)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- For iOS development: macOS with Xcode
- For Android development: Android Studio with Android SDK

## Installation

### 1. Install dependencies

```bash
cd mobile-frontend
npm install --legacy-peer-deps
```

**Note**: We use `--legacy-peer-deps` to resolve peer dependency conflicts between React Navigation v7 and v6 packages.

### 2. Configure environment variables

Copy the example environment file and update with your backend API URL:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# For Android Emulator (localhost alias)
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000

# For iOS Simulator
# EXPO_PUBLIC_API_URL=http://localhost:8000

# For Physical Device (replace with your computer's IP)
# EXPO_PUBLIC_API_URL=http://192.168.1.100:8000
```

## Running the App

### Start the development server

```bash
npm start
```

This will start the Expo development server and show a QR code.

### Run on Android

```bash
npm run android
```

Or press `a` in the terminal after running `npm start`.

**Requirements**:

- Android Emulator running, OR
- Physical Android device connected via USB with USB debugging enabled

### Run on iOS (macOS only)

```bash
npm run ios
```

Or press `i` in the terminal after running `npm start`.

**Requirements**:

- macOS with Xcode installed
- iOS Simulator running

### Run on Web

```bash
npm run web
```

### Scan QR Code with Expo Go

1. Install Expo Go app on your phone ([iOS](https://apps.apple.com/app/expo-go/id982107779) | [Android](https://play.google.com/store/apps/details?id=host.exp.exponent))
2. Scan the QR code shown in terminal
3. Make sure your phone and computer are on the same network
4. Update the `.env` file with your computer's local IP address

## Backend Setup

The mobile app requires the Fluxora backend to be running. To start the backend:

```bash
cd ../code/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The backend will start on `http://localhost:8000`.

### Verify Backend Connection

Once the app is running, go to the Dashboard screen. It should display:

- Backend API Status: HEALTHY (in green)
- Summary statistics (predictions, accuracy, etc.)

If you see errors, check:

1. Backend is running (`http://localhost:8000/health` should return `{"status": "healthy"}`)
2. `.env` file has correct API URL for your platform
3. Firewall isn't blocking connections

## Testing

### Run all tests

```bash
npm test
```

### Run tests in watch mode

```bash
npm run test:watch
```

### Run tests with coverage

```bash
npm run test:coverage
```

**Note**: Some tests may have compatibility issues with the current Expo/React Native version. The core functionality is tested and working.

## Project Structure

```
mobile-frontend/
├── src/
│   ├── api/              # API client and backend integration
│   ├── components/       # Reusable UI components
│   ├── contexts/         # React Context providers
│   ├── constants/        # App configuration constants
│   ├── navigation/       # Navigation configuration
│   ├── screens/          # Screen components
│   ├── styles/           # Theme and styling
│   ├── tests/            # Test files
│   └── utils/            # Utility functions
├── assets/               # Images, icons, fonts
├── App.js               # Root component
├── app.json             # Expo configuration
├── package.json         # Dependencies
├── babel.config.js      # Babel configuration
├── jest.config.js       # Jest configuration
└── .env.example         # Environment variables template
```

## Key Components

### Screens

- **DashboardScreen**: Main dashboard with system overview and quick actions
- **PredictionsScreen**: Energy prediction interface with input form
- **AnalyticsScreen**: Charts and visualizations for energy data
- **SettingsScreen**: App settings and user preferences
- **HomeScreen**: User profile and task management

### API Integration

The app communicates with the backend through the API client in `src/api/api.js`:

- `getHealth()` - Check backend status
- `postPredictions(payload)` - Submit prediction requests
- `getSummary()` - Get summary statistics
- `getHistoricalData(params)` - Fetch historical energy data
- `getModelMetrics()` - Get ML model performance metrics

### Authentication

Authentication is handled through `AuthContext` which provides:

- `user` - Current user object
- `login(username, password)` - Login function
- `logout()` - Logout function
- `register(username, email, password)` - Registration function
- `isAuthenticated` - Boolean authentication status

## Configuration

### API Configuration

Edit `src/constants/config.js` to change API settings:

```javascript
export const API_CONFIG = {
  BASE_URL: __DEV__
    ? process.env.EXPO_PUBLIC_API_URL || "http://10.0.2.2:8000"
    : "https://api.fluxora.com",
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
};
```

### Feature Flags

Toggle features in `src/constants/config.js`:

```javascript
export const FEATURES = {
  ENABLE_NOTIFICATIONS: true,
  ENABLE_OFFLINE_MODE: true,
  ENABLE_ANALYTICS: true,
};
```

## Troubleshooting

### Common Issues

**1. Metro bundler errors**

```bash
# Clear cache and restart
npx expo start --clear
```

**2. Android build errors**

```bash
# Clean Android build
cd android && ./gradlew clean && cd ..
```

**3. iOS build errors**

```bash
# Clean iOS build
cd ios && rm -rf Pods Podfile.lock && pod install && cd ..
```

**4. "Cannot connect to backend" error**

Check that:

- Backend is running on the expected port
- Your `.env` file has the correct IP/URL
- No firewall is blocking connections
- For Android emulator, use `10.0.2.2` instead of `localhost`

**5. Module resolution errors**

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Platform-Specific Notes

**Android Emulator**:

- Use `http://10.0.2.2:8000` for localhost (not `http://localhost:8000`)
- Enable "Wipe data" in AVD Manager if app crashes on startup

**iOS Simulator**:

- Use `http://localhost:8000` for localhost
- If keyboard doesn't appear, press Cmd+K to toggle it

**Physical Devices**:

- Computer and device must be on same Wi-Fi network
- Use computer's local IP address (e.g., `http://192.168.1.100:8000`)
- Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

## Building for Production

### Android APK

```bash
expo build:android
```

### iOS IPA

```bash
expo build:ios
```

### EAS Build (Recommended)

```bash
npm install -g eas-cli
eas build --platform android
eas build --platform ios
```

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Write tests for new features
4. Run tests: `npm test`
5. Run linter: `npm run lint`
6. Submit a pull request

## License

MIT License - see LICENSE file for details
