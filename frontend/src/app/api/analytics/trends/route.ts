import { NextResponse } from "next/server"
import { handle, requireUser } from "@/lib/auth"
import { query } from "@/lib/server/db"

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

// Daily query counts over the last 30 days. Always includes the last 7 days
// (zeros if quiet), plus any earlier day that had queries. Dates are UTC.
export const GET = handle(async () => {
  await requireUser("admin", "manager")
  const rows = await query<{ day: string; n: string }>(
    `SELECT to_char(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD') AS day, count(*) AS n
     FROM query_logs WHERE created_at >= (now() AT TIME ZONE 'UTC')::date - 29
     GROUP BY 1`,
  )
  const counts = new Map(rows.map((r) => [r.day, Number(r.n)]))

  const today = new Date()
  const data: { date: string; queries: number }[] = []
  for (let i = 29; i >= 0; i--) {
    const d = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate() - i))
    const key = d.toISOString().slice(0, 10)
    if (counts.has(key) || i < 7) {
      data.push({ date: `${MONTHS[d.getUTCMonth()]} ${String(d.getUTCDate()).padStart(2, "0")}`, queries: counts.get(key) ?? 0 })
    }
  }
  return NextResponse.json(data)
})
