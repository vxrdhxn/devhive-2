import { query, queryOne, toVector } from "./db"
import { embedMany } from "./embeddings"
import { extractText } from "./extract"

/** Split text into overlapping chunks, breaking on spaces (port of the Python chunker). */
export function chunkText(text: string, chunkSize = 800, overlap = 150): string[] {
  if (!text.trim()) return []
  const chunks: string[] = []
  let start = 0
  while (start < text.length) {
    let end = Math.min(start + chunkSize, text.length)
    if (end < text.length) {
      const boundary = text.lastIndexOf(" ", end)
      if (boundary > start) end = boundary
    }
    const chunk = text.slice(start, end).trim()
    if (chunk) chunks.push(chunk)
    if (end >= text.length) break
    const next = end - overlap
    start = next <= start ? end : next
  }
  return chunks
}

export type IngestOptions = {
  filename: string
  fileType: string
  userId: string
  isPrivate?: boolean
  metadata?: Record<string, unknown>
}

export type IngestResult =
  | { status: "success"; document_id: string; chunks_processed: number }
  | { status: "duplicate"; document_id: string; matched_document_id: string; message: string }

const setStatus = (docId: string, status: string) =>
  query("UPDATE documents SET status = $1 WHERE id = $2", [status, docId])

/**
 * Store a document: dedupe by filename → extract (if bytes) → chunk → embed →
 * dedupe by content → store chunks. Status is updated at each step so the UI
 * can show progress. Runs synchronously so the caller gets the final result.
 */
export async function ingest(
  source: { bytes: Uint8Array } | { text: string },
  opts: IngestOptions,
): Promise<IngestResult> {
  const { filename, fileType, userId, isPrivate = false, metadata = {} } = opts

  // 1. Same filename already ingested by this user → record as duplicate.
  const existing = await queryOne<{ id: string }>(
    "SELECT id FROM documents WHERE filename = $1 AND uploaded_by = $2 AND status = 'completed' LIMIT 1",
    [filename, userId],
  )
  if (existing) {
    const dup = await queryOne<{ id: string }>(
      `INSERT INTO documents (filename, file_type, uploaded_by, status, is_private, metadata)
       VALUES ($1, $2, $3, 'duplicate', $4, $5) RETURNING id`,
      [filename, fileType, userId, isPrivate, JSON.stringify({ ...metadata, duplicate_of: existing.id, match_type: "filename" })],
    )
    return {
      status: "duplicate",
      document_id: dup!.id,
      matched_document_id: existing.id,
      message: `A file with name '${filename}' already exists.`,
    }
  }

  const doc = await queryOne<{ id: string }>(
    `INSERT INTO documents (filename, file_type, uploaded_by, status, is_private, metadata)
     VALUES ($1, $2, $3, 'processing', $4, $5) RETURNING id`,
    [filename, fileType, userId, isPrivate, JSON.stringify(metadata)],
  )
  const docId = doc!.id

  try {
    // 2. Extract text
    let fullText: string
    if ("bytes" in source) {
      await setStatus(docId, "extracting text")
      fullText = await extractText(source.bytes, filename)
    } else {
      fullText = source.text.replace(/\u0000/g, "")
    }

    // 3. Chunk
    await setStatus(docId, "chunking content")
    const chunks = chunkText(fullText)
    if (!chunks.length) throw new Error("No text could be extracted or chunked from document.")

    // 4. Embed
    await setStatus(docId, `generating ${chunks.length} embeddings`)
    const vectors = await embedMany(chunks)

    // 5. Near-identical content already in the workspace → duplicate.
    const match = await queryOne<{ document_id: string }>(
      `SELECT c.document_id FROM chunks c JOIN documents d ON d.id = c.document_id
       WHERE d.id <> $2 AND (d.is_private = false OR d.uploaded_by = $3)
         AND 1 - (c.embedding <=> $1::vector) >= 0.95
       ORDER BY c.embedding <=> $1::vector LIMIT 1`,
      [toVector(vectors[0]), docId, userId],
    )
    if (match) {
      await query("UPDATE documents SET status = 'duplicate', metadata = $1 WHERE id = $2", [
        JSON.stringify({ ...metadata, duplicate_of: match.document_id, match_type: "content" }),
        docId,
      ])
      return {
        status: "duplicate",
        document_id: docId,
        matched_document_id: match.document_id,
        message: `Content already exists in the knowledge base (matched ID: ${match.document_id})`,
      }
    }

    // 6. Store chunks
    await setStatus(docId, "storing in vector db")
    const BATCH = 100
    for (let i = 0; i < chunks.length; i += BATCH) {
      const values: unknown[] = []
      const rows: string[] = []
      chunks.slice(i, i + BATCH).forEach((content, j) => {
        const n = values.length
        rows.push(`($${n + 1}, $${n + 2}, $${n + 3}::vector, $${n + 4})`)
        values.push(docId, content, toVector(vectors[i + j]), JSON.stringify({ index: i + j }))
      })
      await query(`INSERT INTO chunks (document_id, content, embedding, metadata) VALUES ${rows.join(",")}`, values)
    }

    await setStatus(docId, "completed")
    return { status: "success", document_id: docId, chunks_processed: chunks.length }
  } catch (err) {
    await query(
      "UPDATE documents SET status = 'error', metadata = metadata || $1::jsonb WHERE id = $2",
      [JSON.stringify({ error_message: (err as Error).message }), docId],
    ).catch(() => {})
    throw err
  }
}
