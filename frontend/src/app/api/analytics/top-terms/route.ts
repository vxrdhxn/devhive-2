import { NextResponse } from "next/server"
import { handle, requireUser } from "@/lib/auth"
import { query } from "@/lib/server/db"

// The 10 most frequent search queries (longer than 3 characters).
export const GET = handle(async () => {
  await requireUser("admin", "manager")
  const rows = await query<{ term: string; count: string }>(
    `SELECT lower(trim(query)) AS term, count(*) AS count FROM query_logs
     WHERE length(trim(query)) > 3
     GROUP BY 1 ORDER BY count(*) DESC, 1 LIMIT 10`,
  )
  return NextResponse.json(rows.map((r) => ({ term: r.term, count: Number(r.count) })))
})
