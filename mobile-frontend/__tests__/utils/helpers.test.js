import {
  calculatePercentageChange,
  debounce,
  deepClone,
  formatDate,
  formatFileSize,
  formatNumber,
  generateId,
  isEmptyObject,
  isValidEmail,
  sleep,
  truncateText,
} from "../../src/utils/helpers";

describe("formatNumber", () => {
  it("formats with two decimals by default", () => {
    expect(formatNumber(3.14159)).toBe("3.14");
  });

  it("respects a custom number of decimals", () => {
    expect(formatNumber(3.14159, 4)).toBe("3.1416");
  });

  it("returns N/A for null, undefined and NaN", () => {
    expect(formatNumber(null)).toBe("N/A");
    expect(formatNumber(undefined)).toBe("N/A");
    expect(formatNumber(NaN)).toBe("N/A");
  });
});

describe("formatDate", () => {
  const date = new Date(2024, 0, 15, 10, 30, 0);

  it("returns N/A for falsy input", () => {
    expect(formatDate(null)).toBe("N/A");
    expect(formatDate("")).toBe("N/A");
  });

  it("returns Invalid Date for unparseable strings", () => {
    expect(formatDate("not-a-date")).toBe("Invalid Date");
  });

  it("formats the long variant", () => {
    expect(formatDate(date, "long")).toBe("January 15, 2024");
  });

  it("accepts ISO strings", () => {
    expect(formatDate("2024-01-15T12:00:00Z", "long")).toMatch(
      /January 1[45], 2024/,
    );
  });

  it("supports short, time, datetime and unknown formats", () => {
    expect(formatDate(date, "short")).toBe(date.toLocaleDateString());
    expect(formatDate(date, "time")).toBe(date.toLocaleTimeString());
    expect(formatDate(date, "datetime")).toBe(
      `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`,
    );
    expect(formatDate(date, "other")).toBe(date.toLocaleDateString());
  });
});

describe("calculatePercentageChange", () => {
  it("returns a signed percentage", () => {
    expect(calculatePercentageChange(100, 150)).toBe("+50.0%");
    expect(calculatePercentageChange(100, 75)).toBe("-25.0%");
  });

  it("returns N/A when the old value is zero or missing", () => {
    expect(calculatePercentageChange(0, 10)).toBe("N/A");
    expect(calculatePercentageChange(undefined, 10)).toBe("N/A");
  });
});

describe("truncateText", () => {
  it("returns an empty string for falsy input", () => {
    expect(truncateText("")).toBe("");
    expect(truncateText(null)).toBe("");
  });

  it("leaves short text untouched", () => {
    expect(truncateText("short", 10)).toBe("short");
  });

  it("truncates long text with an ellipsis", () => {
    expect(truncateText("abcdefghijkl", 8)).toBe("abcde...");
  });
});

describe("debounce", () => {
  beforeEach(() => jest.useFakeTimers());
  afterEach(() => jest.useRealTimers());

  it("only invokes the function once after the wait", () => {
    const fn = jest.fn();
    const debounced = debounce(fn, 200);

    debounced("a");
    debounced("b");
    debounced("c");
    expect(fn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(200);
    expect(fn).toHaveBeenCalledTimes(1);
    expect(fn).toHaveBeenCalledWith("c");
  });
});

describe("isValidEmail", () => {
  it("accepts well formed addresses", () => {
    expect(isValidEmail("user@example.com")).toBe(true);
  });

  it("rejects malformed addresses", () => {
    expect(isValidEmail("user@")).toBe(false);
    expect(isValidEmail("user example@x.com")).toBe(false);
    expect(isValidEmail("")).toBe(false);
  });
});

describe("generateId", () => {
  it("creates distinct ids", () => {
    expect(generateId()).not.toBe(generateId());
  });
});

describe("deepClone / isEmptyObject", () => {
  it("clones without sharing references", () => {
    const original = { a: { b: 1 } };
    const copy = deepClone(original);
    copy.a.b = 2;
    expect(original.a.b).toBe(1);
  });

  it("detects empty objects", () => {
    expect(isEmptyObject({})).toBe(true);
    expect(isEmptyObject({ a: 1 })).toBe(false);
  });
});

describe("formatFileSize", () => {
  it("formats common sizes", () => {
    expect(formatFileSize(0)).toBe("0 Bytes");
    expect(formatFileSize(1024)).toBe("1 KB");
    expect(formatFileSize(1536)).toBe("1.5 KB");
    expect(formatFileSize(1024 * 1024)).toBe("1 MB");
  });
});

describe("sleep", () => {
  it("resolves after the delay", async () => {
    jest.useFakeTimers();
    const done = jest.fn();
    sleep(100).then(done);
    jest.advanceTimersByTime(100);
    await Promise.resolve();
    expect(done).toHaveBeenCalled();
    jest.useRealTimers();
  });
});
