import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Appbar, List, Switch, Divider, Card, Title, Paragraph, useTheme } from 'react-native-paper';

const SettingsScreen = ({ navigation }) => {
  const theme = useTheme();
  const [notificationsEnabled, setNotificationsEnabled] = React.useState(false);
  const [darkModeEnabled, setDarkModeEnabled] = React.useState(false); // This would typically control the theme

  const toggleNotifications = () => setNotificationsEnabled(previousState => !previousState);
  const toggleDarkMode = () => {
    setDarkModeEnabled(previousState => !previousState);
    // In a real app, you would likely trigger a theme change here
    // e.g., using a context or state management library
    alert('Dark mode toggle is illustrative. Theme switching not implemented.');
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        {/* <Appbar.BackAction onPress={() => navigation.goBack()} /> */}
        <Appbar.Content title="Settings" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        <List.Section title="Preferences">
          <List.Item
            title="Enable Notifications"
            right={() => (
              <Switch
                value={notificationsEnabled}
                onValueChange={toggleNotifications}
                color={theme.colors.primary}
              />
            )}
          />
          <Divider />
          <List.Item
            title="Dark Mode"
            description="Apply dark theme across the app"
            right={() => (
              <Switch
                value={darkModeEnabled}
                onValueChange={toggleDarkMode}
                color={theme.colors.primary}
              />
            )}
          />
        </List.Section>

        <Divider style={styles.divider} />

        {/* Placeholder for other settings like Account, Data Usage etc. */}
        <List.Section title="Account">
            <List.Item
                title="Profile"
                left={() => <List.Icon icon="account-circle-outline" />}
                onPress={() => alert('Navigate to Profile Screen (Not Implemented)')}
            />
            <List.Item
                title="Logout"
                left={() => <List.Icon icon="logout" />}
                onPress={() => alert('Logout Action (Not Implemented)')}
            />
        </List.Section>

        <Divider style={styles.divider} />

        <Card style={styles.card}>
          <Card.Content>
            <Title>About Fluxora</Title>
            <Paragraph>Version: 1.0.0</Paragraph>
            <Paragraph>Manage your energy predictions and analytics on the go.</Paragraph>
          </Card.Content>
        </Card>
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
    // padding: 15, // List.Section provides some padding
  },
  divider: {
    marginVertical: 10,
  },
  card: {
    margin: 15,
    elevation: 3,
  },
});

export default SettingsScreen;
