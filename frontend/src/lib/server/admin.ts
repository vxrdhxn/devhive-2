import { query, queryOne } from "./db"

/** Workspace-wide stats for the overview dashboard. */
export async function getOverview() {
  const [counts, recent_documents, integrations, users] = await Promise.all([
    queryOne<{ documents: string; chunks: string; integrations: string }>(
      "SELECT (SELECT count(*) FROM documents) AS documents, (SELECT count(*) FROM chunks) AS chunks, (SELECT count(*) FROM integrations) AS integrations",
    ),
    query(
      `SELECT d.id, d.filename, d.status, d.created_at, u.email AS uploader_email
       FROM documents d LEFT JOIN users u ON u.id = d.uploaded_by
       ORDER BY d.created_at DESC LIMIT 10`,
    ),
    query(
      `SELECT i.id, i.platform_name, i.status, i.created_at, u.email AS user_email
       FROM integrations i LEFT JOIN users u ON u.id = i.user_id
       ORDER BY i.created_at DESC LIMIT 8`,
    ),
    query("SELECT id, email, role, created_at FROM users ORDER BY created_at ASC"),
  ])
  return {
    document_count: Number(counts?.documents ?? 0),
    chunk_count: Number(counts?.chunks ?? 0),
    integration_count: Number(counts?.integrations ?? 0),
    recent_documents,
    integrations,
    users,
  }
}
