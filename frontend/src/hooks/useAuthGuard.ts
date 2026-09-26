"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AuthUser, bootstrapSession, portalForRole } from "@/lib/auth";

/**
 * Client-side portal guard: decides which UI to show. It is NOT a security
 * boundary — the backend authorises every API call. The user and role come from
 * the server (restored via the httpOnly refresh cookie), never from browser
 * storage, so they can't be edited from DevTools.
 *
 * Renders nothing for the page until the check has run, so protected UI never
 * flashes for an unauthenticated visitor.
 */
export function useAuthGuard(allowedRoles: string[]) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let cancelled = false;

    bootstrapSession().then((u) => {
      if (cancelled) return;

      if (!u) {
        router.replace("/login");
        return;
      }
      if (!allowedRoles.includes(u.role)) {
        // Signed in, but this isn't their portal (or their role has none).
        router.replace(portalForRole(u.role) ?? "/login");
        return;
      }

      setUser(u);
      setChecking(false);
    });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { user, checking };
}
