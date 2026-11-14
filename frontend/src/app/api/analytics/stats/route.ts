import { NextResponse } from "next/server"
import { handle, requireUser } from "@/lib/auth"
import { queryOne } from "@/lib/server/db"

// High-level summary metrics for the analytics dashboard (admin/manager).
export const GET = handle(async () => {
  await requireUser("admin", "manager")
  const row = await queryOne<{ total: string; avg_conf: number | null; users: string }>(
    `SELECT count(*) AS total, avg(confidence) AS avg_conf, count(DISTINCT user_id) AS users FROM query_logs`,
  )
  return NextResponse.json({
    total_queries: Number(row?.total ?? 0),
    avg_confidence: Math.round(Number(row?.avg_conf ?? 0) * 100) / 100,
    active_users: Number(row?.users ?? 0),
    timestamp: new Date().toISOString(),
  })
})
