import { NextResponse } from "next/server"
import { handle, requireUser } from "@/lib/auth"
import { getOverview } from "@/lib/server/admin"

export const GET = handle(async () => {
  await requireUser("admin", "manager")
  return NextResponse.json(await getOverview())
})
