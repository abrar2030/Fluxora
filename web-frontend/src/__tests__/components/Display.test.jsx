import { render, screen } from "@testing-library/react";
import LoadingScreen from "../../components/LoadingScreen";
import StatCard from "../../components/StatCard";

describe("StatCard", () => {
  it("renders label, value and hint", () => {
    render(
      <StatCard
        icon={<span data-testid="icon" />}
        label="Usage"
        value="42 kWh"
        hint="vs last week"
      />,
    );
    expect(screen.getByText("Usage")).toBeInTheDocument();
    expect(screen.getByText("42 kWh")).toBeInTheDocument();
    expect(screen.getByText("vs last week")).toBeInTheDocument();
    expect(screen.getByTestId("icon")).toBeInTheDocument();
  });

  it("hides the value and shows a skeleton while loading", () => {
    const { container } = render(
      <StatCard icon={null} label="Usage" value="42 kWh" loading />,
    );
    expect(screen.queryByText("42 kWh")).not.toBeInTheDocument();
    expect(container.querySelector(".MuiSkeleton-root")).toBeInTheDocument();
  });

  it("omits the hint when not provided", () => {
    render(<StatCard icon={null} label="Usage" value="1" />);
    expect(screen.queryByText("vs last week")).not.toBeInTheDocument();
  });
});

describe("LoadingScreen", () => {
  it("shows the default label", () => {
    render(<LoadingScreen />);
    expect(screen.getByText("Loading Fluxora…")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("shows a custom label", () => {
    render(<LoadingScreen label="Please wait" />);
    expect(screen.getByText("Please wait")).toBeInTheDocument();
  });
});
