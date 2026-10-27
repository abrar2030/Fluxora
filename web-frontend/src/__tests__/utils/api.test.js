import axios from "axios";
import apiClient, {
  API_BASE_URL,
  clearTokens,
  createDataRecord,
  deleteDataRecord,
  getAccessToken,
  getAnalytics,
  getDataRecords,
  getDataRecordsInRange,
  getHealthStatus,
  getPredictions,
  getRefreshToken,
  getUsers,
  loginRequest,
  registerRequest,
  setTokens,
} from "../../utils/api";

const okResponse = (config, data = {}, status = 200) => ({
  data,
  status,
  statusText: "OK",
  headers: {},
  config,
});

const httpError = (config, status) => {
  const error = new Error(`Request failed with status code ${status}`);
  error.config = config;
  error.response = { status, data: {}, config };
  return error;
};

describe("token helpers", () => {
  beforeEach(() => localStorage.clear());

  it("stores and reads tokens", () => {
    setTokens({ access_token: "a", refresh_token: "r" });
    expect(getAccessToken()).toBe("a");
    expect(getRefreshToken()).toBe("r");
  });

  it("ignores missing tokens", () => {
    setTokens({ access_token: "a" });
    expect(getRefreshToken()).toBeNull();
    setTokens({});
    expect(getAccessToken()).toBe("a");
  });

  it("clears tokens", () => {
    setTokens({ access_token: "a", refresh_token: "r" });
    clearTokens();
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });
});

describe("apiClient", () => {
  let adapter;

  beforeEach(() => {
    localStorage.clear();
    adapter = jest.fn((config) => Promise.resolve(okResponse(config)));
    apiClient.defaults.adapter = adapter;
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("falls back to the local backend URL", () => {
    expect(API_BASE_URL).toBe("http://localhost:8000");
    expect(apiClient.defaults.baseURL).toBe("http://localhost:8000");
  });

  it("attaches the bearer token", async () => {
    setTokens({ access_token: "tok" });
    await apiClient.get("/v1/auth/me");
    expect(adapter.mock.calls[0][0].headers.Authorization).toBe("Bearer tok");
  });

  it("omits Authorization without a token", async () => {
    await apiClient.get("/v1/auth/me");
    expect(adapter.mock.calls[0][0].headers.Authorization).toBeUndefined();
  });

  it("skips auth for the health check", async () => {
    setTokens({ access_token: "tok" });
    await getHealthStatus();
    expect(adapter.mock.calls[0][0].headers.Authorization).toBeUndefined();
    expect(adapter.mock.calls[0][0].url).toBe("/health");
  });

  it("posts login credentials as a form", async () => {
    adapter.mockImplementation((config) =>
      Promise.resolve(okResponse(config, { access_token: "x" })),
    );
    const data = await loginRequest("me@example.com", "pw");
    const config = adapter.mock.calls[0][0];
    expect(data).toEqual({ access_token: "x" });
    expect(config.url).toBe("/v1/auth/token");
    expect(String(config.data)).toBe("username=me%40example.com&password=pw");
  });

  it("posts registration details", async () => {
    await registerRequest("me@example.com", "pw");
    const config = adapter.mock.calls[0][0];
    expect(config.url).toBe("/v1/auth/register");
    expect(JSON.parse(config.data)).toEqual({
      email: "me@example.com",
      password: "pw",
    });
  });

  it("builds query parameters", async () => {
    await getUsers({ skip: 2, limit: 5 });
    await getDataRecords();
    await getDataRecordsInRange("s", "e");
    await getAnalytics("week");
    await getPredictions(14);
    const params = adapter.mock.calls.map((c) => c[0].params);
    expect(params).toEqual([
      { skip: 2, limit: 5 },
      { skip: 0, limit: 100 },
      { start_time: "s", end_time: "e" },
      { period: "week" },
      { days: 14 },
    ]);
  });

  it("creates and deletes records", async () => {
    await createDataRecord({ value: 1 });
    expect(await deleteDataRecord(7)).toBe(true);
    expect(adapter.mock.calls[0][0].method).toBe("post");
    expect(adapter.mock.calls[1][0].url).toBe("/v1/data/7");
    expect(adapter.mock.calls[1][0].method).toBe("delete");
  });

  describe("401 handling", () => {
    it("refreshes the token and retries", async () => {
      setTokens({ access_token: "old", refresh_token: "ref" });
      jest.spyOn(axios, "post").mockResolvedValue({
        data: { access_token: "new", refresh_token: "ref2" },
      });
      adapter
        .mockImplementationOnce((config) =>
          Promise.reject(httpError(config, 401)),
        )
        .mockImplementationOnce((config) =>
          Promise.resolve(okResponse(config, { ok: true })),
        );

      const response = await apiClient.get("/v1/users/");

      expect(response.data).toEqual({ ok: true });
      expect(adapter.mock.calls[1][0].headers.Authorization).toBe("Bearer new");
      expect(getAccessToken()).toBe("new");
      expect(getRefreshToken()).toBe("ref2");
    });

    it("clears tokens and emits fluxora:logout when refresh fails", async () => {
      setTokens({ access_token: "old", refresh_token: "ref" });
      jest.spyOn(axios, "post").mockRejectedValue(new Error("refresh failed"));
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 401)),
      );
      const onLogout = jest.fn();
      window.addEventListener("fluxora:logout", onLogout);

      await expect(apiClient.get("/v1/users/")).rejects.toThrow(
        "refresh failed",
      );

      window.removeEventListener("fluxora:logout", onLogout);
      expect(onLogout).toHaveBeenCalledTimes(1);
      expect(getAccessToken()).toBeNull();
    });

    it("emits fluxora:logout for a 401 with no refresh token", async () => {
      setTokens({ access_token: "old" });
      const post = jest.spyOn(axios, "post");
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 401)),
      );
      const onLogout = jest.fn();
      window.addEventListener("fluxora:logout", onLogout);

      await expect(apiClient.get("/v1/users/")).rejects.toThrow(
        "status code 401",
      );

      window.removeEventListener("fluxora:logout", onLogout);
      expect(post).not.toHaveBeenCalled();
      expect(onLogout).toHaveBeenCalledTimes(1);
      expect(getAccessToken()).toBeNull();
    });

    it("does not refresh for auth endpoints", async () => {
      setTokens({ access_token: "old", refresh_token: "ref" });
      const post = jest.spyOn(axios, "post");
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 401)),
      );

      await expect(apiClient.post("/v1/auth/token", {})).rejects.toThrow(
        "status code 401",
      );
      expect(post).not.toHaveBeenCalled();
    });

    it("passes other errors through", async () => {
      setTokens({ access_token: "old", refresh_token: "ref" });
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 500)),
      );
      await expect(apiClient.get("/v1/users/")).rejects.toThrow(
        "status code 500",
      );
      expect(getAccessToken()).toBe("old");
    });
  });
});
