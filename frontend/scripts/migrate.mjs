// Applies db/schema.sql to the database (idempotent).
// Uses the direct (unpooled) Neon URL for DDL, per Neon guidance.
// Runs automatically before `next build`; run manually with `npm run db:migrate`.
import { readFileSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import nextEnv from "@next/env"
import pg from "pg"

const here = dirname(fileURLToPath(import.meta.url))
const appDir = resolve(here, "..")
// Load frontend/.env* (see `npm run env:sync`), falling back to the repo-root .env.
// (Already-set variables are never overwritten, so the first load wins.)
nextEnv.loadEnvConfig(appDir)
nextEnv.loadEnvConfig(resolve(appDir, ".."))

const url = process.env.DATABASE_URL_UNPOOLED || process.env.DATABASE_URL
if (!url) {
  console.warn("[migrate] DATABASE_URL is not set; skipping schema migration.")
  process.exit(0)
}

// Neon URLs use sslmode=require; pg treats that as verify-full but warns. Be explicit.
const client = new pg.Client({ connectionString: url.replace(/([?&]sslmode=)(prefer|require|verify-ca)\b/, "$1verify-full") })
try {
  await client.connect()
  await client.query(readFileSync(join(appDir, "db", "schema.sql"), "utf8"))
  console.log("[migrate] Database schema is up to date.")
} catch (err) {
  console.error("[migrate] Failed:", err.message)
  process.exit(1)
} finally {
  await client.end().catch(() => {})
}
