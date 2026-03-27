/**
 * API client — fetch wrapper for backend calls via BFF proxy.
 */

export interface ApiResponse<T> {
  data: T | null;
  error: { code: string; message: string } | null;
}

export async function apiPost<T>(
  path: string,
  body: Record<string, unknown>,
): Promise<ApiResponse<T>> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    credentials: "include",
  });
  return res.json() as Promise<ApiResponse<T>>;
}

export async function apiGet<T>(path: string): Promise<ApiResponse<T>> {
  const res = await fetch(path, {
    credentials: "include",
  });
  return res.json() as Promise<ApiResponse<T>>;
}
