import React from "react";
import { fireEvent, render, waitFor } from "@testing-library/react-native";
import { PaperProvider } from "react-native-paper";
import SignUpScreen from "../../src/screens/SignUpScreen";
import { useAuth } from "../../src/contexts/AuthContext";

jest.mock("../../src/contexts/AuthContext", () => ({
  useAuth: jest.fn(),
}));

const setup = (register = jest.fn()) => {
  useAuth.mockReturnValue({ register });
  const navigation = { navigate: jest.fn(), reset: jest.fn() };
  const utils = render(
    <PaperProvider>
      <SignUpScreen navigation={navigation} />
    </PaperProvider>,
  );
  return { ...utils, navigation, register };
};

const fill = (utils, email, password, confirm) => {
  const [emailInput, passwordInput, confirmInput] = utils.getAllByTestId(
    "text-input-outlined",
  );
  fireEvent.changeText(emailInput, email);
  fireEvent.changeText(passwordInput, password);
  fireEvent.changeText(confirmInput, confirm);
};

const submit = (utils) =>
  fireEvent.press(utils.getByRole("button", { name: "Create account" }));

describe("SignUpScreen", () => {
  it("renders the heading and three inputs", () => {
    const utils = setup();
    expect(utils.getByText("Create your account")).toBeTruthy();
    expect(utils.getAllByTestId("text-input-outlined")).toHaveLength(3);
  });

  it("requires every field", () => {
    const utils = setup();
    submit(utils);
    expect(utils.getByText("Please fill in every field.")).toBeTruthy();
    expect(utils.register).not.toHaveBeenCalled();
  });

  it("enforces the minimum password length", () => {
    const utils = setup();
    fill(utils, "me@example.com", "short", "short");
    submit(utils);
    expect(
      utils.getByText("Password must be at least 8 characters long."),
    ).toBeTruthy();
    expect(utils.register).not.toHaveBeenCalled();
  });

  it("requires matching passwords", () => {
    const utils = setup();
    fill(utils, "me@example.com", "password1", "password2");
    submit(utils);
    expect(utils.getByText("Passwords do not match.")).toBeTruthy();
    expect(utils.register).not.toHaveBeenCalled();
  });

  it("registers and navigates to the main app", async () => {
    const register = jest.fn().mockResolvedValue({ success: true });
    const utils = setup(register);
    fill(utils, "me@example.com", "password1", "password1");

    submit(utils);

    await waitFor(() =>
      expect(utils.navigation.reset).toHaveBeenCalledWith({
        index: 0,
        routes: [{ name: "Main" }],
      }),
    );
    expect(register).toHaveBeenCalledWith("me@example.com", "password1");
  });

  it("shows the server error when registration fails", async () => {
    const register = jest
      .fn()
      .mockResolvedValue({ success: false, error: "Email already registered" });
    const utils = setup(register);
    fill(utils, "me@example.com", "password1", "password1");

    submit(utils);

    await waitFor(() =>
      expect(utils.getByText("Email already registered")).toBeTruthy(),
    );
    expect(utils.navigation.reset).not.toHaveBeenCalled();
  });
});
