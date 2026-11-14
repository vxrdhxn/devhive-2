// Copies the app's variables from the repo-root .env (written by `neon env pull`
// / `neon deploy`) into frontend/.env.local, which Next.js reads. Existing keys
// in .env.local are updated in place; other lines are kept. Values are not printed.
//   npm run env:sync
import { existsSync, readFileSync, writeFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const appDir = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const rootEnv = resolve(appDir, "..", ".env")
const localEnv = resolve(appDir, ".env.local")
const KEYS = [
  "DATABASE_URL", "DATABASE_URL_UNPOOLED", "JWT_SECRET",
  "GROQ_API_KEY", "GROQ_MODEL", "LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL",
  "NEON_AI_GATEWAY_BASE_URL", "NEON_AI_GATEWAY_TOKEN",
]

const parse = (text) =>
  Object.fromEntries(
    text.split(/\r?\n/).map((l) => /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$/.exec(l)).filter(Boolean).map((m) => [m[1], m[2]]),
  )

if (!existsSync(rootEnv)) {
  console.error(`No ${rootEnv} found. Run \`neon env pull\` in the repo root first.`)
  process.exit(1)
}
const source = parse(readFileSync(rootEnv, "utf8"))
const lines = existsSync(localEnv) ? readFileSync(localEnv, "utf8").split(/\r?\n/) : []
const synced = []
for (const key of KEYS) {
  if (source[key] === undefined) continue
  const idx = lines.findIndex((l) => new RegExp(`^\\s*${key}\\s*=`).test(l))
  const line = `${key}=${source[key]}`
  if (idx >= 0) lines[idx] = line
  else lines.push(line)
  synced.push(key)
}
writeFileSync(localEnv, lines.join("\n").replace(/\n*$/, "\n"))
console.log(`Synced to frontend/.env.local: ${synced.join(", ")}`)
