"use client";

import { apiBase } from "@/lib/apiBase";

/**
 * Session model
 * -------------
 * - The short-lived access token and the user object live in module memory only.
 *   Nothing auth-related is written to localStorage or a JS-readable cookie, so an
 *   XSS bug can't lift a long-lived credential out of storage.
 * - The refresh token is an httpOnly cookie set by the backend (path /api/v1/auth).
 *   On a page load the session is restored by calling /auth/refresh.
 * - Identity and role always come from the backend's response. Nothing here is
 *   trusted from the client: the route guards below only decide what UI to show,
 *   the backend enforces access on every request.
 */

export interface AuthUser {
  id: string;
  email: string | null;
  mobile?: string | null;
  role: "SUPER_ADMIN" | "ADMIN" | "MANAGEMENT" | "TEACHER" | "STUDENT" | "PARENT" | string;
  status: string;
  first_name?: string;
  last_name?: string;
}

interface TokenResponse {
  access_token: string;
  token_type?: string;
  expires_in?: number;
  user: AuthUser;
}

const ADMIN_ROLES = ["SUPER_ADMIN", "ADMIN", "MANAGEMENT", "ACCOUNTANT", "COUNSELLOR"];

let accessToken: string | null = null;
let currentUser: AuthUser | null = null;

// Refresh tokens rotate, and the backend treats reuse of an old one as theft and
// revokes every session. Concurrent callers (React strict-mode double effects,
// several requests failing with 401 at once) must therefore share one refresh.
let refreshInFlight: Promise<boolean> | null = null;

export function getAuthToken(): string | null {
  return accessToken;
}

export function getCurrentUser(): AuthUser | null {
  return currentUser;
}

/** Where a user of this role should land after signing in; null if the role has no portal. */
export function portalForRole(role: string | undefined): string | null {
  if (role && ADMIN_ROLES.includes(role)) return "/admin";
  if (role === "TEACHER") return "/teacher";
  if (role === "STUDENT" || role === "PARENT") return "/student";
  return null;
}

function setSession(token: string, user: AuthUser) {
  accessToken = token;
  currentUser = user;
}

/** Forget the in-memory session and purge anything older builds left in the browser. */
export function clearAuthSession() {
  accessToken = null;
  currentUser = null;
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem("aarambh_access_token");
    localStorage.removeItem("aarambh_user");
  } catch {
    /* storage unavailable */
  }
  document.cookie = "aarambh_token=; path=/; max-age=0";
}

async function parseError(res: Response, fallback: string): Promise<string> {
  const body = await res.json().catch(() => null);
  return (typeof body?.detail === "string" && body.detail) || fallback;
}

/**
 * Exchange the httpOnly refresh cookie for a new access token.
 * Returns false when there is no valid session.
 */
export function refreshSession(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    try {
      const res = await fetch(`${apiBase()}/api/v1/auth/refresh`, {
        method: "POST",
        credentials: "include",
      });
      if (!res.ok) {
        accessToken = null;
        currentUser = null;
        return false;
      }
      const data: TokenResponse = await res.json();
      setSession(data.access_token, data.user);
      return true;
    } catch {
      return false;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

/** Resolve the signed-in user, restoring the session from the refresh cookie if needed. */
export async function bootstrapSession(): Promise<AuthUser | null> {
  if (accessToken && currentUser) return currentUser;
  const ok = await refreshSession();
  return ok ? currentUser : null;
}

/**
 * Login with email or mobile + password.
 */
export async function loginUser(
  identifier: string,
  password: string
): Promise<{ success: boolean; user?: AuthUser; error?: string }> {
  try {
    const res = await fetch(`${apiBase()}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ identifier, password }),
    });

    if (!res.ok) {
      return {
        success: false,
        error: await parseError(res, "Invalid login credentials. Please check your email and password."),
      };
    }

    const data: TokenResponse = await res.json();
    if (!data.access_token || !data.user) {
      return { success: false, error: "Failed to establish user session" };
    }

    setSession(data.access_token, data.user);
    return { success: true, user: data.user };
  } catch {
    return {
      success: false,
      error: "Could not reach the server. Please check your connection and try again.",
    };
  }
}

/** Revoke the session server-side (clears the refresh cookie), then forget it locally. */
export async function logoutUser(): Promise<void> {
  try {
    await fetch(`${apiBase()}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    /* still clear the local session below */
  } finally {
    clearAuthSession();
  }
}

/**
 * Authenticated API Fetcher
 * On a 401 it refreshes the session once and retries; if that fails the user is
 * sent back to /login.
 */
export async function authFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data?: T; error?: string; status: number }> {
  const url = endpoint.startsWith("http") ? endpoint : `${apiBase()}${endpoint}`;

  const send = () => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
    return fetch(url, { ...options, headers, credentials: "include" });
  };

  try {
    // No token in memory (e.g. right after a reload): try to restore before the first call.
    if (!accessToken) await refreshSession();

    let res = await send();

    if (res.status === 401) {
      if (await refreshSession()) {
        res = await send();
      }
      if (res.status === 401) {
        clearAuthSession();
        if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
          // Full navigation on purpose: drops all in-memory page state of the dead session.
          // eslint-disable-next-line @next/next/no-location-assign-relative-destination
          window.location.assign("/login");
        }
      }
    }

    const json = await res.json().catch(() => null);

    if (!res.ok) {
      return {
        error: json?.detail || `Request failed with status ${res.status}`,
        status: res.status,
      };
    }

    return { data: json, status: res.status };
  } catch (err: any) {
    return {
      error: err?.message || "Failed to connect to backend",
      status: 0,
    };
  }
}
