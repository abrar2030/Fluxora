# Apps Directory

## Overview

The `apps` directory contains the application code for different platforms in the Fluxora project. This directory follows a modular architecture that separates the codebase by platform, allowing for independent development and maintenance of each application while sharing common functionality.

## Structure

The directory is organized into the following subdirectories:

- **backend**: Contains backend application code specific to the apps layer, including API tests and authentication tests.
- **mobile**: A React Native mobile application for iOS and Android platforms, built with Expo.
- **web**: A React-based web application with a modern frontend architecture.

## Mobile Application

The mobile application is built using React Native with Expo for cross-platform compatibility. Key features include:

- Navigation system using React Navigation
- Screen components for Analytics, Dashboard, Predictions, and Settings
- API integration for data fetching
- Testing setup with Jest

### Key Files

- `App.js`: Main application entry point
- `src/navigation/AppNavigator.js`: Navigation configuration
- `src/screens/`: Screen components
- `src/api/api.js`: API integration

## Web Application

The web application is built using React with a modern frontend stack. Key features include:

- Component-based architecture
- Page routing
- API integration
- Theming support

### Key Files

- `src/App.jsx`: Main application component
- `src/components/`: Reusable UI components
- `src/pages/`: Page components
- `src/utils/`: Utility functions including API integration

## Development

To work with the applications in this directory:

1. Choose the platform you want to work with (backend, mobile, or web)
2. Navigate to the respective directory
3. Install dependencies using the package manager specified in the package.json
4. Follow the platform-specific development workflow

### Mobile Development

```bash
cd apps/mobile
npm install
npm start
```

### Web Development

```bash
cd apps/web
npm install
npm run dev
```

## Testing

Each application includes its own testing setup:

- Mobile: Jest tests in `src/tests/`
- Web: Jest and React Testing Library in `src/tests/`

Run tests using the respective package manager commands defined in each application's package.json.

## Deployment

The applications can be built for production using their respective build commands:

- Mobile: `npm run build`
- Web: `npm run build`

Refer to the deployment documentation in the `deployments` directory for information on deploying these applications to production environments.
