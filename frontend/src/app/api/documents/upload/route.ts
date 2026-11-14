import { NextRequest, NextResponse } from "next/server"
import { HttpError, handle, requireUser } from "@/lib/auth"
import { SUPPORTED_EXTENSIONS } from "@/lib/server/extract"
import { ingest } from "@/lib/server/ingest"

// Extraction + embeddings run in-process; give the function room on Vercel.
export const maxDuration = 300

const MAX_BYTES = 4 * 1024 * 1024 // Vercel caps request bodies at 4.5 MB

export const POST = handle(async (req: NextRequest) => {
  const user = await requireUser()
  const form = await req.formData()
  const file = form.get("file")
  if (!(file instanceof File) || !file.name) throw new HttpError(400, "No file selected")

  const ext = file.name.split(".").pop()?.toLowerCase() ?? ""
  if (!SUPPORTED_EXTENSIONS.includes(ext)) {
    throw new HttpError(400, `Unsupported file format: .${ext}. Supported: ${SUPPORTED_EXTENSIONS.join(", ")}`)
  }
  if (file.size > MAX_BYTES) throw new HttpError(413, "File is too large (max 4 MB)")

  // Accept the privacy flag as a query param (current UI) or a form field.
  const privateFlag = req.nextUrl.searchParams.get("is_private") ?? String(form.get("is_private") ?? "false")
  const isPrivate = privateFlag === "true"

  // Processed before responding so the UI can report duplicates immediately.
  let result
  try {
    result = await ingest(
      { bytes: new Uint8Array(await file.arrayBuffer()) },
      { filename: file.name, fileType: file.type || "text/plain", userId: user.id, isPrivate },
    )
  } catch (err) {
    throw new HttpError(500, `Ingestion failed: ${(err as Error).message}`)
  }

  if (result.status === "duplicate") {
    return NextResponse.json({ status: "duplicate", message: result.message, filename: file.name, id: result.document_id })
  }
  return NextResponse.json({
    status: "success",
    message: "Document processed and inserted successfully",
    filename: file.name,
    id: result.document_id,
  })
})
