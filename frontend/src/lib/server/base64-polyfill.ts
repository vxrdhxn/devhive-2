// Spec-compatible Uint8Array.fromBase64 / prototype.toBase64 (TC39 proposal).
//
// Why: pdf.js (via unpdf) installs its own polyfill for these when they're
// missing, but that version ignores the `alphabet` option. `jose` uses these
// APIs when present (with alphabet: "base64url"), so after the first PDF was
// parsed every JWT failed to verify. Installing a correct version first makes
// pdf.js skip its own. Import this before anything that loads unpdf or jose.

type Alphabet = "base64" | "base64url"

const B64 = /^[A-Za-z0-9+/\s]*={0,2}\s*$/
const B64URL = /^[A-Za-z0-9_\-\s]*={0,2}\s*$/

const U8 = Uint8Array as unknown as {
  fromBase64?: (s: string, o?: { alphabet?: Alphabet }) => Uint8Array
  prototype: { toBase64?: (o?: { alphabet?: Alphabet; omitPadding?: boolean }) => string }
}

if (typeof U8.fromBase64 !== "function") {
  Object.defineProperty(Uint8Array, "fromBase64", {
    configurable: true,
    writable: true,
    value(input: string, options: { alphabet?: Alphabet } = {}) {
      if (typeof input !== "string") throw new TypeError("fromBase64 expects a string")
      const alphabet = options.alphabet ?? "base64"
      if (!(alphabet === "base64url" ? B64URL : B64).test(input)) throw new SyntaxError("Invalid character")
      return new Uint8Array(Buffer.from(input, alphabet))
    },
  })
}

if (typeof U8.prototype.toBase64 !== "function") {
  Object.defineProperty(Uint8Array.prototype, "toBase64", {
    configurable: true,
    writable: true,
    value(this: Uint8Array, options: { alphabet?: Alphabet; omitPadding?: boolean } = {}) {
      const alphabet = options.alphabet ?? "base64"
      let out = Buffer.from(this.buffer, this.byteOffset, this.byteLength).toString("base64")
      if (alphabet === "base64url") out = out.replace(/\+/g, "-").replace(/\//g, "_")
      return options.omitPadding ? out.replace(/=+$/, "") : out
    },
  })
}

export {}
