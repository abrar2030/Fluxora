import React from "react";
import { Text } from "react-native";
import {
  act,
  render,
  renderHook,
  waitFor,
} from "@testing-library/react-native";
import {
  AuthProvider,
  extractErrorMessage,
  useAuth,
} from "../../src/contexts/AuthContext";
import * as api from "../../src/api/api";

jest.mock("../../src/api/api", () => ({
  clearTokens: jest.fn(),
  deleteCurrentUser: jest.fn(),
  fetchCurrentUser: jest.fn(),
  getAccessToken: jest.fn(),
  loginRequest: jest.fn(),
  registerForcedLogoutHandler: jest.fn(),
  registerRequest: jest.fn(),
  setTokens: jest.fn(),
  updateCurrentUser: jest.fn(),
}));

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

const user = { id: 1, email: "me@example.com" };

const setup = async () => {
  const hook = renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(hook.result.current.isInitializing).toBe(false));
  return hook;
};

describe("extractErrorMessage", () => {
  it("prefers the structured error message", () => {
    const err = {
      response: { data: { error: { message: "structured" }, detail: "d" } },
    };
    expect(extractErrorMessage(err, "fallback")).toBe("structured");
  });

  it("falls back through detail, string body, message and default", () => {
    expect(
      extractErrorMessage({ response: { data: { detail: "detail" } } }, "f"),
    ).toBe("detail");
    expect(extractErrorMessage({ response: { data: "plain" } }, "f")).toBe(
      "plain",
    );
    expect(extractErrorMessage(new Error("boom"), "f")).toBe("boom");
    expect(extractErrorMessage({}, "f")).toBe("f");
  });
});

describe("useAuth", () => {
  it("throws outside of an AuthProvider", () => {
    const spy = jest.spyOn(console, "error").mockImplementation(() => {});
    const Probe = () => {
      useAuth();
      return <Text>never</Text>;
    };
    expect(() => render(<Probe />)).toThrow(
      "useAuth must be used within an AuthProvider",
    );
    spy.mockRestore();
  });
});

describe("AuthProvider", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.getAccessToken.mockResolvedValue(null);
  });

  it("finishes initializing unauthenticated when there is no token", async () => {
    const { result } = await setup();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(api.fetchCurrentUser).not.toHaveBeenCalled();
  });

  it("restores the session when a token exists", async () => {
    api.getAccessToken.mockResolvedValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();
    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it("clears tokens when the stored session is invalid", async () => {
    const warn = jest.spyOn(console, "warn").mockImplementation(() => {});
    api.getAccessToken.mockResolvedValue("tok");
    api.fetchCurrentUser.mockRejectedValue(new Error("expired"));
    const { result } = await setup();
    expect(api.clearTokens).toHaveBeenCalled();
    expect(result.current.isAuthenticated).toBe(false);
    warn.mockRestore();
  });

  it("registers and unregisters the forced logout handler", async () => {
    const { unmount } = await setup();
    expect(api.registerForcedLogoutHandler).toHaveBeenCalledWith(
      expect.any(Function),
    );
    unmount();
    expect(api.registerForcedLogoutHandler).toHaveBeenLastCalledWith(null);
  });

  it("logs in and stores tokens", async () => {
    const tokens = { access_token: "a", refresh_token: "r" };
    api.loginRequest.mockResolvedValue(tokens);
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.login("me@example.com", "pw");
    });

    expect(outcome).toEqual({ success: true });
    expect(api.setTokens).toHaveBeenCalledWith(tokens);
    expect(result.current.user).toEqual(user);
  });

  it("reports login failures", async () => {
    api.loginRequest.mockRejectedValue({
      response: { data: { detail: "Bad credentials" } },
    });
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.login("me@example.com", "wrong");
    });

    expect(outcome).toEqual({ success: false, error: "Bad credentials" });
    expect(result.current.authError).toBe("Bad credentials");
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("registers, then signs in", async () => {
    api.registerRequest.mockResolvedValue({});
    api.loginRequest.mockResolvedValue({ access_token: "a" });
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.register("me@example.com", "password1");
    });

    expect(outcome).toEqual({ success: true });
    expect(api.registerRequest).toHaveBeenCalledWith(
      "me@example.com",
      "password1",
    );
    expect(result.current.user).toEqual(user);
  });

  it("reports registration failures with a fallback message", async () => {
    api.registerRequest.mockRejectedValue({});
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.register("me@example.com", "password1");
    });

    expect(outcome).toEqual({
      success: false,
      error: "Unable to create your account.",
    });
  });

  it("logs out", async () => {
    api.getAccessToken.mockResolvedValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();

    await act(async () => {
      await result.current.logout();
    });

    expect(api.clearTokens).toHaveBeenCalled();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("updates the profile and persists reissued tokens", async () => {
    const updated = { ...user, email: "new@example.com" };
    api.updateCurrentUser.mockResolvedValue({
      user: updated,
      access_token: "a2",
      refresh_token: "r2",
    });
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.updateProfile({
        email: "new@example.com",
      });
    });

    expect(outcome).toEqual({ success: true, user: updated });
    expect(api.setTokens).toHaveBeenCalledWith(
      expect.objectContaining({ access_token: "a2" }),
    );
    expect(result.current.user).toEqual(updated);
  });

  it("does not store tokens when the profile update returns none", async () => {
    api.updateCurrentUser.mockResolvedValue({ user });
    const { result } = await setup();

    await act(async () => {
      await result.current.updateProfile({ full_name: "Me" });
    });

    expect(api.setTokens).not.toHaveBeenCalled();
  });

  it("reports profile update failures", async () => {
    api.updateCurrentUser.mockRejectedValue({});
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.updateProfile({});
    });

    expect(outcome).toEqual({
      success: false,
      error: "Unable to update your profile.",
    });
  });

  it("deletes the account and clears the session", async () => {
    api.getAccessToken.mockResolvedValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    api.deleteCurrentUser.mockResolvedValue(true);
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.deleteAccount();
    });

    expect(outcome).toEqual({ success: true });
    expect(api.clearTokens).toHaveBeenCalled();
    expect(result.current.user).toBeNull();
  });

  it("keeps the session when account deletion fails", async () => {
    api.getAccessToken.mockResolvedValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    api.deleteCurrentUser.mockRejectedValue({});
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.deleteAccount();
    });

    expect(outcome).toEqual({
      success: false,
      error: "Unable to delete your account.",
    });
    expect(result.current.user).toEqual(user);
  });

  it("clears the user when the forced logout handler fires", async () => {
    api.getAccessToken.mockResolvedValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();
    const handler = api.registerForcedLogoutHandler.mock.calls[0][0];

    act(() => handler());

    expect(result.current.user).toBeNull();
  });
});
