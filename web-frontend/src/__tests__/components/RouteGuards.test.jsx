import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import AdminRoute from "../../components/AdminRoute";
import ProtectedRoute from "../../components/ProtectedRoute";
import PublicOnlyRoute from "../../components/PublicOnlyRoute";
import { useAuth } from "../../context/AuthContext";

jest.mock("../../context/AuthContext", () => ({
  useAuth: jest.fn(),
}));

const renderGuard = (Guard, initialPath) =>
  render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route element={<Guard />}>
          <Route path="/guarded" element={<div>guarded content</div>} />
        </Route>
        <Route path="/signin" element={<div>sign in page</div>} />
        <Route path="/dashboard" element={<div>dashboard page</div>} />
      </Routes>
    </MemoryRouter>,
  );

describe("ProtectedRoute", () => {
  it("shows a loading screen while the session initializes", () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isInitializing: true });
    renderGuard(ProtectedRoute, "/guarded");
    expect(screen.getByText("Checking your session…")).toBeInTheDocument();
    expect(screen.queryByText("guarded content")).not.toBeInTheDocument();
  });

  it("renders children when authenticated", () => {
    useAuth.mockReturnValue({ isAuthenticated: true, isInitializing: false });
    renderGuard(ProtectedRoute, "/guarded");
    expect(screen.getByText("guarded content")).toBeInTheDocument();
  });

  it("redirects to /signin when unauthenticated", () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isInitializing: false });
    renderGuard(ProtectedRoute, "/guarded");
    expect(screen.getByText("sign in page")).toBeInTheDocument();
    expect(screen.queryByText("guarded content")).not.toBeInTheDocument();
  });
});

describe("PublicOnlyRoute", () => {
  it("shows a loading screen while initializing", () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isInitializing: true });
    renderGuard(PublicOnlyRoute, "/guarded");
    expect(screen.getByText("Loading Fluxora…")).toBeInTheDocument();
  });

  it("renders children for guests", () => {
    useAuth.mockReturnValue({ isAuthenticated: false, isInitializing: false });
    renderGuard(PublicOnlyRoute, "/guarded");
    expect(screen.getByText("guarded content")).toBeInTheDocument();
  });

  it("redirects authenticated users to the dashboard", () => {
    useAuth.mockReturnValue({ isAuthenticated: true, isInitializing: false });
    renderGuard(PublicOnlyRoute, "/guarded");
    expect(screen.getByText("dashboard page")).toBeInTheDocument();
  });
});

describe("AdminRoute", () => {
  it("shows a loading screen while initializing", () => {
    useAuth.mockReturnValue({ user: null, isInitializing: true });
    renderGuard(AdminRoute, "/guarded");
    expect(screen.getByText("Loading Fluxora…")).toBeInTheDocument();
  });

  it("renders children for superusers", () => {
    useAuth.mockReturnValue({
      user: { is_superuser: true },
      isInitializing: false,
    });
    renderGuard(AdminRoute, "/guarded");
    expect(screen.getByText("guarded content")).toBeInTheDocument();
  });

  it("redirects regular users to the dashboard", () => {
    useAuth.mockReturnValue({
      user: { is_superuser: false },
      isInitializing: false,
    });
    renderGuard(AdminRoute, "/guarded");
    expect(screen.getByText("dashboard page")).toBeInTheDocument();
  });

  it("redirects when there is no user", () => {
    useAuth.mockReturnValue({ user: null, isInitializing: false });
    renderGuard(AdminRoute, "/guarded");
    expect(screen.getByText("dashboard page")).toBeInTheDocument();
  });
});
