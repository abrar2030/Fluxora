import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react-native";
import { HomeScreen } from "../../screens/HomeScreen";
import { AuthProvider } from "../../contexts/AuthContext";

const mockNavigation = {
  navigate: jest.fn(),
};

const mockAuth = {
  user: {
    id: "1",
    username: "testuser",
    email: "test@example.com",
  },
  logout: jest.fn(),
};

jest.mock("../../contexts/AuthContext", () => ({
  useAuth: () => mockAuth,
}));

describe("HomeScreen", () => {
  beforeEach(() => {
    mockNavigation.navigate.mockClear();
    mockAuth.logout.mockClear();
  });

  it("renders user information correctly", () => {
    const { getByText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    expect(getByText("Welcome, testuser")).toBeTruthy();
    expect(getByText("test@example.com")).toBeTruthy();
  });

  it("handles missing user data gracefully", () => {
    mockAuth.user = null;
    const { getByText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    expect(getByText("Welcome, Guest")).toBeTruthy();
  });

  it("navigates to profile screen when profile button is pressed", () => {
    const { getByTestId } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    fireEvent.press(getByTestId("profile-button"));
    expect(mockNavigation.navigate).toHaveBeenCalledWith("Profile");
  });

  it("handles logout correctly", async () => {
    const { getByTestId } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    fireEvent.press(getByTestId("logout-button"));

    await waitFor(() => {
      expect(mockAuth.logout).toHaveBeenCalled();
      expect(mockNavigation.navigate).toHaveBeenCalledWith("Login");
    });
  });

  it("handles logout error gracefully", async () => {
    mockAuth.logout.mockRejectedValueOnce(new Error("Logout failed"));
    const { getByTestId, getByText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    fireEvent.press(getByTestId("logout-button"));

    await waitFor(() => {
      expect(getByText("Failed to logout. Please try again.")).toBeTruthy();
    });
  });

  it("renders task list correctly", () => {
    const { getByTestId } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    expect(getByTestId("task-list")).toBeTruthy();
  });

  it("handles empty task list", () => {
    const { getByText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    expect(getByText("No tasks available")).toBeTruthy();
  });

  it("handles task creation", async () => {
    const { getByTestId, getByPlaceholderText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    const addButton = getByTestId("add-task-button");
    fireEvent.press(addButton);

    const titleInput = getByPlaceholderText("Task title");
    const descriptionInput = getByPlaceholderText("Task description");

    fireEvent.changeText(titleInput, "New Task");
    fireEvent.changeText(descriptionInput, "Task description");

    const submitButton = getByTestId("submit-task-button");
    fireEvent.press(submitButton);

    await waitFor(() => {
      expect(getByTestId("task-list")).toContainElement(
        getByTestId("task-New Task"),
      );
    });
  });

  it("handles task creation validation", async () => {
    const { getByTestId, getByPlaceholderText, getByText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    const addButton = getByTestId("add-task-button");
    fireEvent.press(addButton);

    const submitButton = getByTestId("submit-task-button");
    fireEvent.press(submitButton);

    await waitFor(() => {
      expect(getByText("Title is required")).toBeTruthy();
      expect(getByText("Description is required")).toBeTruthy();
    });
  });

  it("handles task completion", async () => {
    const { getByTestId } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    const taskCheckbox = getByTestId("task-checkbox-1");
    fireEvent.press(taskCheckbox);

    await waitFor(() => {
      expect(taskCheckbox).toHaveStyle({ backgroundColor: "#4CAF50" });
    });
  });

  it("handles task completion error", async () => {
    const { getByTestId, getByText } = render(
      <AuthProvider>
        <HomeScreen navigation={mockNavigation} />
      </AuthProvider>,
    );

    const taskCheckbox = getByTestId("task-checkbox-1");
    fireEvent.press(taskCheckbox);

    // Simulate error
    await waitFor(() => {
      expect(getByText("Failed to update task status")).toBeTruthy();
    });
  });
});
