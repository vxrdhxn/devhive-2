import type { NextConfig } from "next";
import path from "node:path";

// Env vars: locally from frontend/.env.local (`npm run env:sync` copies them
// from the repo-root .env that `neon env pull` writes); on Vercel, from the
// project's Environment Variables settings.

const ORT_BIN = "node_modules/onnxruntime-node/bin/napi-v*";

const nextConfig: NextConfig = {
  // The repo root also has a package.json (Neon config); this app lives in frontend/.
  outputFileTracingRoot: path.resolve(__dirname),
  turbopack: { root: path.resolve(__dirname) },
  // Native/large packages: load from node_modules at runtime instead of bundling.
  serverExternalPackages: ["@huggingface/transformers", "onnxruntime-node", "sharp"],
  // transformers.js loads ONNX Runtime's native binding (and sharp) dynamically,
  // which the file tracer can't follow — include them for routes that embed.
  outputFileTracingIncludes: Object.fromEntries(
    ["/api/search", "/api/documents/upload", "/api/integrations/*/sync"].map((route) => [
      route,
      [
        "node_modules/onnxruntime-node/package.json",
        "node_modules/onnxruntime-node/dist/**",
        `${ORT_BIN}/linux/x64/**`,
        "node_modules/onnxruntime-common/**",
        "node_modules/@huggingface/transformers/node_modules/**",
        "node_modules/@img/**",
        "node_modules/sharp/**",
      ],
    ]),
  ),
  // Keep the serverless bundle small: Vercel runs linux-x64, so drop the other
  // platforms' ONNX Runtime binaries and the browser (WASM) runtime.
  outputFileTracingExcludes: {
    "*": [
      `${ORT_BIN}/darwin/**`,
      `${ORT_BIN}/win32/**`,
      `${ORT_BIN}/linux/arm64/**`,
      "node_modules/onnxruntime-web/dist/*.wasm",
      "node_modules/onnxruntime-web/dist/*.jsep.*",
      "node_modules/onnxruntime-web/dist/*.webgpu.*",
      "node_modules/onnxruntime-web/dist/*.webgl.*",
    ],
  },
};

export default nextConfig;
