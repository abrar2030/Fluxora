import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import SignUp from "../../pages/SignUp";

jest.mock("../../context/AuthContext", () => ({
  useAuth: jest.fn(),
}));

const renderPage = (register = jest.fn()) => {
  useAuth.mockReturnValue({ register });
  render(
    <MemoryRouter initialEntries={["/signup"]}>
      <Routes>
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<div>dashboard page</div>} />
      </Routes>
    </MemoryRouter>,
  );
  return { register, user: userEvent.setup() };
};

const fill = async (user, { email, password, confirm, agree = true }) => {
  if (email) await user.type(screen.getByLabelText("Email address"), email);
  if (password) await user.type(screen.getByLabelText("Password"), password);
  if (confirm) {
    await user.type(screen.getByLabelText("Confirm password"), confirm);
  }
  if (agree) await user.click(screen.getByRole("checkbox"));
};

const submit = (user) =>
  user.click(screen.getByRole("button", { name: "Create account" }));

describe("SignUp page", () => {
  it("renders the form", () => {
    renderPage();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Confirm password")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Create account" }),
    ).toBeInTheDocument();
  });

  it("requires every field", async () => {
    const { register, user } = renderPage();
    await submit(user);
    expect(screen.getByText("Please fill in every field.")).toBeInTheDocument();
    expect(register).not.toHaveBeenCalled();
  });

  it("enforces the minimum password length", async () => {
    const { register, user } = renderPage();
    await fill(user, {
      email: "me@example.com",
      password: "short",
      confirm: "short",
    });
    await submit(user);
    expect(
      screen.getByText("Password must be at least 8 characters long."),
    ).toBeInTheDocument();
    expect(register).not.toHaveBeenCalled();
  });

  it("requires matching passwords", async () => {
    const { register, user } = renderPage();
    await fill(user, {
      email: "me@example.com",
      password: "password1",
      confirm: "password2",
    });
    await submit(user);
    expect(screen.getByText("Passwords do not match.")).toBeInTheDocument();
    expect(register).not.toHaveBeenCalled();
  });

  it("requires accepting the terms", async () => {
    const { register, user } = renderPage();
    await fill(user, {
      email: "me@example.com",
      password: "password1",
      confirm: "password1",
      agree: false,
    });
    await submit(user);
    expect(
      screen.getByText("Please accept the terms to continue."),
    ).toBeInTheDocument();
    expect(register).not.toHaveBeenCalled();
  });

  it("registers and redirects to the dashboard", async () => {
    const register = jest.fn().mockResolvedValue({ success: true });
    const { user } = renderPage(register);
    await fill(user, {
      email: "me@example.com",
      password: "password1",
      confirm: "password1",
    });

    await submit(user);

    await waitFor(() =>
      expect(screen.getByText("dashboard page")).toBeInTheDocument(),
    );
    expect(register).toHaveBeenCalledWith("me@example.com", "password1");
  });

  it("shows the server error when registration fails", async () => {
    const register = jest
      .fn()
      .mockResolvedValue({ success: false, error: "Email already registered" });
    const { user } = renderPage(register);
    await fill(user, {
      email: "me@example.com",
      password: "password1",
      confirm: "password1",
    });

    await submit(user);

    expect(
      await screen.findByText("Email already registered"),
    ).toBeInTheDocument();
    expect(screen.queryByText("dashboard page")).not.toBeInTheDocument();
  });
});
