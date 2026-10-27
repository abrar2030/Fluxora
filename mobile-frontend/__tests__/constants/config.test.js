describe("config", () => {
  afterEach(() => {
    jest.resetModules();
  });

  const load = (os) => {
    jest.resetModules();
    jest.doMock("react-native", () => ({ Platform: { OS: os } }));
    return require("../../src/constants/config");
  };

  it("uses localhost on iOS by default", () => {
    expect(load("ios").API_BASE_URL).toBe("http://localhost:8000");
  });

  it("uses the emulator alias on Android by default", () => {
    expect(load("android").API_BASE_URL).toBe("http://10.0.2.2:8000");
  });

  it("exposes storage keys and timeout", () => {
    const config = load("ios");
    expect(config.STORAGE_KEYS.ACCESS_TOKEN).toBe("fluxora_access_token");
    expect(config.STORAGE_KEYS.REFRESH_TOKEN).toBe("fluxora_refresh_token");
    expect(config.API_TIMEOUT).toBe(30000);
    expect(config.default.API_BASE_URL).toBe(config.API_BASE_URL);
  });
});
