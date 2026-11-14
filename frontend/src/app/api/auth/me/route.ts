import { NextResponse } from "next/server"
import { handle, requireUser } from "@/lib/auth"

export const GET = handle(async () => NextResponse.json(await requireUser()))
