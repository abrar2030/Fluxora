import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import SignIn from "../../pages/SignIn";

jest.mock("../../context/AuthContext", () => ({
  useAuth: jest.fn(),
}));

const renderPage = (login = jest.fn(), entry = "/signin") => {
  useAuth.mockReturnValue({ login });
  render(
    <MemoryRouter initialEntries={[entry]}>
      <Routes>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<div>signup page</div>} />
        <Route path="/dashboard" element={<div>dashboard page</div>} />
        <Route path="/" element={<div>home page</div>} />
      </Routes>
    </MemoryRouter>,
  );
  return { login, user: userEvent.setup() };
};

describe("SignIn page", () => {
  it("renders the form", () => {
    renderPage();
    expect(
      screen.getByRole("heading", { name: "Sign in" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument();
  });

  it("requires both fields", async () => {
    const { login, user } = renderPage();
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(
      screen.getByText("Please enter both your email and password."),
    ).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it("signs in and redirects to the dashboard", async () => {
    const login = jest.fn().mockResolvedValue({ success: true });
    const { user } = renderPage(login);

    await user.type(screen.getByLabelText("Email address"), "me@example.com");
    await user.type(screen.getByLabelText("Password"), "secret123");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() =>
      expect(screen.getByText("dashboard page")).toBeInTheDocument(),
    );
    expect(login).toHaveBeenCalledWith("me@example.com", "secret123");
  });

  it("shows the server error when sign in fails", async () => {
    const login = jest
      .fn()
      .mockResolvedValue({ success: false, error: "Bad credentials" });
    const { user } = renderPage(login);

    await user.type(screen.getByLabelText("Email address"), "me@example.com");
    await user.type(screen.getByLabelText("Password"), "wrong");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByText("Bad credentials")).toBeInTheDocument();
    expect(screen.queryByText("dashboard page")).not.toBeInTheDocument();
  });

  it("toggles password visibility", async () => {
    const { user } = renderPage();
    const input = screen.getByLabelText("Password");
    expect(input).toHaveAttribute("type", "password");

    await user.click(screen.getByTestId("VisibilityIcon").closest("button"));

    expect(input).toHaveAttribute("type", "text");
  });

  it("links to sign up and the homepage", async () => {
    const { user } = renderPage();
    await user.click(screen.getByRole("link", { name: "Create an account" }));
    expect(screen.getByText("signup page")).toBeInTheDocument();
  });
});
