"use server"

import { redirect } from "next/navigation"
import { clearSessionCookie, createToken, hashPassword, setSessionCookie, verifyPassword } from "@/lib/auth"
import { queryOne } from "@/lib/server/db"

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function readCredentials(formData: FormData): { email: string; password: string } | string {
  const email = String(formData.get("email") || "").trim().toLowerCase()
  const password = String(formData.get("password") || "")
  if (!EMAIL_RE.test(email)) return "Enter a valid email address"
  if (password.length < 6 || password.length > 128) return "Password must be 6-128 characters"
  return { email, password }
}

const fail = (message: string): never => redirect(`/login?message=${encodeURIComponent(message)}`)

export async function login(formData: FormData) {
  const creds = readCredentials(formData)
  if (typeof creds === "string") fail(creds)
  const { email, password } = creds as { email: string; password: string }

  const user = await queryOne<{ id: string; password_hash: string }>(
    "SELECT id, password_hash FROM users WHERE email = $1",
    [email],
  )
  if (!user || !(await verifyPassword(password, user.password_hash))) fail("Invalid email or password")

  await setSessionCookie(await createToken(user!.id))
  redirect("/")
}

export async function signup(formData: FormData) {
  const creds = readCredentials(formData)
  if (typeof creds === "string") fail(creds)
  const { email, password } = creds as { email: string; password: string }

  let userId: string | undefined
  try {
    // The very first account becomes the workspace admin so someone can manage roles.
    const row = await queryOne<{ id: string }>(
      `INSERT INTO users (email, password_hash, role)
       VALUES ($1, $2, CASE WHEN EXISTS (SELECT 1 FROM users) THEN 'employee' ELSE 'admin' END)
       RETURNING id`,
      [email, await hashPassword(password)],
    )
    userId = row!.id
  } catch (err: any) {
    if (err?.code === "23505") {
      // Already registered: log in instead if the password matches.
      const existing = await queryOne<{ id: string; password_hash: string }>(
        "SELECT id, password_hash FROM users WHERE email = $1",
        [email],
      )
      if (existing && (await verifyPassword(password, existing.password_hash))) {
        await setSessionCookie(await createToken(existing.id))
        redirect("/")
      }
      fail("An account with this email already exists")
    }
    console.error("Signup failed:", err)
    fail("Could not create account. Please try again.")
  }

  await setSessionCookie(await createToken(userId!))
  redirect("/")
}

export async function logout() {
  await clearSessionCookie()
  redirect("/login")
}
