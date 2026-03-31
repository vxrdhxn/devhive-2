"use client"

import { useEffect, useState, useRef } from "react"
import { motion } from "framer-motion"
import { X, FileText, Loader2, Sparkles } from "lucide-react"
import { createClient } from "@/utils/supabase/client"

type DocumentViewerProps = {
  documentId: string
  activeChunkId?: string
  onClose: () => void
}

type Chunk = {
  id: string
  content: string
  metadata: any
}

export function DocumentViewer({ documentId, activeChunkId, onClose }: DocumentViewerProps) {
  const [chunks, setChunks] = useState<Chunk[]>([])
  const [docName, setDocName] = useState("Loading Document...")
  const [loading, setLoading] = useState(true)
  const supabase = createClient()
  
  // Create a ref map to dynamically scroll to the correct chunk
  const chunkRefs = useRef<{ [key: string]: HTMLDivElement | null }>({})

  useEffect(() => {
    async function fetchDocument() {
      setLoading(true)
      
      // Get doc name
      const { data: docData } = await supabase
        .from('documents')
        .select('filename')
        .eq('id', documentId)
        .single()
        
      if (docData) setDocName(docData.filename)

      // Get all chunks for doc
      const { data: chunkData } = await supabase
        .from('chunks')
        .select('id, content, metadata')
        .eq('document_id', documentId)

      if (chunkData) {
        // Sort chunks by their index metadata to reconstruct the document order
        const sorted = [...chunkData].sort((a, b) => {
          const idxA = a.metadata?.index || 0
          const idxB = b.metadata?.index || 0
          return idxA - idxB
        })
        setChunks(sorted)
      }
      setLoading(false)
    }

    if (documentId) {
      fetchDocument()
    }
  }, [documentId])

  // Scroll to active chunk
  useEffect(() => {
    if (!loading && activeChunkId) {
      const el = chunkRefs.current[activeChunkId]
      if (el) {
        // Scroll smoothly to the exact paragraph the AI cited
        setTimeout(() => {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }, 300)
      }
    }
  }, [loading, activeChunkId])

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="h-full w-full flex flex-col bg-background overflow-hidden relative"
    >
      {/* Viewer Header */}
      <div className="h-20 shrink-0 border-b border-border bg-card flex items-center justify-between px-8 sticky top-0 z-10">
        <div className="flex items-center gap-4 overflow-hidden">
          <div className="h-10 w-10 rounded-lg bg-foreground text-background flex justify-center items-center shrink-0">
            <FileText className="h-5 w-5" />
          </div>
          <div className="flex flex-col min-w-0">
             <h3 className="font-bold text-sm text-foreground truncate uppercase tracking-tight">{docName}</h3>
             <p className="text-[10px] font-black text-muted uppercase tracking-[0.2em] flex items-center gap-2">
               <Sparkles className="h-3 w-3" /> AI Context Verification
             </p>
          </div>
        </div>
        <button 
          onClick={onClose}
          className="h-10 w-10 rounded-full border border-border hover:border-foreground hover:bg-foreground/5 text-muted hover:text-foreground flex justify-center items-center transition-all"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Reconstructed Content Stream */}
      <div className="flex-1 overflow-y-auto p-10 relative custom-scrollbar bg-background">
        {loading ? (
          <div className="h-full flex flex-col items-center justify-center">
            <div className="relative mb-6">
               <div className="absolute inset-0 blur-xl bg-foreground/10 rounded-full animate-pulse" />
               <Loader2 className="h-10 w-10 relative animate-spin text-foreground/40" />
            </div>
            <p className="text-[10px] font-black uppercase tracking-[0.3em] text-muted">Reconstructing Knowledge Units...</p>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6 pb-32">
            {chunks.map((chunk) => {
              const isActive = chunk.id === activeChunkId
              return (
                <div 
                  key={chunk.id} 
                  ref={(el) => { chunkRefs.current[chunk.id] = el }}
                  className={`
                    text-foreground/90 leading-loose text-[16px] font-medium transition-all duration-500 p-6 rounded-2xl border
                    ${isActive 
                      ? 'bg-foreground text-background border-foreground shadow-2xl scale-[1.01]' 
                      : 'bg-card border-border hover:border-foreground/20'
                    }
                  `}
                >
                  <div className={`mb-4 flex items-center justify-between opacity-40 text-[9px] font-black uppercase tracking-widest ${isActive ? 'text-background' : 'text-muted'}`}>
                     <span>Chunk ID: {chunk.id.split('-')[0]}</span>
                     {isActive && <span className="flex items-center gap-1"><Sparkles className="h-3 w-3" /> Cited Context</span>}
                  </div>
                  {chunk.content}
                </div>
              )
            })}
            {chunks.length === 0 && (
              <div className="p-12 border border-dashed border-border rounded-3xl text-center">
                <p className="text-[10px] font-black uppercase tracking-widest text-muted">No vectorized context stream available</p>
              </div>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}
