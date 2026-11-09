/** Base URL for calls made from the Next.js server (inside Docker this is the service name). */
export const API_INTERNAL_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

/** Base URL the browser uses. */
export const API_PUBLIC_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApiStatus =
  | { reachable: true; version: string }
  | { reachable: false; error: string };

export async function getApiStatus(): Promise<ApiStatus> {
  try {
    const res = await fetch(`${API_INTERNAL_URL}/health`, {
      cache: "no-store",
      signal: AbortSignal.timeout(2000),
    });
    if (!res.ok) return { reachable: false, error: `HTTP ${res.status}` };
    const body = (await res.json()) as { version: string };
    return { reachable: true, version: body.version };
  } catch (err) {
    return { reachable: false, error: err instanceof Error ? err.name : "unknown error" };
  }
}
