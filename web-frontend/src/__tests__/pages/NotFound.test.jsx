import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import NotFound from "../../pages/NotFound";

jest.mock("../../context/AuthContext", () => ({
  useAuth: jest.fn(),
}));

const renderPage = (isAuthenticated) => {
  useAuth.mockReturnValue({ isAuthenticated });
  render(
    <MemoryRouter initialEntries={["/404"]}>
      <Routes>
        <Route path="/404" element={<NotFound />} />
        <Route path="/dashboard" element={<div>dashboard page</div>} />
        <Route path="/" element={<div>home page</div>} />
      </Routes>
    </MemoryRouter>,
  );
  return userEvent.setup();
};

describe("NotFound page", () => {
  it("sends guests back to the homepage", async () => {
    const user = renderPage(false);
    expect(screen.getByText("404")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Back to Homepage" }));
    expect(screen.getByText("home page")).toBeInTheDocument();
  });

  it("sends signed in users back to the dashboard", async () => {
    const user = renderPage(true);
    await user.click(screen.getByRole("button", { name: "Back to Dashboard" }));
    expect(screen.getByText("dashboard page")).toBeInTheDocument();
  });
});
