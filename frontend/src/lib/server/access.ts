import type { SessionUser } from "@/lib/auth"

/** Admins and managers can see and manage everything in the shared workspace. */
export const isPrivileged = (user: SessionUser) => user.role === "admin" || user.role === "manager"

/**
 * SQL condition for documents the user may see (shared workspace):
 * public documents, their own uploads, and — for admins/managers — everything.
 * `alias` is the documents table alias; `$n` placeholders are appended to `params`.
 */
export function visibleDocsSql(user: SessionUser, alias: string, params: unknown[]): string {
  if (isPrivileged(user)) return "TRUE"
  params.push(user.id)
  return `(${alias}.is_private = false OR ${alias}.uploaded_by = $${params.length})`
}
