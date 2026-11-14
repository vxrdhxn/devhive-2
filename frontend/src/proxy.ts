import { NextResponse, type NextRequest } from "next/server"

const TOKEN_COOKIE = "devhive_token"

// Lightweight gate: redirect to /login when there is no session cookie.
// The token itself is validated by the backend (pages call /auth/me).
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const isPublic = pathname.startsWith("/login") || pathname.startsWith("/api/")

  if (!isPublic && !request.cookies.get(TOKEN_COOKIE)?.value) {
    const url = request.nextUrl.clone()
    url.pathname = "/login"
    url.search = ""
    return NextResponse.redirect(url)
  }
  return NextResponse.next()
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
