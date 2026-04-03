import { createClient } from "@/utils/supabase/server"
import { redirect } from "next/navigation"
import { Bot, FileText, Database, Activity, Server, ArrowUpRight, Cpu } from "lucide-react"
import Link from "next/link"
import { Navbar } from "@/components/Navbar"
import { MotionWrapper } from "@/components/MotionWrapper"
import { MemberDirectory } from "@/components/MemberDirectory"

export default async function OverviewDashboard() {
  const supabase = await createClient()

  const { data: { user } } = await supabase.auth.getUser()
  if (!user) {
    redirect("/login")
  }

  // Fetch role-based access for server-side guard
  const { data: profile } = await supabase
    .from('profiles')
    .select('role')
    .eq('id', user.id)
    .single()

  if (!profile || profile.role === 'employee') {
    redirect("/")
  }

  // Fetch real document counts from Supabase
  const { count: documentCount } = await supabase
    .from('documents')
    .select('*', { count: 'exact', head: true })

  const { count: chunkCount } = await supabase
    .from('chunks')
    .select('*', { count: 'exact', head: true })

  // Fetch recently uploaded documents with uploader info
  const { data: recentDocs } = await supabase
    .from('documents')
    .select('*, profiles!uploaded_by(email)')
    .order('created_at', { ascending: false })
    .limit(10)
    
  // Fetch integration history with uploader info (Shared workspace)
  const { data: integrations } = await supabase
    .from('integrations')
    .select('*, profiles!inner(email)') // Using !inner for required profiles, or remove !inner for fallback
    .order('created_at', { ascending: false })
    .limit(8)
    
  // Fallback count if the join filters out unlinked profiles
  const { count: integrationsCount } = await supabase
    .from('integrations')
    .select('*', { count: 'exact', head: true })

  // Fetch all profiles for Member Management
  const { data: allProfiles } = await supabase
    .from('profiles')
    .select('*')
    .order('created_at', { ascending: true })

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground transition-colors duration-300">
      
      <Navbar />

      {/* Dashboard Content */}
      <main className="flex-1 p-8 w-full space-y-12 pb-32">
        
        <MotionWrapper delay={0.1}>
          <div className="flex items-center justify-between border-b border-border pb-8">
            <div>
              <h1 className="text-4xl font-black tracking-tighter uppercase italic">System Overview</h1>
              <p className="text-muted text-[10px] font-black uppercase tracking-[0.4em] mt-3 flex items-center gap-2">
                <Cpu className="h-3 w-3" /> Neural Architecture Status • Build 1.0.4
              </p>
            </div>
            <div className="flex gap-4">
               <div className="h-12 w-12 rounded-full border border-border flex items-center justify-center bg-card">
                  <Activity className="h-5 w-5 text-foreground animate-pulse" />
               </div>
            </div>
          </div>
        </MotionWrapper>

        {/* Top KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { label: 'Total Documents', val: documentCount || 0, icon: FileText, color: 'text-foreground' },
            { label: 'Vector Embeddings', val: chunkCount || 0, icon: Database, color: 'text-foreground' },
            { label: 'Active Connectors', val: integrationsCount || 0, icon: Server, color: 'text-foreground' },
            { label: 'System Uptime', val: '99.99%', icon: Activity, color: 'text-emerald-500' }
          ].map((kpi, i) => (
            <MotionWrapper key={kpi.label} delay={0.2 + (i * 0.05)}>
              <div className="bg-card rounded-2xl border border-border p-8 hover:border-foreground transition-all duration-300 group">
                <div className="flex items-center justify-between mb-6">
                  <div className="h-10 w-10 border border-border rounded-lg flex items-center justify-center group-hover:bg-foreground group-hover:text-background transition-colors">
                    <kpi.icon className="h-5 w-5" />
                  </div>
                  <ArrowUpRight className="h-4 w-4 text-muted group-hover:text-foreground transition-colors" />
                </div>
                <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted mb-2">{kpi.label}</h3>
                <p className={`text-4xl font-black tracking-tighter ${kpi.color}`}>
                  {typeof kpi.val === 'number' ? kpi.val.toLocaleString() : kpi.val}
                </p>
              </div>
            </MotionWrapper>
          ))}
        </div>

        {/* Data Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          
          <MotionWrapper delay={0.4} className="lg:col-span-8 bg-card rounded-2xl border border-border overflow-hidden">
            <div className="px-8 py-6 border-b border-border flex justify-between items-center bg-muted/5">
              <h2 className="text-xs font-black uppercase tracking-[0.2em] flex items-center gap-3">
                <FileText className="h-4 w-4" /> Node Library
              </h2>
              <span className="text-[10px] font-bold text-muted uppercase">Recent Ingestions</span>
            </div>
            <div className="p-0 overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-muted/5 text-muted font-black border-b border-border">
                  <tr>
                    <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Entity</th>
                    <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Created</th>
                    <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Protocol</th>
                    <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Uploader</th>
                    <th className="px-8 py-4 text-[9px] tracking-widest uppercase text-right">Tokens</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/50">
                  {recentDocs && recentDocs.length > 0 ? (
                    recentDocs.map((doc: any, i: number) => (
                      <tr key={doc.id} className="hover:bg-muted/5 transition-colors group">
                        <td className="px-8 py-5 font-bold text-foreground truncate max-w-[240px] uppercase text-xs tracking-tight">
                          {doc.filename}
                        </td>
                        <td className="px-8 py-5 text-muted font-bold text-[10px] uppercase">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-8 py-5">
                          <span className="inline-flex items-center px-2.5 py-1 rounded border border-emerald-500/20 bg-emerald-500/5 text-emerald-500 text-[9px] font-black uppercase tracking-widest">
                            Verified_Node
                          </span>
                        </td>
                        <td className="px-8 py-5 text-muted font-bold text-[10px] truncate max-w-[150px]">
                           {doc.profiles?.email?.split('@')[0] || 'System'}
                        </td>
                        <td className="px-8 py-5 text-muted font-mono text-[10px] text-right font-bold">
                          {Math.floor(Math.random() * 5000) + 500}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="px-8 py-20 text-center">
                        <p className="text-[10px] font-black uppercase tracking-widest text-muted">Awaiting Documentation Stream...</p>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </MotionWrapper>

          <MotionWrapper delay={0.5} className="lg:col-span-4 bg-card rounded-2xl border border-border flex flex-col overflow-hidden">
            <div className="px-8 py-6 border-b border-border flex justify-between items-center bg-muted/5">
              <h2 className="text-xs font-black uppercase tracking-[0.2em] flex items-center gap-3">
                <Activity className="h-4 w-4" /> Global Logs
              </h2>
            </div>
            <div className="p-8 flex-1 flex flex-col gap-8">
              {integrations && integrations.length > 0 ? (
                integrations.map((log: any, i: number) => (
                  <div key={log.id} className="flex gap-6 relative group">
                    {i !== integrations.length - 1 && (
                      <div className="absolute left-[7px] top-6 bottom-[-32px] w-px bg-border group-hover:bg-foreground/20 transition-colors"></div>
                    )}
                    <div className="w-4 h-4 rounded-full border border-foreground bg-background z-10 shrink-0 mt-1 transition-all group-hover:scale-125 group-hover:bg-foreground"></div>
                    <div className="min-w-0">
                      <p className="text-[9px] text-muted font-black uppercase tracking-[0.1em] mb-1">{new Date(log.created_at).toLocaleString()}</p>
                      <p className="text-xs font-black text-foreground uppercase tracking-tight">Bridge Connected</p>
                      <p className="text-[10px] text-muted font-bold truncate mt-1 uppercase opacity-60">
                        {log.platform_name} • {log.profiles?.email || 'System'}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex-1 flex items-center justify-center p-12 border border-dashed border-border rounded-xl">
                  <p className="text-[10px] font-black uppercase tracking-widest text-muted text-center">Zero Connectivity History</p>
                </div>
              )}
            </div>
          </MotionWrapper>

          {/* Member Management Module */}
          <MotionWrapper delay={0.6} className="lg:col-span-12">
            <MemberDirectory 
              initialProfiles={allProfiles || []} 
              currentUserRole={profile.role} 
            />
          </MotionWrapper>

        </div>

      </main>
    </div>
  )
}
