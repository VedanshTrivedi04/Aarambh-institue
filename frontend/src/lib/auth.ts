"use client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export interface AuthUser {
  id: string;
  email: string;
  mobile?: string | null;
  role: "SUPER_ADMIN" | "ADMIN" | "MANAGEMENT" | "TEACHER" | "STUDENT" | "PARENT" | string;
  status: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type?: string;
  user?: AuthUser;
}

export const DEMO_ADMIN: AuthUser = {
  id: "17b17871-b615-4593-b2c6-d0a743a3868e",
  email: "admin@aarambhinstitute.com",
  mobile: "8839714081",
  role: "ADMIN",
  status: "ACTIVE",
  first_name: "Aarambh",
  last_name: "Admin",
};

export const DEMO_TEACHER: AuthUser = {
  id: "2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d",
  email: "pankaj.dubey@aarambhinstitute.com",
  mobile: "8839714081",
  role: "TEACHER",
  status: "ACTIVE",
  first_name: "Pankaj",
  last_name: "Dubey",
};

export const DEMO_STUDENT: AuthUser = {
  id: "3b4c5d6e-7f8a-9b0c-1d2e-3f4a5b6c7d8e",
  email: "student@aarambhinstitute.com",
  mobile: "8839714081",
  role: "STUDENT",
  status: "ACTIVE",
  first_name: "Prince",
  last_name: "Yadav",
};

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("aarambh_access_token");
}

export function getCurrentUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("aarambh_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setAuthSession(token: string, user: AuthUser) {
  if (typeof window === "undefined") return;
  localStorage.setItem("aarambh_access_token", token);
  localStorage.setItem("aarambh_user", JSON.stringify(user));
  document.cookie = `aarambh_token=${token}; path=/; max-age=86400; SameSite=Lax`;
}

export function clearAuthSession() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("aarambh_access_token");
  localStorage.removeItem("aarambh_user");
  document.cookie = `aarambh_token=; path=/; max-age=0`;
}

/**
 * Login with email or mobile + password
 */
export async function loginUser(
  identifier: string,
  password: string
): Promise<{ success: boolean; user?: AuthUser; error?: string }> {

  // --- Demo credential short-circuit (works whether backend is up or down) ---
  if (identifier === "admin@aarambhinstitute.com" && password === "AarambhAdmin@2026") {
    setAuthSession("demo_admin_jwt_token", DEMO_ADMIN);
    return { success: true, user: DEMO_ADMIN };
  }
  if (identifier === "pankaj.dubey@aarambhinstitute.com" && password === "AarambhTeacher@2026") {
    setAuthSession("demo_teacher_jwt_token", DEMO_TEACHER);
    return { success: true, user: DEMO_TEACHER };
  }
  if (identifier === "student@aarambhinstitute.com" && password === "AarambhStudent@2026") {
    setAuthSession("demo_student_jwt_token", DEMO_STUDENT);
    return { success: true, user: DEMO_STUDENT };
  }
  // ---------------------------------------------------------------------------

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      return {
        success: false,
        error: errData.detail || "Invalid login credentials. Please check your email and password.",
      };
    }

    const data: LoginResponse = await res.json();
    const token = data.access_token;

    // Fetch user details or use fallback
    let user = data.user;
    if (!user) {
      const meRes = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (meRes.ok) {
        user = await meRes.json();
      } else {
        user = {
          ...DEMO_ADMIN,
          email: identifier,
        };
      }
    }

    if (user && token) {
      setAuthSession(token, user);
      return { success: true, user };
    }

    return { success: false, error: "Failed to establish user session" };
  } catch (err: any) {
    return {
      success: false,
      error: err?.message || "Network error. Please make sure the backend server is running.",
    };
  }
}

/**
 * Authenticated API Fetcher
 */
export async function authFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data?: T; error?: string; status: number }> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      // Session expired
      clearAuthSession();
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
