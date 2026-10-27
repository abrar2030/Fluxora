import { act, renderHook, waitFor } from "@testing-library/react";
import {
  AuthProvider,
  extractErrorMessage,
  useAuth,
} from "../../context/AuthContext";
import * as api from "../../utils/api";

jest.mock("../../utils/api", () => ({
  clearTokens: jest.fn(),
  deleteCurrentUser: jest.fn(),
  fetchCurrentUser: jest.fn(),
  getAccessToken: jest.fn(),
  loginRequest: jest.fn(),
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
  it("prefers the structured message, then detail, string body and message", () => {
    expect(
      extractErrorMessage(
        {
          response: { data: { error: { message: "structured" }, detail: "d" } },
        },
        "f",
      ),
    ).toBe("structured");
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
    expect(() => renderHook(() => useAuth())).toThrow(
      "useAuth must be used within an AuthProvider",
    );
    spy.mockRestore();
  });
});

describe("AuthProvider", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.getAccessToken.mockReturnValue(null);
  });

  it("initializes unauthenticated without a token", async () => {
    const { result } = await setup();
    expect(result.current.isAuthenticated).toBe(false);
    expect(api.fetchCurrentUser).not.toHaveBeenCalled();
  });

  it("restores the session from a stored token", async () => {
    api.getAccessToken.mockReturnValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();
    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it("clears tokens when the stored session is invalid", async () => {
    api.getAccessToken.mockReturnValue("tok");
    api.fetchCurrentUser.mockRejectedValue(new Error("expired"));
    const { result } = await setup();
    expect(api.clearTokens).toHaveBeenCalled();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("signs in and stores tokens", async () => {
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

  it("reports sign in failures", async () => {
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
  });

  it("registers then signs in", async () => {
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
    api.getAccessToken.mockReturnValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();

    act(() => result.current.logout());

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

  it("skips token storage when the update returns none", async () => {
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

  it("deletes the account", async () => {
    api.getAccessToken.mockReturnValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    api.deleteCurrentUser.mockResolvedValue(true);
    const { result } = await setup();

    let outcome;
    await act(async () => {
      outcome = await result.current.deleteAccount();
    });

    expect(outcome).toEqual({ success: true });
    expect(result.current.user).toBeNull();
  });

  it("keeps the session when deletion fails", async () => {
    api.getAccessToken.mockReturnValue("tok");
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

  it("clears the user on a fluxora:logout event", async () => {
    api.getAccessToken.mockReturnValue("tok");
    api.fetchCurrentUser.mockResolvedValue(user);
    const { result } = await setup();

    act(() => {
      window.dispatchEvent(new CustomEvent("fluxora:logout"));
    });

    expect(result.current.user).toBeNull();
  });
});
