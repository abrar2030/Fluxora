import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { Login } from "../../components/Login";
import { AuthProvider } from "../../contexts/AuthContext";

const mockLogin = jest.fn();

jest.mock("../../contexts/AuthContext", () => ({
  ...jest.requireActual("../../contexts/AuthContext"),
  useAuth: () => ({
    login: mockLogin,
    error: null,
    loading: false,
  }),
}));

describe("Login Component", () => {
  beforeEach(() => {
    mockLogin.mockClear();
  });

  it("renders login form correctly", () => {
    render(
      <AuthProvider>
        <Login />
      </AuthProvider>,
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in/i }),
    ).toBeInTheDocument();
  });

  it("handles form submission correctly", async () => {
    render(
      <AuthProvider>
        <Login />
      </AuthProvider>,
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
    });
  });

  it("shows validation errors for invalid input", async () => {
    render(
      <AuthProvider>
        <Login />
      </AuthProvider>,
    );

    const submitButton = screen.getByRole("button", { name: /sign in/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it("shows error message when login fails", async () => {
    mockLogin.mockRejectedValueOnce(new Error("Invalid credentials"));

    render(
      <AuthProvider>
        <Login />
      </AuthProvider>,
    );

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "wrongpassword" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});
