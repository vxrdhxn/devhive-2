"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Terminal, Activity, CheckCircle, Clock, AlertCircle, Trash2, Loader2 } from "lucide-react"
import { createClient } from "@/utils/supabase/client"

type ProcessingDoc = {
  id: string
  filename: string
  status: string
  created_at: string
}

export function ProcessingMatrix() {
  const [docs, setDocs] = useState<ProcessingDoc[]>([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const supabase = createClient()

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    setDeletingId(id)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api"
      const res = await fetch(`${backendUrl}/documents/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${session?.access_token}`
        }
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || "Delete operation failed")
      }
      setDocs(prev => prev.filter(d => d.id !== id))
    } catch (err: any) {
      console.error(err)
      alert(`Deletion Failed: ${err.message}`)
    } finally {
      setDeletingId(null)
    }
  }

  const fetchStatus = async () => {
    const { data, error } = await supabase
      .from('documents')
      .select('id, filename, status, created_at')
      .order('created_at', { ascending: false })

    if (!error && data) {
      setDocs(data)
    }
    setLoading(false)
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 3000) // Poll every 3s for "Live" feel
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="p-8 bg-card rounded-2xl border border-border overflow-hidden relative group">
      {/* Terminal Header */}
      <div className="flex items-center justify-between mb-6 border-b border-border pb-4">
        <div className="flex items-center gap-3">
           <div className="flex gap-1.5 mr-2">
             <div className="h-2 w-2 rounded-full border border-border" />
             <div className="h-2 w-2 rounded-full border border-border" />
             <div className="h-2 w-2 rounded-full border border-border" />
           </div>
           <Activity className="h-4 w-4 text-foreground" />
           <span className="text-[10px] font-black uppercase tracking-widest text-muted">Ingestion Matrix V2.0</span>
        </div>
        <div className="h-2 w-2 rounded-full bg-foreground animate-pulse" />
      </div>

      {/* Terminal Body */}
      <div className="space-y-4 font-mono text-[10px] min-h-[160px] max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
        {loading && docs.length === 0 ? (
          <div className="text-muted animate-pulse font-bold uppercase tracking-widest">Awaiting Knowledge Stream...</div>
        ) : (
          <AnimatePresence mode="popLayout">
            {docs.map((doc) => {
              const isCompleted = doc.status === 'completed'
              const isError = doc.status === 'error'
              
              return (
                <motion.div 
                  layout
                  initial={{ opacity: 0, x: -5 }}
                  animate={{ opacity: 1, x: 0 }}
                  key={doc.id}
                  className="flex items-center justify-between group/row border-b border-border/10 pb-2 last:border-0"
                >
                  <div className="flex items-center gap-4 overflow-hidden">
                    <span className="text-muted font-bold">[{new Date(doc.created_at).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit' })}]</span>
                    <span className="text-foreground font-black truncate max-w-[140px] uppercase">{doc.filename}</span>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <div className={`flex items-center gap-2 px-2 py-1 rounded-md border text-[9px] font-black uppercase tracking-widest ${
                      isCompleted ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : 
                      isError ? 'text-red-500 border-red-500/20 bg-red-500/5' : 
                      'text-muted border-border bg-muted/5 animate-pulse'
                    }`}>
                      {doc.status}
                    </div>
                    
                    <button 
                      onClick={(e) => handleDelete(e, doc.id)}
                      disabled={deletingId === doc.id}
                      className="opacity-0 group-hover/row:opacity-100 transition-opacity p-1 hover:bg-red-500/10 rounded-md text-muted hover:text-red-500"
                    >
                      {deletingId === doc.id ? <Loader2 className="h-3 w-3 animate-spin"/> : <Trash2 className="h-3 w-3" />}
                    </button>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        )}

        {!loading && docs.length === 0 && (
          <div className="text-muted italic opacity-50 uppercase tracking-widest py-8 text-center border border-dashed border-border rounded-xl">
             No active operations found in buffer
          </div>
        )}
      </div>

      {/* Bottom status */}
      <div className="mt-8 pt-4 border-t border-border flex justify-between items-center">
         <span className="text-[9px] text-muted font-bold uppercase tracking-[0.2em] flex items-center gap-2">
           <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> System Optimized
         </span>
         <span className="text-[9px] text-foreground font-black uppercase tracking-widest">Vector Core Active</span>
      </div>
    </div>
  )
}
