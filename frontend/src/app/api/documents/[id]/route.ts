import { NextRequest, NextResponse } from "next/server"
import { HttpError, assertUuid, handle, requireUser } from "@/lib/auth"
import { query, queryOne } from "@/lib/server/db"
import { isPrivileged, visibleDocsSql } from "@/lib/server/access"

type Ctx = { params: Promise<{ id: string }> }

// A document the user may see, with its chunks in original order.
export const GET = handle(async (_req: NextRequest, ctx: Ctx) => {
  const user = await requireUser()
  const { id } = await ctx.params
  assertUuid(id, "Document")
  const params: unknown[] = [id]
  const doc = await queryOne(
    `SELECT d.id, d.filename, d.file_type, d.uploaded_by, d.status, d.is_private, d.metadata, d.created_at
     FROM documents d WHERE d.id = $1 AND ${visibleDocsSql(user, "d", params)}`,
    params,
  )
  if (!doc) throw new HttpError(404, "Document not found")
  const chunks = await query(
    `SELECT id, content, metadata FROM chunks WHERE document_id = $1
     ORDER BY COALESCE((metadata->>'index')::int, 0)`,
    [id],
  )
  return NextResponse.json({ ...doc, chunks })
})

// Delete a document (owner, or admin/manager). Chunks go via ON DELETE CASCADE.
export const DELETE = handle(async (_req: NextRequest, ctx: Ctx) => {
  const user = await requireUser()
  const { id } = await ctx.params
  assertUuid(id, "Document")
  const doc = await queryOne<{ uploaded_by: string }>("SELECT uploaded_by FROM documents WHERE id = $1", [id])
  if (!doc) throw new HttpError(404, "Document not found")
  if (doc.uploaded_by !== user.id && !isPrivileged(user)) {
    throw new HttpError(403, "Not authorized to delete this document. Ownership or Admin/Manager role required.")
  }
  await query("DELETE FROM documents WHERE id = $1", [id])
  return NextResponse.json({ message: "Document deleted successfully" })
})
