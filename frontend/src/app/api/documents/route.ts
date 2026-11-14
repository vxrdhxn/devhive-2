import { NextRequest, NextResponse } from "next/server"
import { handle, requireUser } from "@/lib/auth"
import { query } from "@/lib/server/db"
import { visibleDocsSql } from "@/lib/server/access"

// Shared workspace: admins/managers see every document; everyone else sees
// public documents plus their own uploads. Newest first.
export const GET = handle(async (req: NextRequest) => {
  const user = await requireUser()
  const limit = Math.min(Math.max(Number(req.nextUrl.searchParams.get("limit")) || 200, 1), 500)
  const params: unknown[] = []
  const visible = visibleDocsSql(user, "d", params)
  params.push(limit)
  const docs = await query(
    `SELECT d.id, d.filename, d.file_type, d.uploaded_by, d.status, d.is_private, d.metadata, d.created_at
     FROM documents d WHERE ${visible} ORDER BY d.created_at DESC LIMIT $${params.length}`,
    params,
  )
  return NextResponse.json(docs)
})
