import { Pool, type QueryResultRow } from "pg"
import { attachDatabasePool } from "@vercel/functions"

// One pool per server instance. On Vercel (Fluid compute) attachDatabasePool
// lets idle connections close cleanly before the instance is suspended.
// Uses Neon's pooled DATABASE_URL at runtime.

const globalForDb = globalThis as unknown as { __devhivePool?: Pool }

/** Neon URLs use sslmode=require; pg treats that as verify-full but warns. Be explicit. */
export function strictSsl(url: string): string {
  return url.replace(/([?&]sslmode=)(prefer|require|verify-ca)\b/, "$1verify-full")
}

function createPool(): Pool {
  const connectionString = process.env.DATABASE_URL
  if (!connectionString) {
    throw new Error("DATABASE_URL is not set. Point it at your Neon Postgres database.")
  }
  const pool = new Pool({
    connectionString: strictSsl(connectionString),
    max: 5,
    idleTimeoutMillis: 5_000,
    connectionTimeoutMillis: 15_000, // Neon may need a moment to wake from scale-to-zero
  })
  attachDatabasePool(pool)
  return pool
}

export function getPool(): Pool {
  if (!globalForDb.__devhivePool) globalForDb.__devhivePool = createPool()
  return globalForDb.__devhivePool
}

export async function query<T extends QueryResultRow = any>(sql: string, params: unknown[] = []): Promise<T[]> {
  const res = await getPool().query<T>(sql, params)
  return res.rows
}

export async function queryOne<T extends QueryResultRow = any>(sql: string, params: unknown[] = []): Promise<T | null> {
  const rows = await query<T>(sql, params)
  return rows[0] ?? null
}

/** pgvector text literal; use with `$n::vector`. */
export function toVector(values: ArrayLike<number>): string {
  return `[${Array.from(values, (v) => Number(v).toPrecision(7)).join(",")}]`
}
