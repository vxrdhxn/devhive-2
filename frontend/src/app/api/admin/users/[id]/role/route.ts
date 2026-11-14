import { NextRequest, NextResponse } from "next/server"
import { HttpError, assertUuid, handle, requireUser } from "@/lib/auth"
import { queryOne } from "@/lib/server/db"

type Ctx = { params: Promise<{ id: string }> }
const ROLES = ["admin", "manager", "employee"]

export const PATCH = handle(async (req: NextRequest, ctx: Ctx) => {
  const current = await requireUser("admin")
  const { id } = await ctx.params
  assertUuid(id, "User")
  const { role } = await req.json().catch(() => ({}))
  if (!ROLES.includes(role)) throw new HttpError(400, `role must be one of: ${ROLES.join(", ")}`)
  if (id === current.id && role !== "admin") throw new HttpError(400, "You cannot remove your own admin role")

  const row = await queryOne("UPDATE users SET role = $1 WHERE id = $2 RETURNING id, email, role, created_at", [role, id])
  if (!row) throw new HttpError(404, "User not found")
  return NextResponse.json(row)
})
