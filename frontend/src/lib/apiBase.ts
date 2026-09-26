/**
 * Where API requests go.
 *
 * Server side (RSC, route handlers) talks to the backend directly.
 * In the browser we use a relative URL: next.config.ts proxies /api/v1/* to the
 * backend, so the browser only ever talks to our own origin. That keeps the
 * httpOnly refresh cookie first-party (it would be a blocked third-party cookie
 * on Safari/Chrome if the browser called onrender.com directly) and means the
 * backend doesn't need to trust foreign origins via CORS.
 */
export const BACKEND_URL =
  process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export function apiBase(): string {
  return typeof window === "undefined" ? BACKEND_URL : "";
}
