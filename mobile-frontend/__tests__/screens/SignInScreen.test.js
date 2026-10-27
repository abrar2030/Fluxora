import React from "react";
import { fireEvent, render, waitFor } from "@testing-library/react-native";
import { PaperProvider } from "react-native-paper";
import SignInScreen from "../../src/screens/SignInScreen";
import { useAuth } from "../../src/contexts/AuthContext";

jest.mock("../../src/contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

const setup = (login = jest.fn()) => {
  useAuth.mockReturnValue({ login });
  const navigation = { navigate: jest.fn(), reset: jest.fn() };
  const utils = render(
    <PaperProvider>
      <SignInScreen navigation={navigation} />
    </PaperProvider>,
  );
  return { ...utils, navigation, login };
};

const inputs = (utils) => utils.getAllByTestId("text-input-outlined");

const fill = (utils, email, password) => {
  const [emailInput, passwordInput] = inputs(utils);
  fireEvent.changeText(emailInput, email);
  fireEvent.changeText(passwordInput, password);
};

describe("SignInScreen", () => {
  it("renders the form", () => {
    const utils = setup();
    expect(inputs(utils)).toHaveLength(2);
    expect(utils.getAllByText("Email address").length).toBeGreaterThan(0);
    expect(utils.getAllByText("Password").length).toBeGreaterThan(0);
    expect(utils.getByRole("button", { name: "Sign in" })).toBeTruthy();
    expect(utils.getByText("Create an account")).toBeTruthy();
  });

  it("requires both email and password", () => {
    const utils = setup();
    fireEvent.press(utils.getByRole("button", { name: "Sign in" }));
    expect(
      utils.getByText("Please enter both your email and password."),
    ).toBeTruthy();
    expect(utils.login).not.toHaveBeenCalled();
  });

  it("navigates to the main app after a successful sign in", async () => {
    const login = jest.fn().mockResolvedValue({ success: true });
    const utils = setup(login);
    fill(utils, "me@example.com", "secret123");

    fireEvent.press(utils.getByRole("button", { name: "Sign in" }));

    await waitFor(() =>
      expect(utils.navigation.reset).toHaveBeenCalledWith({
        index: 0,
        routes: [{ name: "Main" }],
      }),
    );
    expect(login).toHaveBeenCalledWith("me@example.com", "secret123");
  });

  it("shows the server error when sign in fails", async () => {
    const login = jest
      .fn()
      .mockResolvedValue({ success: false, error: "Bad credentials" });
    const utils = setup(login);
    fill(utils, "me@example.com", "wrong");

    fireEvent.press(utils.getByRole("button", { name: "Sign in" }));

    await waitFor(() =>
      expect(utils.getByText("Bad credentials")).toBeTruthy(),
    );
    expect(utils.navigation.reset).not.toHaveBeenCalled();
  });

  it("links to sign up and back to the homepage", () => {
    const utils = setup();
    fireEvent.press(utils.getByText("Create an account"));
    expect(utils.navigation.navigate).toHaveBeenCalledWith("SignUp");
    fireEvent.press(utils.getByText(/Back to homepage/));
    expect(utils.navigation.navigate).toHaveBeenCalledWith("Home");
  });
});
