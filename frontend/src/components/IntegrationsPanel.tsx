"use client"

import { useState, useEffect } from "react"
import { Plug, CheckCircle2, Plus, Server, Key, Globe, Box, Layout, ShieldCheck, Trash2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { createClient } from "@/utils/supabase/client"

type CustomIntegration = {
  id: string
  platform_name: string
  base_url: string
  platform_type: string
  status: string
  last_synced_at?: string
  created_at?: string
}

export function IntegrationsPanel() {
  const [connections, setConnections] = useState<CustomIntegration[]>([])
  const [isAdding, setIsAdding] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [syncingId, setSyncingId] = useState<string | null>(null)
  const supabase = createClient()
  
  // Form State
  const [platformName, setPlatformName] = useState("")
  const [baseUrl, setBaseUrl] = useState("")
  const [apiKey, setApiKey] = useState("")

  useEffect(() => {
    async function loadConnections() {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      const { data } = await supabase
        .from('integrations')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (data) setConnections(data)
    }
    loadConnections()
  }, [])

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!platformName || !apiKey) return
    
    setIsSubmitting(true)
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        alert("Session expired. Please log in again.")
        return
      }

      // Infer platform type (simple heuristic)
      const platformType = platformName.toLowerCase().includes('notion') ? 'notion' : 'rest'

      const newConnection = {
        user_id: user.id,
        platform_name: platformName,
        base_url: baseUrl,
        api_token: apiKey,
        platform_type: platformType,
        status: 'active'
      }

      const { data, error } = await supabase
        .from('integrations')
        .insert([newConnection])
        .select()
        .single()

      if (error) {
        throw error
      }
      
      setConnections(prev => [data, ...prev])
      
      // Reset
      setPlatformName("")
      setBaseUrl("")
      setApiKey("")
      setIsAdding(false)
    } catch (err: any) {
      console.error("Failed to insert integration:", err)
      alert(`Connection failed: ${err.message || "Unknown error"}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRemove = async (integrationId: string) => {
    if (!confirm("Are you sure you want to remove this connection? This will stop all synchronization.")) return
    
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api"
      const response = await fetch(`${backendUrl}/integrations/${integrationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`
        }
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || "Removal failed")
      }
      
      setConnections(prev => prev.filter(c => c.id !== integrationId))
    } catch (err: any) {
      console.error("Failed to delete integration:", err)
      alert(`Removal failed: ${err.message}`)
    }
  }

  const handleSync = async (integrationId: string) => {
    setSyncingId(integrationId)
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000"
      const response = await fetch(`${backendUrl}/integrations/${integrationId}/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`
        }
      })
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || "Sync failed")
      }
      
      const result = await response.json()
      alert(`Sync successful! Processed context from ${result.pages_indexed || result.items_indexed || result.pages_found || 0} nodes.`)
      
      const { data } = await supabase.from('integrations').select('*').eq('id', integrationId).single()
      if (data) {
        setConnections(prev => prev.map(c => c.id === integrationId ? data : c))
      }
    } catch (err: any) {
      console.error(err)
      alert(`Sync failed: ${err.message}`)
    } finally {
      setSyncingId(null)
    }
  }

  return (
    <div className="p-8 bg-card min-h-[400px]">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-sm font-bold flex items-center gap-2 uppercase tracking-widest text-muted">
            <Plug className="h-4 w-4" />
            Active Bridges
          </h2>
        </div>
        
        <motion.button 
          whileHover={{ scale: 1.05, rotate: isAdding ? 0 : 90 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsAdding(!isAdding)}
          className={`h-9 w-9 rounded-full flex items-center justify-center transition-all border ${
            isAdding 
              ? 'bg-foreground text-background border-foreground rotate-45' 
              : 'bg-background text-foreground border-border hover:border-foreground'
          }`}
        >
          <Plus className="h-5 w-5" />
        </motion.button>
      </div>
      
      <div className="space-y-4">
        <AnimatePresence mode="popLayout">
          {connections.length === 0 && !isAdding ? (
            <motion.div 
              key="empty"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="text-center py-16 px-6 border border-dashed border-border rounded-2xl bg-muted/5"
            >
              <div className="h-14 w-14 border border-border bg-background rounded-full flex items-center justify-center mx-auto mb-4">
                <Globe className="h-6 w-6 text-muted" />
              </div>
              <p className="text-xs font-bold uppercase tracking-widest text-foreground">Zero Node Connectivity</p>
              <p className="text-[10px] text-muted mt-3 max-w-[200px] mx-auto leading-relaxed font-medium">
                Bridge external context by providing an identity and protocol key.
              </p>
            </motion.div>
          ) : (
            connections.map((conn) => (
              <motion.div 
                key={conn.id}
                layout
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="group border border-border bg-background rounded-xl p-5 flex items-center justify-between hover:border-foreground transition-all duration-300"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 bg-foreground text-background rounded flex items-center justify-center overflow-hidden">
                    <Box className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm tracking-tight">{conn.platform_name}</h3>
                    <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.2em] mt-2">
                      <span className="text-emerald-500 flex items-center gap-1">
                        <ShieldCheck className="h-2.5 w-2.5" />
                        Live
                      </span>
                      <span className="text-muted/40">•</span>
                      <span className="text-muted">
                        {conn.last_synced_at ? `Refreshed ${new Date(conn.last_synced_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}` : 'Static'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <motion.button 
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleRemove(conn.id)}
                    className="h-8 w-8 rounded-full flex items-center justify-center text-muted hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950 transition-all border border-transparent hover:border-red-200 dark:hover:border-red-900"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </motion.button>

                  <motion.button 
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSync(conn.id)}
                    disabled={syncingId === conn.id}
                    className={`px-4 py-2 rounded-lg font-black text-[9px] uppercase tracking-widest border transition-all ${
                      syncingId === conn.id 
                        ? "bg-muted/10 text-muted border-transparent cursor-not-allowed"
                        : "bg-background text-foreground border-border hover:bg-foreground hover:text-background hover:border-foreground"
                    }`}
                  >
                    {syncingId === conn.id ? 'Refreshing...' : 'Sync Now'}
                  </motion.button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        <AnimatePresence>
          {isAdding && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="mt-4"
            >
              <form onSubmit={handleConnect} className="border border-foreground bg-background rounded-2xl p-6 flex flex-col gap-6 relative overflow-hidden ring-1 ring-foreground/5">
                <div className="space-y-5">
                  <div>
                    <label className="text-[9px] font-black uppercase tracking-[0.2em] text-muted mb-3 block">Namespace</label>
                    <div className="relative">
                      <Layout className="h-4 w-4 text-muted absolute left-4 top-3.5" />
                      <input
                        required
                        type="text"
                        placeholder="e.g. GitHub Repository"
                        value={platformName}
                        onChange={(e) => setPlatformName(e.target.value)}
                        className="w-full rounded-lg border border-border bg-muted/5 pl-11 pr-4 py-3 text-xs font-bold text-foreground focus:bg-background focus:ring-0 focus:border-foreground focus:outline-none transition-all"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[9px] font-black uppercase tracking-[0.2em] text-muted mb-3 block">Endpoint URI</label>
                    <div className="relative">
                      <Globe className="h-4 w-4 text-muted absolute left-4 top-3.5" />
                      <input
                        type="url"
                        placeholder="https://api.provider.com"
                        value={baseUrl}
                        onChange={(e) => setBaseUrl(e.target.value)}
                        className="w-full rounded-lg border border-border bg-muted/5 pl-11 pr-4 py-3 text-xs font-bold text-foreground focus:bg-background focus:ring-0 focus:border-foreground focus:outline-none transition-all font-mono"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="text-[9px] font-black uppercase tracking-[0.2em] text-muted mb-3 block">Protocol Key</label>
                    <div className="relative">
                      <Key className="h-4 w-4 text-muted absolute left-4 top-3.5" />
                      <input
                        required
                        type="password"
                        placeholder="Bearer Token / JWT"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        className="w-full rounded-lg border border-border bg-muted/5 pl-11 pr-4 py-3 text-xs font-bold text-foreground focus:bg-background focus:ring-0 focus:border-foreground focus:outline-none transition-all"
                      />
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-3 pt-2">
                  <button 
                    type="button"
                    onClick={() => setIsAdding(false)}
                    className="flex-1 bg-background border border-border text-muted font-bold py-3.5 px-4 rounded-xl hover:bg-muted/5 transition-all text-[10px] uppercase tracking-widest"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    disabled={!platformName || !apiKey || isSubmitting}
                    className="flex-[2] bg-foreground text-background font-black py-3.5 px-4 rounded-xl hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 text-[10px] uppercase tracking-widest shadow-lg shadow-foreground/5"
                  >
                    {isSubmitting ? (
                      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                        <Plug className="h-4 w-4" />
                      </motion.div>
                    ) : (
                      <Plug className="h-4 w-4" />
                    )}
                    {isSubmitting ? 'Bridges Uplinking...' : 'Bridge Connectivity'}
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
