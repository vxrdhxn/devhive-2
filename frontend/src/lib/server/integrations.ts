import { ingest } from "./ingest"

// Integration adapters (ports of the Python Notion, GitHub and generic web/REST adapters).

// Columns safe to return to the browser (never the stored API token).
export const PUBLIC_COLUMNS = "id, user_id, platform_name, base_url, platform_type, status, last_synced_at, created_at"

type SyncResult = Record<string, unknown>
type Integration = { platform_type?: string | null; platform_name?: string | null; base_url?: string | null }

/** Pick the adapter: explicit type first, then infer from name/URL (legacy 'rest' bridges). */
export function resolvePlatform(i: Integration): "notion" | "github" | "web" {
  const type = (i.platform_type || "").toLowerCase()
  if (type === "notion" || type === "github") return type
  const name = (i.platform_name || "").toLowerCase()
  const url = (i.base_url || "").toLowerCase()
  if (name.includes("github") || url.includes("github.com")) return "github"
  if (name.includes("notion") || url.includes("notion.so")) return "notion"
  return "web"
}

async function syncNotion(apiToken: string, userId: string): Promise<SyncResult> {
  const headers = {
    Authorization: `Bearer ${apiToken}`,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
  }
  const res = await fetch("https://api.notion.com/v1/search", {
    method: "POST",
    headers,
    body: JSON.stringify({ filter: { property: "object", value: "page" } }),
  })
  if (!res.ok) throw new Error(`Failed to connect to Notion: ${res.status} ${res.statusText}`)
  const pages: any[] = (await res.json()).results ?? []

  let indexed = 0
  for (const page of pages) {
    let title = "Untitled Page"
    for (const prop of Object.values<any>(page.properties ?? {})) {
      if (prop?.type === "title" && prop.title?.length) {
        title = prop.title.map((t: any) => t.plain_text ?? "").join("")
      }
    }
    const blocksRes = await fetch(`https://api.notion.com/v1/blocks/${page.id}/children`, { headers })
    if (!blocksRes.ok) continue
    const blocks: any[] = (await blocksRes.json()).results ?? []
    const text = blocks
      .filter((b) => ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"].includes(b.type))
      .map((b) => (b[b.type]?.rich_text ?? []).map((t: any) => t.plain_text ?? "").join(""))
      .filter(Boolean)
      .join("\n")
    if (text.trim()) {
      await ingest({ text }, {
        filename: `Notion: ${title}`, fileType: "notion", userId,
        metadata: { notion_page_id: page.id, url: page.url },
      })
      indexed++
    }
  }
  return { status: "success", pages_found: pages.length, pages_indexed: indexed, timestamp: new Date().toISOString() }
}

async function syncGitHub(apiToken: string, userId: string, baseUrl?: string | null): Promise<SyncResult> {
  if (!baseUrl) throw new Error("GitHub requires a repository URL in the Endpoint URI field")
  const parts = baseUrl.replace(/\.git$/, "").replace(/\/+$/, "").split("/")
  if (parts.length < 2) throw new Error(`Invalid GitHub URL format: ${baseUrl}`)
  const repo = `${parts[parts.length - 2]}/${parts[parts.length - 1]}`
  const api = `https://api.github.com/repos/${repo}`
  const headers: Record<string, string> = { Accept: "application/vnd.github.v3+json", "User-Agent": "Dev-Hive-KTP" }
  if (apiToken) headers.Authorization = `token ${apiToken}`

  const repoRes = await fetch(api, { headers })
  if (!repoRes.ok) throw new Error(`GitHub repository not accessible (${repoRes.status} ${repoRes.statusText})`)
  const branch: string = (await repoRes.json()).default_branch || "main"

  const treeRes = await fetch(`${api}/git/trees/${encodeURIComponent(branch)}?recursive=1`, { headers })
  if (!treeRes.ok) throw new Error(`Could not read repository tree (${treeRes.status})`)
  const MAX_FILES = 50 // keep each sync within the function time limit
  const queue: any[] = ((await treeRes.json()).tree ?? [])
    .filter((it: any) => it.type === "blob" && /\.(md|txt)$/i.test(it.path ?? ""))
    .slice(0, MAX_FILES)

  let indexed = 0
  const CONCURRENCY = 5
  for (let i = 0; i < queue.length; i += CONCURRENCY) {
    const results = await Promise.all(
      queue.slice(i, i + CONCURRENCY).map(async (item) => {
        try {
          const blobRes = await fetch(item.url, { headers })
          if (!blobRes.ok) return false
          const blob = await blobRes.json()
          const text = blob.encoding === "base64"
            ? Buffer.from(String(blob.content).replace(/\n/g, ""), "base64").toString("utf8")
            : String(blob.content ?? "")
          if (!text.trim()) return false
          await ingest({ text }, {
            filename: `GitHub: ${repo}/${item.path}`, fileType: "github", userId,
            metadata: { github_repo: repo, path: item.path, branch },
          })
          return true
        } catch (err) {
          console.warn(`Failed to index ${item.path}: ${(err as Error).message}`)
          return false
        }
      }),
    )
    indexed += results.filter(Boolean).length
  }
  return {
    status: "success", repo, branch, pages_indexed: indexed,
    message: `Indexed ${indexed} files from ${branch}.`, timestamp: new Date().toISOString(),
  }
}

async function syncWeb(apiToken: string, userId: string, baseUrl?: string | null): Promise<SyncResult> {
  if (!baseUrl) {
    return {
      status: "partial",
      message: "Platform adapter is in simplified mode. Basic connectivity verified.",
      pages_found: 0,
      items_indexed: 0,
    }
  }
  let url: URL
  try {
    url = new URL(baseUrl)
  } catch {
    throw new Error(`Invalid URL: ${baseUrl}`)
  }
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("Only http(s) URLs can be synced")
  // Don't let the server be pointed at internal/private addresses.
  const host = url.hostname.replace(/^\[|\]$/g, "").toLowerCase()
  if (
    host === "localhost" || host.endsWith(".localhost") || host.endsWith(".internal") || host === "::1" ||
    /^(127\.|10\.|0\.|169\.254\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)/.test(host) || /^f[cd]|^fe80/.test(host)
  ) {
    throw new Error("Private or internal addresses cannot be synced")
  }

  const res = await fetch(url, { headers: apiToken ? { Authorization: `Bearer ${apiToken}` } : {} })
  if (!res.ok) throw new Error(`Failed to fetch content from ${baseUrl}: ${res.status} ${res.statusText}`)
  const type = res.headers.get("content-type") ?? ""
  let text = type.includes("application/json") ? JSON.stringify(await res.json(), null, 1) : await res.text()
  if (type.includes("text/html")) {
    text = text
      .replace(/<(script|style)[\s\S]*?<\/\1>/gi, " ")
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s*\n+/g, "\n\n")
  }
  await ingest({ text }, { filename: `Web: ${baseUrl}`, fileType: "web", userId, metadata: { source_url: baseUrl } })
  return {
    status: "success", pages_found: 1, pages_indexed: 1,
    message: `Source ${baseUrl} fetched and indexed successfully.`, timestamp: new Date().toISOString(),
  }
}

export async function syncIntegration(
  integration: Integration & { api_token?: string | null },
  ownerId: string,
): Promise<SyncResult> {
  const token = integration.api_token || ""
  switch (resolvePlatform(integration)) {
    case "notion": return syncNotion(token, ownerId)
    case "github": return syncGitHub(token, ownerId, integration.base_url)
    default: return syncWeb(token, ownerId, integration.base_url)
  }
}
