import { NextRequest, NextResponse } from "next/server"
import { HttpError, handle, requireUser } from "@/lib/auth"
import { query, queryOne } from "@/lib/server/db"
import { PUBLIC_COLUMNS, resolvePlatform } from "@/lib/server/integrations"

// Shared workspace: everyone can see the connected bridges (never their tokens).
export const GET = handle(async () => {
  await requireUser()
  return NextResponse.json(await query(`SELECT ${PUBLIC_COLUMNS} FROM integrations ORDER BY created_at DESC`))
})

export const POST = handle(async (req: NextRequest) => {
  const user = await requireUser()
  const body = await req.json().catch(() => ({}))
  const platformName = String(body.platform_name ?? "").trim()
  const apiToken = String(body.api_token ?? "").trim()
  const baseUrl = String(body.base_url ?? "").trim() || null
  if (!platformName || platformName.length > 200) throw new HttpError(400, "platform_name is required")
  if (!apiToken) throw new HttpError(400, "api_token is required")
  const platformType =
    ["notion", "github", "rest"].includes(body.platform_type) ? body.platform_type
    : resolvePlatform({ platform_name: platformName, base_url: baseUrl }) === "web" ? "rest"
    : resolvePlatform({ platform_name: platformName, base_url: baseUrl })

  const row = await queryOne(
    `INSERT INTO integrations (user_id, platform_name, base_url, api_token, platform_type, status)
     VALUES ($1, $2, $3, $4, $5, 'active') RETURNING ${PUBLIC_COLUMNS}`,
    [user.id, platformName, baseUrl, apiToken, platformType],
  )
  return NextResponse.json(row, { status: 201 })
})
