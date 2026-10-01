// One helper for all backend calls: adds the JWT token and turns errors into messages.
const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function api(path, { method = "GET", body } = {}) {
  const token = localStorage.getItem("token");
  const res = await fetch(API + path, {
    method,
    headers: { "Content-Type": "application/json", ...(token && { Authorization: `Bearer ${token}` }) },
    body: body && JSON.stringify(body),
  });
  if (!res.ok) {
    const e = await res.json().catch(() => ({}));
    throw new Error(typeof e.detail === "string" ? e.detail : "Request failed");
  }
  return res.json();
}

// remove empty filter values before building a query string
export const qs = (o) => new URLSearchParams(Object.fromEntries(Object.entries(o).filter(([, v]) => v))).toString();
