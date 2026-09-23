"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken, getCurrentUser, AuthUser } from "@/lib/auth";

/**
 * Client-side portal guard: redirects to /login when there's no session or
 * the logged-in user's role isn't allowed for this portal. Renders nothing
 * for the page until the check has run, so protected content never flashes
 * for an unauthenticated visitor.
 */
export function useAuthGuard(allowedRoles: string[]) {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    const cu = getCurrentUser();

    if (!token || !cu || !allowedRoles.includes(cu.role)) {
      router.replace("/login");
      return;
    }

    setUser(cu);
    setChecking(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { user, checking };
}
