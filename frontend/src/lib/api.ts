/**
 * Browser-side helper for calling the app's own API routes (/api/*).
 * The httpOnly session cookie is sent automatically.
 */
export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const res = await fetch(`/api${path.startsWith("/") ? path : `/${path}`}`, init)
  if (res.status === 401 && typeof window !== "undefined") {
    window.location.href = "/login?message=Session%20expired.%20Please%20sign%20in%20again."
  }
  return res
}

export async function apiJson<T = any>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, init)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed (${res.status})`)
  }
  return res.json() as Promise<T>
}
