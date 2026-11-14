import "@/lib/server/base64-polyfill" // must load before jose/pdf.js — see that file
import { cookies, headers } from "next/headers"
import { NextResponse } from "next/server"
import bcrypt from "bcryptjs"
import { SignJWT, jwtVerify } from "jose"
import { queryOne } from "@/lib/server/db"

// Self-hosted email/password auth: bcrypt password hashes + HS256 JWT in an
// httpOnly cookie. Roles live on the users table and are read fresh per request.

export const TOKEN_COOKIE = "devhive_token"
const TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7

export type Role = "admin" | "manager" | "employee"
export type SessionUser = { id: string; email: string; role: Role }

function secret(): Uint8Array {
  const s = process.env.JWT_SECRET
  if (!s) throw new Error("JWT_SECRET is not set")
  return new TextEncoder().encode(s)
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export async function createToken(userId: string): Promise<string> {
  return new SignJWT({})
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(userId)
    .setIssuedAt()
    .setExpirationTime(`${TOKEN_TTL_SECONDS}s`)
    .sign(secret())
}

export async function setSessionCookie(token: string) {
  ;(await cookies()).set(TOKEN_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: TOKEN_TTL_SECONDS,
  })
}

export async function clearSessionCookie() {
  ;(await cookies()).delete(TOKEN_COOKIE)
}

async function userIdFromToken(token: string | undefined): Promise<string | null> {
  if (!token) return null
  try {
    const { payload } = await jwtVerify(token, secret(), { algorithms: ["HS256"] })
    return typeof payload.sub === "string" ? payload.sub : null
  } catch {
    return null
  }
}

/** The logged-in user (from the session cookie or a Bearer header), or null. */
export async function getCurrentUser(): Promise<SessionUser | null> {
  let token = (await cookies()).get(TOKEN_COOKIE)?.value
  if (!token) {
    const auth = (await headers()).get("authorization")
    if (auth?.toLowerCase().startsWith("bearer ")) token = auth.slice(7)
  }
  const userId = await userIdFromToken(token)
  if (!userId) return null
  return queryOne<SessionUser>("SELECT id, email, role FROM users WHERE id = $1", [userId])
}

// ---------- helpers for API route handlers ----------

export class HttpError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

export async function requireUser(...roles: Role[]): Promise<SessionUser> {
  const user = await getCurrentUser()
  if (!user) throw new HttpError(401, "Invalid authentication credentials")
  if (roles.length && !roles.includes(user.role)) {
    throw new HttpError(403, `Access denied. Required roles: ${roles.join(", ")}`)
  }
  return user
}

/** Wraps a route handler: maps HttpError/unknown errors to JSON `{ detail }` responses. */
export function handle<A extends unknown[]>(fn: (...args: A) => Promise<Response>) {
  return async (...args: A): Promise<Response> => {
    try {
      return await fn(...args)
    } catch (err) {
      if (err instanceof HttpError) {
        return NextResponse.json({ detail: err.message }, { status: err.status })
      }
      console.error(err)
      return NextResponse.json({ detail: "Internal server error" }, { status: 500 })
    }
  }
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
export function assertUuid(id: string, what = "Resource") {
  if (!UUID_RE.test(id)) throw new HttpError(404, `${what} not found`)
}
