"use server"

import { createClient } from "@/utils/supabase/server"
import { redirect } from "next/navigation"

export async function login(formData: FormData) {
  const email = (formData.get("email") as string).toLowerCase()
  const password = formData.get("password") as string
  const supabase = await createClient()

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

  const { error, data } = await supabase.auth.signUp({
    email,
    password,
  })

  if (error) {
    console.error("Signup Error:", error.message)
    return redirect(`/login?message=${encodeURIComponent(error.message)}`)
  }

  // If session is present (Auto-confirm is on), redirect to home
  if (data?.session) {
    return redirect("/")
  }

  // Fallback for when email confirmation is still enabled in Supabase
  return redirect("/login?message=Check email to continue sign in process")
}

export async function logout() {
  const supabase = await createClient()
  await supabase.auth.signOut()
  redirect("/login")
}
