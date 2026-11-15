// AI answer generation over any OpenAI-compatible Chat Completions API.
// Provider is picked from env vars, first match wins:
//   1. LLM_BASE_URL + LLM_API_KEY (+ LLM_MODEL)   — anything OpenAI-compatible
//   2. GROQ_API_KEY (+ GROQ_MODEL)                 — Groq (free tier)
//   3. NEON_AI_GATEWAY_BASE_URL + NEON_AI_GATEWAY_TOKEN (+ LLM_MODEL) — Neon AI Gateway

type Provider = { name: string; baseUrl: string; apiKey: string; model: string }

function resolveProvider(): Provider | null {
  const e = process.env
  if (e.LLM_BASE_URL && e.LLM_API_KEY) {
    return { name: "custom", baseUrl: e.LLM_BASE_URL.replace(/\/+$/, ""), apiKey: e.LLM_API_KEY, model: e.LLM_MODEL || "gpt-4o-mini" }
  }
  if (e.GROQ_API_KEY) {
    return { name: "groq", baseUrl: "https://api.groq.com/openai/v1", apiKey: e.GROQ_API_KEY, model: e.GROQ_MODEL || "openai/gpt-oss-20b" }
  }
  if (e.NEON_AI_GATEWAY_BASE_URL && e.NEON_AI_GATEWAY_TOKEN) {
    return { name: "neon", baseUrl: `${e.NEON_AI_GATEWAY_BASE_URL.replace(/\/+$/, "")}/v1`, apiKey: e.NEON_AI_GATEWAY_TOKEN, model: e.LLM_MODEL || "claude-haiku-4-5" }
  }
  return null
}

export type ContextChunk = { filename: string; index: number; text: string }

export async function generateAnswer(question: string, chunks: ContextChunk[]) {
  const provider = resolveProvider()
  if (!provider) {
    return {
      answer: "AI answers are not configured. Set GROQ_API_KEY (or LLM_BASE_URL/LLM_API_KEY) in the environment.",
      sources: [] as string[],
      confidence: null,
    }
  }

  // ~25k chars (~7-9k tokens) keeps requests inside Groq's free-tier limits.
  const context = chunks
    .map((c) => `Source: ${c.filename} (Chunk ${c.index})\nContent: ${c.text}`)
    .join("\n\n")
    .slice(0, 25_000)

  const prompt = `You are a **Technical Knowledge Architect** for the Knowledge Transfer Platform (KTP).
Your goal is to provide **exhaustive, structured, and highly detailed** answers based ONLY on the provided context.

### TASK:
Analyze the context chunks below and answer the user's question with maximum depth.
- **CRITICAL**: Unless the user explicitly asks for a "Summary of all files" or a "Workspace overview", DO NOT include any file list, document breakdown, or metadata table at the beginning of your response.
- **START DIRECTLY** with the answer to the specific question. Focus 100% on answering the technical details.
- If the user asks a technical question, explain the "how" and "why" not just the "what."
- Use **Markdown tables** if you encounter data that is easier to compare side-by-side.
- NEVER make up information. If it's not in the context, say it's missing from the knowledge base.

### CONTEXT:
${context}

### QUESTION:
${question}

### DETAILED RESPONSE:`

  try {
    const res = await fetch(`${provider.baseUrl}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${provider.apiKey}` },
      body: JSON.stringify({
        model: provider.model,
        messages: [
          { role: "system", content: "You are a senior technical architect specializing in documentation synthesis and detailed technical reviews." },
          { role: "user", content: prompt },
        ],
        temperature: 0.3,
        // gpt-oss models reason before answering, and the reasoning counts against
        // max_tokens: keep it short and leave room for a full answer.
        max_tokens: 4096,
        ...(/gpt-oss/.test(provider.model) ? { reasoning_effort: "low" } : {}),
      }),
      signal: AbortSignal.timeout(60_000),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      const msg = data?.error?.message || data?.detail || res.statusText
      throw new Error(`${provider.name} returned ${res.status}: ${msg}`)
    }
    return {
      answer: String(data.choices?.[0]?.message?.content ?? ""),
      sources: [...new Set(chunks.map((c) => c.filename))],
      confidence: 0.85,
    }
  } catch (err) {
    return { answer: `Error generating answer: ${(err as Error).message}`, sources: [] as string[], confidence: null }
  }
}
