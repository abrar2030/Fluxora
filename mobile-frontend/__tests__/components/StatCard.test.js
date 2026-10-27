import React from "react";
import { render } from "@testing-library/react-native";
import { PaperProvider } from "react-native-paper";
import StatCard from "../../src/components/StatCard";

const renderCard = (props) =>
  render(
    <PaperProvider>
      <StatCard icon="flash" label="Usage" value="42 kWh" {...props} />
    </PaperProvider>,
  );

describe("StatCard", () => {
  it("renders the label and value", () => {
    const { getByText } = renderCard();
    expect(getByText("Usage")).toBeTruthy();
    expect(getByText("42 kWh")).toBeTruthy();
  });

  it("renders the hint when provided", () => {
    const { getByText } = renderCard({ hint: "vs last week" });
    expect(getByText("vs last week")).toBeTruthy();
  });

  it("omits the hint when not provided", () => {
    const { queryByText } = renderCard();
    expect(queryByText("vs last week")).toBeNull();
  });
});
