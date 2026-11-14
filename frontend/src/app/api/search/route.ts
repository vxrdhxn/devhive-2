import { NextRequest, NextResponse } from "next/server"
import { HttpError, handle, requireUser } from "@/lib/auth"
import { query, toVector } from "@/lib/server/db"
import { visibleDocsSql } from "@/lib/server/access"
import { embedOne } from "@/lib/server/embeddings"
import { generateAnswer } from "@/lib/server/llm"

export const maxDuration = 60

type Match = { id: string; document_id: string; content: string; filename: string; similarity: number }

const GLOBAL_HINTS = ["summarize all", "all files", "everything", "all documents", "total overview"]

export const POST = handle(async (req: NextRequest) => {
  const user = await requireUser()
  const body = await req.json().catch(() => ({}))
  const q = String(body.query ?? "").trim()
  if (!q) throw new HttpError(400, "Query cannot be empty")
  // Workspace-wide questions pull more context (capped for Groq free-tier limits).
  const isGlobal = GLOBAL_HINTS.some((w) => q.toLowerCase().includes(w))
  const topK = isGlobal ? 20 : Math.min(Math.max(Number(body.top_k) || 5, 1), 50)
  const minSimilarity = Number.isFinite(Number(body.min_similarity)) ? Number(body.min_similarity) : 0.3
  const useAi = body.use_ai !== false

  // 1. Semantic search (pgvector cosine) over documents the user may see
  const params: unknown[] = [toVector(await embedOne(q)), minSimilarity, topK]
  const visible = visibleDocsSql(user, "d", params)
  const rows = await query<Match>(
    `SELECT c.id, c.document_id, c.content, d.filename,
            1 - (c.embedding <=> $1::vector) AS similarity
     FROM chunks c JOIN documents d ON d.id = c.document_id
     WHERE ${visible} AND 1 - (c.embedding <=> $1::vector) > $2
     ORDER BY c.embedding <=> $1::vector
     LIMIT $3`,
    params,
  )
  const chunks = rows.map((r) => ({
    id: r.id,
    text: r.content,
    document_id: r.document_id,
    filename: r.filename,
    similarity: Number(r.similarity),
  }))

  // 2. Optional AI answer
  let ai_answer: string | null = null
  let sources: string[] = []
  let confidence: number | null = null
  if (useAi) {
    if (!chunks.length) {
      ai_answer = "I could not find any relevant information in your uploaded documents."
    } else {
      const result = await generateAnswer(q, chunks.map((c, i) => ({ filename: c.filename, index: i, text: c.text })))
      ai_answer = result.answer
      sources = result.sources
      confidence = result.confidence
    }
  }

  // 3. Log the query (best effort) — feeds the analytics dashboard
  await query(
    "INSERT INTO query_logs (user_id, query, response, confidence) VALUES ($1, $2, $3, $4)",
    [user.id, q, ai_answer, confidence],
  ).catch((e) => console.error("Failed to log query:", e.message))

  return NextResponse.json({ query: q, ai_answer, sources, chunks, confidence })
})
