import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import apiClient, {
  clearTokens,
  createDataRecord,
  getAccessToken,
  getAnalytics,
  getDataRecords,
  getHealthStatus,
  getPredictions,
  getRefreshToken,
  loginRequest,
  registerForcedLogoutHandler,
  setTokens,
} from "../../src/api/api";
import { STORAGE_KEYS } from "../../src/constants/config";

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

describe("token storage helpers", () => {
  beforeEach(async () => {
    await AsyncStorage.clear();
  });

  it("stores and reads both tokens", async () => {
    await setTokens({ access_token: "a1", refresh_token: "r1" });
    expect(await getAccessToken()).toBe("a1");
    expect(await getRefreshToken()).toBe("r1");
  });

  it("only stores the tokens that are provided", async () => {
    await setTokens({ access_token: "only-access" });
    expect(await getAccessToken()).toBe("only-access");
    expect(await getRefreshToken()).toBeNull();
  });

  it("does nothing when no tokens are provided", async () => {
    await setTokens({});
    expect(await getAccessToken()).toBeNull();
  });

  it("clears both tokens", async () => {
    await setTokens({ access_token: "a1", refresh_token: "r1" });
    await clearTokens();
    expect(await getAccessToken()).toBeNull();
    expect(await getRefreshToken()).toBeNull();
  });
});

describe("apiClient", () => {
  let adapter;

  beforeEach(async () => {
    await AsyncStorage.clear();
    adapter = jest.fn((config) => Promise.resolve(okResponse(config)));
    apiClient.defaults.adapter = adapter;
    registerForcedLogoutHandler(null);
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("attaches the bearer token when one is stored", async () => {
    await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, "tok");
    await apiClient.get("/v1/auth/me");
    expect(adapter.mock.calls[0][0].headers.Authorization).toBe("Bearer tok");
  });

  it("omits the Authorization header when no token is stored", async () => {
    await apiClient.get("/v1/auth/me");
    expect(adapter.mock.calls[0][0].headers.Authorization).toBeUndefined();
  });

  it("skips auth for requests flagged with X-Skip-Auth", async () => {
    await AsyncStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, "tok");
    await getHealthStatus();
    expect(adapter.mock.calls[0][0].headers.Authorization).toBeUndefined();
    expect(adapter.mock.calls[0][0].url).toBe("/health");
  });

  it("sends login credentials as form encoded data", async () => {
    adapter.mockImplementation((config) =>
      Promise.resolve(okResponse(config, { access_token: "x" })),
    );
    const data = await loginRequest("me@example.com", "pw");
    const config = adapter.mock.calls[0][0];
    expect(data).toEqual({ access_token: "x" });
    expect(config.url).toBe("/v1/auth/token");
    expect(config.data).toBe("username=me%40example.com&password=pw");
    expect(config.headers["Content-Type"]).toBe(
      "application/x-www-form-urlencoded",
    );
  });

  it("passes pagination and query parameters", async () => {
    await getDataRecords({ skip: 5, limit: 10 });
    await getAnalytics("year");
    await getPredictions(3);
    expect(adapter.mock.calls[0][0].params).toEqual({ skip: 5, limit: 10 });
    expect(adapter.mock.calls[1][0].params).toEqual({ period: "year" });
    expect(adapter.mock.calls[2][0].params).toEqual({ days: 3 });
  });

  it("posts new data records", async () => {
    await createDataRecord({ value: 1 });
    const config = adapter.mock.calls[0][0];
    expect(config.method).toBe("post");
    expect(config.url).toBe("/v1/data/");
  });

  describe("401 handling", () => {
    it("refreshes the token and retries the original request", async () => {
      await setTokens({ access_token: "old", refresh_token: "ref" });
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
      expect(adapter).toHaveBeenCalledTimes(2);
      expect(adapter.mock.calls[1][0].headers.Authorization).toBe("Bearer new");
      expect(await getAccessToken()).toBe("new");
      expect(await getRefreshToken()).toBe("ref2");
    });

    it("clears tokens and triggers forced logout when refresh fails", async () => {
      await setTokens({ access_token: "old", refresh_token: "ref" });
      const onLogout = jest.fn();
      registerForcedLogoutHandler(onLogout);
      jest.spyOn(axios, "post").mockRejectedValue(new Error("refresh failed"));
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 401)),
      );

      await expect(apiClient.get("/v1/users/")).rejects.toThrow(
        "refresh failed",
      );

      expect(onLogout).toHaveBeenCalledTimes(1);
      expect(await getAccessToken()).toBeNull();
      expect(await getRefreshToken()).toBeNull();
    });

    it("does not attempt a refresh without a refresh token", async () => {
      const post = jest.spyOn(axios, "post");
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 401)),
      );

      await expect(apiClient.get("/v1/users/")).rejects.toThrow(
        "status code 401",
      );
      expect(post).not.toHaveBeenCalled();
    });

    it("does not refresh for auth endpoints", async () => {
      await setTokens({ access_token: "old", refresh_token: "ref" });
      const post = jest.spyOn(axios, "post");
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 401)),
      );

      await expect(apiClient.post("/v1/auth/token", {})).rejects.toThrow(
        "status code 401",
      );
      expect(post).not.toHaveBeenCalled();
    });

    it("passes non-401 errors through untouched", async () => {
      await setTokens({ access_token: "old", refresh_token: "ref" });
      const post = jest.spyOn(axios, "post");
      adapter.mockImplementation((config) =>
        Promise.reject(httpError(config, 500)),
      );

      await expect(apiClient.get("/v1/users/")).rejects.toThrow(
        "status code 500",
      );
      expect(post).not.toHaveBeenCalled();
    });
  });
});
