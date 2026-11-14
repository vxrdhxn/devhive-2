import "./base64-polyfill" // must load before unpdf/pdf.js — see that file
import JSZip from "jszip"

// Text extraction for uploaded files (port of the old Python document_processor).
// Office formats are zip archives of XML, so they are parsed with JSZip directly.

const decodeEntities = (s: string) =>
  s
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
    .replace(/&amp;/g, "&")

/** Collect the text of all <tag>…</tag> elements inside each block element. */
function xmlBlocks(xml: string, blockTag: string, textTag: string): string[] {
  const blocks: string[] = []
  const blockRe = new RegExp(`<${blockTag}[\\s>][\\s\\S]*?</${blockTag}>`, "g")
  const textRe = new RegExp(`<${textTag}(?:\\s[^>]*)?>([\\s\\S]*?)</${textTag}>`, "g")
  for (const block of xml.match(blockRe) ?? []) {
    let text = ""
    for (const m of block.matchAll(textRe)) text += m[1]
    if (text.trim()) blocks.push(decodeEntities(text))
  }
  return blocks
}

const naturalOrder = (a: string, b: string) => a.localeCompare(b, undefined, { numeric: true })

async function extractPdf(buf: Uint8Array): Promise<string> {
  const { extractText, getDocumentProxy } = await import("unpdf")
  const pdf = await getDocumentProxy(buf)
  const { text } = await extractText(pdf, { mergePages: true })
  return text
}

async function extractDocx(buf: Uint8Array): Promise<string> {
  const zip = await JSZip.loadAsync(buf)
  const xml = await zip.file("word/document.xml")?.async("string")
  if (!xml) throw new Error("Not a valid .docx file")
  return xmlBlocks(xml, "w:p", "w:t").join("\n")
}

async function extractPptx(buf: Uint8Array): Promise<string> {
  const zip = await JSZip.loadAsync(buf)
  const slides = Object.keys(zip.files).filter((f) => /^ppt\/slides\/slide\d+\.xml$/.test(f)).sort(naturalOrder)
  const parts: string[] = []
  for (const name of slides) {
    const xml = await zip.file(name)!.async("string")
    parts.push(...xmlBlocks(xml, "a:p", "a:t"))
  }
  return parts.join("\n")
}

async function extractXlsx(buf: Uint8Array): Promise<string> {
  const zip = await JSZip.loadAsync(buf)
  const shared: string[] = []
  const ssXml = await zip.file("xl/sharedStrings.xml")?.async("string")
  if (ssXml) {
    for (const si of ssXml.match(/<si>[\s\S]*?<\/si>/g) ?? []) {
      let t = ""
      for (const m of si.matchAll(/<t(?:\s[^>]*)?>([\s\S]*?)<\/t>/g)) t += m[1]
      shared.push(decodeEntities(t))
    }
  }
  // Sheet names, in workbook order
  const wbXml = (await zip.file("xl/workbook.xml")?.async("string")) ?? ""
  const sheetNames = [...wbXml.matchAll(/<sheet\b[^>]*\bname="([^"]*)"/g)].map((m) => decodeEntities(m[1]))
  const sheetFiles = Object.keys(zip.files).filter((f) => /^xl\/worksheets\/sheet\d+\.xml$/.test(f)).sort(naturalOrder)

  const parts: string[] = []
  for (const [i, name] of sheetFiles.entries()) {
    parts.push(`Sheet: ${sheetNames[i] ?? `Sheet${i + 1}`}`)
    const xml = await zip.file(name)!.async("string")
    for (const row of xml.match(/<row\b[\s\S]*?<\/row>/g) ?? []) {
      const cells: string[] = []
      for (const c of row.matchAll(/<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g)) {
        const attrs = c[1]
        const inner = c[2] ?? ""
        const type = /\bt="([^"]+)"/.exec(attrs)?.[1]
        let value = ""
        if (type === "s") value = shared[Number(/<v>([\s\S]*?)<\/v>/.exec(inner)?.[1])] ?? ""
        else if (type === "inlineStr") value = decodeEntities([...inner.matchAll(/<t(?:\s[^>]*)?>([\s\S]*?)<\/t>/g)].map((m) => m[1]).join(""))
        else value = decodeEntities(/<v>([\s\S]*?)<\/v>/.exec(inner)?.[1] ?? "")
        if (value !== "") cells.push(value)
      }
      if (cells.join(" ").trim()) parts.push(cells.join(" "))
    }
  }
  return parts.join("\n")
}

function extractRtf(text: string): string {
  return text
    .replace(/\\par[d]?/g, "\n")
    .replace(/\{\\\*[^{}]*\}/g, "")
    .replace(/\\'([0-9a-f]{2})/gi, (_, h) => String.fromCharCode(parseInt(h, 16)))
    .replace(/\\u(-?\d+)\??/g, (_, n) => String.fromCharCode(Number(n) < 0 ? Number(n) + 65536 : Number(n)))
    .replace(/\\[a-z]+-?\d* ?/gi, "")
    .replace(/[{}]/g, "")
    .replace(/\n{3,}/g, "\n\n")
}

function decodeText(buf: Uint8Array): string {
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(buf)
  } catch {
    return new TextDecoder("latin1").decode(buf)
  }
}

export const SUPPORTED_EXTENSIONS = ["pdf", "docx", "pptx", "xlsx", "rtf", "csv", "txt", "md"]

export async function extractText(buf: Uint8Array, filename: string): Promise<string> {
  const ext = filename.split(".").pop()?.toLowerCase() ?? ""
  let text: string
  switch (ext) {
    case "pdf": text = await extractPdf(buf); break
    case "docx": text = await extractDocx(buf); break
    case "pptx": text = await extractPptx(buf); break
    case "xlsx": text = await extractXlsx(buf); break
    case "rtf": text = extractRtf(decodeText(buf)); break
    case "csv": text = decodeText(buf).split(/\r?\n/).map((l) => l.split(",").join(" ")).join("\n"); break
    case "txt":
    case "md": text = decodeText(buf); break
    default: throw new Error(`Unsupported file format: ${ext}`)
  }
  return text.replace(/\u0000/g, "").trim()
}
