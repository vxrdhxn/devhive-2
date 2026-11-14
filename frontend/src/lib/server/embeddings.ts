import type { FeatureExtractionPipeline } from "@huggingface/transformers"

// Local embeddings with BAAI/bge-small-en-v1.5 (384 dims) via ONNX Runtime —
// same model the old Python backend used, but no PyTorch and no API key.
// The quantized model (~34 MB) is downloaded from Hugging Face on first use
// and cached in /tmp for the life of the server instance.

const MODEL_ID = process.env.EMBEDDING_MODEL || "Xenova/bge-small-en-v1.5"
const BATCH_SIZE = 16

let extractorPromise: Promise<FeatureExtractionPipeline> | null = null

async function getExtractor(): Promise<FeatureExtractionPipeline> {
  if (!extractorPromise) {
    extractorPromise = (async () => {
      const { pipeline, env } = await import("@huggingface/transformers")
      // Serverless file systems are read-only except /tmp.
      if (process.env.VERCEL || process.env.NODE_ENV === "production") {
        env.cacheDir = "/tmp/hf-cache"
      }
      env.allowLocalModels = false
      return pipeline("feature-extraction", MODEL_ID, { dtype: "q8" }) as Promise<FeatureExtractionPipeline>
    })().catch((err) => {
      extractorPromise = null // allow a retry on the next request
      throw err
    })
  }
  return extractorPromise
}

export async function embedMany(texts: string[]): Promise<number[][]> {
  const extractor = await getExtractor()
  const out: number[][] = []
  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const batch = texts.slice(i, i + BATCH_SIZE)
    const tensor = await extractor(batch, { pooling: "cls", normalize: true })
    const [rows, dims] = tensor.dims as [number, number]
    const data = tensor.data as Float32Array
    for (let r = 0; r < rows; r++) out.push(Array.from(data.subarray(r * dims, (r + 1) * dims)))
  }
  return out
}

export async function embedOne(text: string): Promise<number[]> {
  return (await embedMany([text]))[0]
}
