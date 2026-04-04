"use client"

import { useState } from "react"
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { createClient } from "@/utils/supabase/client"
import { motion, AnimatePresence } from "framer-motion"

export function UploadPanel() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState<"idle" | "success" | "error" | "offline" | "duplicate">("idle")
  const [isPrivate, setIsPrivate] = useState(false)
  const supabase = createClient()
  const [duplicateMessage, setDuplicateMessage] = useState("")

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
      setStatus("idle")
      setDuplicateMessage("")
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setStatus("idle")
    setDuplicateMessage("")

    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      const formData = new FormData()
      formData.append("file", file)
      formData.append("is_private", isPrivate.toString())

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api"
      // Note: We use query params for boolean/simple flags to match FastAPI's easier handling of non-file fields in some setups
      const res = await fetch(`${backendUrl}/documents/upload?is_private=${isPrivate}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`
        },
        body: formData
      })
      
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || "Upload failed")
      }
      
      const data = await res.json()
      if (data.status === "duplicate") {
        setStatus("duplicate")
        setDuplicateMessage(data.message)
      } else {
        setStatus("success")
        setFile(null)
        setIsPrivate(false)
      }
    } catch (err: any) {
      console.error("Upload error details:", err)
      if (err.name === "TypeError" && err.message === "Failed to fetch") {
        setStatus("offline")
      } else {
        alert(`Ingestion failed: ${err.message}`)
        setStatus("error")
      }
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-8 bg-card border-b border-border">
      <h2 className="text-sm font-bold mb-6 flex items-center justify-between uppercase tracking-widest text-muted">
        <div className="flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Ingestion Layer
        </div>
      </h2>
      
      <motion.label 
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center bg-muted/5 hover:bg-muted/10 transition-all cursor-pointer group relative overflow-hidden"
      >
        <input 
          type="file" 
          className="hidden" 
          accept=".pdf,.docx,.txt,.md,.pptx,.xlsx,.csv,.rtf"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <AnimatePresence mode="wait">
          {file ? (
            <motion.div 
              key="file"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="flex flex-col items-center"
            >
              <div className="h-12 w-12 bg-foreground text-background rounded-full flex items-center justify-center mb-4 shadow-sm">
                 <FileText className="h-6 w-6" />
              </div>
              <p className="text-sm font-bold text-center max-w-[200px] truncate tracking-tight">{file.name}</p>
              <p className="text-[10px] font-black uppercase tracking-widest mt-2 opacity-50">Staged for Indexing</p>
            </motion.div>
          ) : (
            <motion.div 
              key="empty"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="flex flex-col items-center text-center px-4"
            >
              <div className="h-12 w-12 bg-background border border-border text-muted rounded-full flex items-center justify-center mb-4 group-hover:bg-foreground group-hover:text-background group-hover:border-foreground transition-all">
                 <Upload className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold tracking-tight">Supply Knowledge Unit</p>
              <p className="text-[10px] text-muted mt-2 font-medium leading-relaxed max-w-[180px]">
                Accepts PDF, DOCX, XLSX, CSV, MD, and standard text formats
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.label>

      {/* Privacy Toggle */}
      <div className="mt-6 flex items-center justify-between p-4 bg-muted/5 rounded-xl border border-border">
        <div className="flex flex-col">
          <span className="text-[10px] font-black uppercase tracking-widest mb-1">Visibility Level</span>
          <span className="text-[9px] text-muted font-medium">Managers/Admins only if enabled</span>
        </div>
        <button
          onClick={() => setIsPrivate(!isPrivate)}
          className={`relative inline-flex h-5 w-10 items-center rounded-full transition-colors focus:outline-none ${
            isPrivate ? "bg-foreground" : "bg-muted/20"
          }`}
        >
          <span
            className={`inline-block h-3 w-3 transform rounded-full bg-background transition-transform ${
              isPrivate ? "translate-x-6" : "translate-x-1"
            }`}
          />
        </button>
      </div>


      <AnimatePresence>
        {file && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <motion.button 
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={handleUpload}
              disabled={uploading}
              className="w-full bg-foreground text-background font-bold py-4 px-4 rounded-xl mt-6 transition-all disabled:opacity-50 flex justify-center items-center gap-2 text-sm uppercase tracking-widest"
            >
              {uploading ? (
                 <><Loader2 className="h-4 w-4 animate-spin" /> Vectorizing...</>
              ) : (
                "Execute Ingestion"
              )}
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {status === "success" && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 bg-foreground text-background rounded-xl flex items-center gap-3 text-xs font-bold uppercase tracking-widest"
          >
            <CheckCircle className="h-4 w-4" />
            Indexing Successful
          </motion.div>
        )}
        {status === "error" && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 border border-red-500/20 bg-red-500/5 text-red-500 rounded-xl flex items-center gap-3 text-xs font-bold uppercase tracking-widest"
          >
            <AlertCircle className="h-4 w-4" />
            Ingestion Request Failed
          </motion.div>
        )}
        {status === "duplicate" && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 border border-amber-500/20 bg-amber-500/5 text-amber-500 rounded-xl flex items-center gap-3 text-xs font-bold uppercase tracking-widest"
          >
            <AlertCircle className="h-4 w-4" />
            {duplicateMessage || "Duplicate Content Detected"}
          </motion.div>
        )}
        {status === "offline" && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-4 border border-orange-500/20 bg-orange-500/5 text-orange-500 rounded-xl flex items-center gap-3 text-xs font-bold uppercase tracking-widest"
          >
            <AlertCircle className="h-4 w-4" />
            Backend Offline: Check Server
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
