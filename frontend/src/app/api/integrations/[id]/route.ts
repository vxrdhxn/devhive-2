import { NextRequest, NextResponse } from "next/server"
import { HttpError, assertUuid, handle, requireUser } from "@/lib/auth"
import { query, queryOne } from "@/lib/server/db"
import { isPrivileged } from "@/lib/server/access"

type Ctx = { params: Promise<{ id: string }> }

// Remove a bridge (owner, or admin/manager).
export const DELETE = handle(async (_req: NextRequest, ctx: Ctx) => {
  const user = await requireUser()
  const { id } = await ctx.params
  assertUuid(id, "Integration")
  const row = await queryOne<{ user_id: string }>("SELECT user_id FROM integrations WHERE id = $1", [id])
  if (!row) throw new HttpError(404, "Integration not found")
  if (row.user_id !== user.id && !isPrivileged(user)) {
    throw new HttpError(403, "Not authorized to delete this integration")
  }
  await query("DELETE FROM integrations WHERE id = $1", [id])
  return NextResponse.json({ message: "Integration removed successfully" })
})
