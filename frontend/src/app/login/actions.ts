"use server"

import { createClient } from "@/utils/supabase/server"
import { redirect } from "next/navigation"

export async function login(formData: FormData) {
  const email = (formData.get("email") as string).toLowerCase()
  const password = formData.get("password") as string
  const supabase = await createClient()

  if (password.length < 6) {
    return redirect(`/login?message=${encodeURIComponent("Password must be at least 6 characters")}`)
  }

  const { error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })

  if (error) {
    console.error("Login Error:", error.message)
    return redirect(`/login?message=${encodeURIComponent(error.message)}`)
  }

  return redirect("/")
}

export async function signup(formData: FormData) {
  const email = (formData.get("email") as string).toLowerCase()
  const password = formData.get("password") as string
  const supabase = await createClient()

  if (password.length < 6) {
    return redirect(`/login?message=${encodeURIComponent("Password must be at least 6 characters")}`)
  }

  const { error, data } = await supabase.auth.signUp({
    email,
    password,
  })

  if (error) {
    // If user already exists, logic fallthrough to attempt login anyway
    if (error.message.includes("already registered") || error.message.includes("already exists")) {
      const loginRes = await supabase.auth.signInWithPassword({ email, password })
      if (!loginRes.error) return redirect("/")
    }
    console.error("Signup Error:", error.message)
    return redirect(`/login?message=${encodeURIComponent(error.message)}`)
  }

  // If session is present (Auto-confirm is on), redirect to home
  if (data?.session) {
    return redirect("/")
  }

  // Final fallback: try to sign in immediately (works if unconfirmed is allowed)
  const finalLogin = await supabase.auth.signInWithPassword({ email, password })
  if (!finalLogin.error) return redirect("/")

  return redirect("/login?message=Check email to continue sign in process")
}

export async function logout() {
  const supabase = await createClient()
  await supabase.auth.signOut()
  redirect("/login")
}
