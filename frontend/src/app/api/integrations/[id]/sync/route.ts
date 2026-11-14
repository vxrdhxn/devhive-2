import { NextRequest, NextResponse } from "next/server"
import { HttpError, assertUuid, handle, requireUser } from "@/lib/auth"
import { query, queryOne } from "@/lib/server/db"
import { isPrivileged } from "@/lib/server/access"
import { PUBLIC_COLUMNS, syncIntegration } from "@/lib/server/integrations"

export const maxDuration = 300

type Ctx = { params: Promise<{ id: string }> }

// Sync a bridge (owner, or admin/manager). Content is indexed as the bridge owner's.
export const POST = handle(async (_req: NextRequest, ctx: Ctx) => {
  const user = await requireUser()
  const { id } = await ctx.params
  assertUuid(id, "Integration")
  const integration = await queryOne("SELECT * FROM integrations WHERE id = $1", [id])
  if (!integration) throw new HttpError(404, "Integration not found")
  if (integration.user_id !== user.id && !isPrivileged(user)) {
    throw new HttpError(403, "Access denied. Only the owner or an administrator can sync this bridge.")
  }
  if (!integration.api_token) throw new HttpError(400, "Integration is missing API token")

  await query("UPDATE integrations SET status = 'syncing' WHERE id = $1", [id])
  try {
    const result = await syncIntegration(integration, integration.user_id)
    const updated = await queryOne(
      `UPDATE integrations SET status = 'active', last_synced_at = now() WHERE id = $1 RETURNING ${PUBLIC_COLUMNS}`,
      [id],
    )
    return NextResponse.json({ ...result, integration: updated })
  } catch (err) {
    await query("UPDATE integrations SET status = 'error' WHERE id = $1", [id])
    throw new HttpError(500, `Sync failed: ${(err as Error).message || "Internal processing error during synchronization"}`)
  }
})
