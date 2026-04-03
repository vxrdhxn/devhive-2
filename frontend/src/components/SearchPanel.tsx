"use client"

import { useState } from "react"
import { Search, Loader2, FileText, Bot, Sparkles, ChevronRight, Activity, LayoutGrid } from "lucide-react"
import { createClient } from "@/utils/supabase/client"
import { motion, AnimatePresence } from "framer-motion"
import { DocumentViewer } from "./DocumentViewer"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

type SearchResultChunk = {
  id: string
  text: string
  document_id: string
  similarity: number
}

type SearchResponse = {
  query: string
  ai_answer: string | null
  sources: string[]
  chunks: SearchResultChunk[]
}

export function SearchPanel() {
  const [query, setQuery] = useState("")
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  // Split-pane state
  const [activeDocId, setActiveDocId] = useState<string | null>(null)
  const [activeChunkId, setActiveChunkId] = useState<string | undefined>(undefined)

  const supabase = createClient()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setSearching(true)
    setError(null)
    setResults(null)
    setActiveDocId(null) // Reset split view on new search

    try {
      const { data: { session } } = await supabase.auth.getSession()

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api"
      const res = await fetch(`${backendUrl}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.access_token}`
        },
        body: JSON.stringify({
          query,
          top_k: 5,
          min_similarity: 0.3,
          use_ai: true
        })
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Unknown server error" }));
        throw new Error(errorData.detail || "Search request failed");
      }
      
      const data: SearchResponse = await res.json();
      setResults(data);
    } catch (err: any) {
      console.error("Search error details:", err);
      if (err.name === "TypeError" && err.message === "Failed to fetch") {
        setError("Backend Offline: Check Server or Network Connection.");
      } else {
        setError(err.message || "An error occurred while communicating with the AI search engine.");
      }
    } finally {
      setSearching(false);
    }
  }

  const openDocumentViewer = (documentId: string, chunkId?: string) => {
    setActiveDocId(documentId)
    setActiveChunkId(chunkId)
  }

  return (
    <div className="flex h-full w-full bg-background overflow-hidden relative">
      {/* Main Search Panel */}
      <div 
        className={`flex flex-col h-full transition-all duration-500 ease-[cubic-bezier(0.25,1,0.5,1)] ${
          activeDocId ? 'w-1/2 border-r border-border p-8 bg-background' : 'w-full p-10'
        }`}
      >
        <div className="flex items-center justify-between mb-8 shrink-0">
          <h2 className="text-3xl font-bold flex items-center gap-3 tracking-tighter">
            <Bot className="h-7 w-7" />
            Semantic Search
          </h2>
          <div className="flex items-center gap-2 text-xs font-medium text-muted uppercase tracking-widest">
            <Activity className="h-3 w-3" />
            Core Ingestion Online
          </div>
        </div>
        
        <form onSubmit={handleSearch} className="flex gap-3 relative z-10 shrink-0">
          <div className="relative flex-1 group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted group-focus-within:text-foreground transition-colors" />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about your knowledge base..." 
              className="w-full rounded-xl border border-border bg-card px-11 py-4 focus:ring-2 focus:ring-foreground/5 focus:border-foreground focus:outline-none transition-all text-foreground placeholder:text-muted/60"
              disabled={searching}
            />
          </div>
          <motion.button 
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            type="submit"
            disabled={searching || !query.trim()}
            className="px-8 bg-foreground text-background py-4 rounded-xl font-bold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center min-w-[120px]"
          >
            {searching ? <Loader2 className="h-5 w-5 animate-spin" /> : "Search"}
          </motion.button>
        </form>

        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="mt-6 shrink-0 p-4 text-red-600 bg-red-50 dark:bg-red-950/20 rounded-xl text-sm border border-red-200 dark:border-red-900/50"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Search Results Area */}
        <div className="mt-10 flex-1 overflow-y-auto pr-2 pb-10">
          <AnimatePresence mode="wait">
            {!results && !searching && !error && (
              <motion.div 
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="text-center py-24 border border-border border-dashed rounded-3xl h-full flex flex-col items-center justify-center bg-muted/5 group hover:bg-muted/10 transition-colors"
              >
                <div className="h-20 w-20 rounded-full border border-border flex items-center justify-center mb-6 group-hover:scale-110 transition-transform bg-background">
                  <Sparkles className="h-10 w-10 text-muted" />
                </div>
                <p className="text-xl font-bold">Intelligent Synthesis</p>
                <p className="text-sm mt-3 text-muted max-w-sm leading-relaxed px-6">
                  Query your enterprise context using natural language. Our AI will traverse your documents and generate a verified answer.
                </p>
              </motion.div>
            )}

            {searching && (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center py-32"
              >
                <div className="relative">
                   <div className="absolute inset-0 blur-xl bg-foreground/10 rounded-full animate-pulse" />
                   <Bot className="h-12 w-12 relative animate-bounce" />
                </div>
                <p className="text-sm font-bold mt-6 tracking-widest uppercase opacity-60">Architecting Response...</p>
              </motion.div>
            )}

            {results && (
              <motion.div 
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ staggerChildren: 0.1, duration: 0.4 }}
                className="space-y-12"
              >
                
                {/* AI Synthesized Answer */}
                {results.ai_answer && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-card border border-border rounded-2xl p-8 shadow-sm relative overflow-hidden group"
                  >
                    <div className="absolute top-0 right-0 p-4">
                       <Sparkles className="h-5 w-5 text-muted opacity-20 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <div className="flex items-center gap-3 mb-6">
                       <div className="h-8 w-8 bg-foreground text-background rounded-lg flex items-center justify-center font-bold text-xs">AI</div>
                       <h3 className="font-bold uppercase tracking-widest text-[10px] text-muted">Generated Synthesis</h3>
                    </div>
                    <div className={`text-foreground leading-relaxed prose prose-neutral dark:prose-invert max-w-none ${activeDocId ? 'text-sm' : 'text-base font-medium'}`}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {results.ai_answer}
                      </ReactMarkdown>
                    </div>
                    {results.sources.length > 0 && (
                      <div className="mt-8 pt-6 border-t border-border flex flex-col gap-4">
                        <span className="font-bold uppercase tracking-widest text-[9px] text-muted">Verified Sources</span>
                        <div className="flex flex-wrap gap-2">
                          {results.sources.map((src, i) => (
                            <button 
                              key={i} 
                              onClick={() => {
                                const matchingChunk = results.chunks.find(c => src.includes(c.document_id.split("-")[0]))
                                if (matchingChunk) openDocumentViewer(matchingChunk.document_id, matchingChunk.id)
                              }}
                              className="bg-background border border-border px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider hover:bg-foreground hover:text-background transition-all flex items-center gap-2"
                            >
                              <FileText className="h-3 w-3" />
                              {src}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Semantic Chunks */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-bold uppercase tracking-widest text-[10px] text-muted flex items-center gap-2">
                      <LayoutGrid className="h-4 w-4" />
                      Semantic Context Blocks
                    </h3>
                  </div>
                  
                  {results.chunks.length === 0 ? (
                    <div className="p-8 border-2 border-dashed border-border rounded-2xl text-center text-muted italic text-sm">
                       No semantic proximity matches found.
                    </div>
                  ) : (
                    <div className="grid gap-4">
                      {results.chunks.map((chunk, i) => (
                        <motion.button 
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.4 + (i * 0.1) }}
                          key={chunk.id || i} 
                          onClick={() => openDocumentViewer(chunk.document_id, chunk.id)}
                          className={`w-full text-left group border border-border rounded-xl p-6 transition-all duration-300 shadow-sm ${activeChunkId === chunk.id ? 'bg-foreground text-background border-foreground' : 'bg-card hover:bg-muted/5'}`}
                        >
                          <div className="flex justify-between items-center gap-2 mb-4">
                            <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded border ${activeChunkId === chunk.id ? 'border-background/20 bg-background/10' : 'border-border bg-muted/5'}`}>
                              {chunk.document_id.split("-")[0]}
                            </span>
                            <span className={`text-[9px] font-black uppercase tracking-tighter ${activeChunkId === chunk.id ? 'text-background' : 'text-emerald-500'}`}>
                              Match Index: {(chunk.similarity * 100).toFixed(1)}%
                            </span>
                          </div>
                          <p className={`text-sm leading-relaxed transition-all duration-300 ${activeChunkId === chunk.id ? 'text-background' : 'text-foreground/80'} ${activeDocId ? 'line-clamp-2' : 'line-clamp-4'}`}>
                            &ldquo;{chunk.text}&rdquo;
                          </p>
                          <div className={`mt-4 flex items-center gap-1 text-[9px] font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity ${activeChunkId === chunk.id ? 'text-background' : 'text-foreground'}`}>
                             Inspect Source <ChevronRight className="h-3 w-3" />
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  )}
                </motion.div>
                
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Split Pane: Document Viewer */}
      <AnimatePresence>
        {activeDocId && (
          <motion.div 
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: "50%", opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.25, 1, 0.5, 1] }}
            className="h-full border-l border-border bg-background z-20 shrink-0"
          >
            <DocumentViewer 
              documentId={activeDocId} 
              activeChunkId={activeChunkId} 
              onClose={() => { setActiveDocId(null); setActiveChunkId(undefined); }} 
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
