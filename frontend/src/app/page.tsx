import { createClient } from "@/utils/supabase/server"
import { redirect } from "next/navigation"
import { logout } from "./login/actions"
import { LayoutGrid, Activity } from "lucide-react"
import Link from "next/link"
import { SearchPanel } from "@/components/SearchPanel"
import { UploadPanel } from "@/components/UploadPanel"
import { IntegrationsPanel } from "@/components/IntegrationsPanel"
import { ProcessingMatrix } from "@/components/ProcessingMatrix"
import { MotionWrapper } from "@/components/MotionWrapper"
import { CommandMenu } from "@/components/CommandMenu"
import { Navbar } from "@/components/Navbar"

export default async function Home() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/login")
  }

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground transition-colors duration-300">
      <CommandMenu />

      <Navbar />

      <main className="flex-1 w-full px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          
          {/* Main Search Experience */}
          <div className="lg:col-span-8 space-y-10">
            <MotionWrapper delay={0.1} className="bg-card border border-border rounded-2xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none min-h-[600px]">
              <SearchPanel />
            </MotionWrapper>
          </div>

          {/* Productivity & Integration Sidebar */}
          <div className="lg:col-span-4 space-y-8 h-[calc(100vh-120px)] overflow-y-auto pr-2">
            <MotionWrapper delay={0.2} className="bg-card border border-border rounded-2xl p-1 shadow-sm">
              <UploadPanel />
            </MotionWrapper>

            <MotionWrapper delay={0.25}>
              <ProcessingMatrix />
            </MotionWrapper>

            <MotionWrapper delay={0.3} className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
              <IntegrationsPanel />
            </MotionWrapper>
            
            <MotionWrapper delay={0.4} className="border border-border rounded-2xl p-8 text-center bg-muted/5">
               <h3 className="font-bold text-sm mb-3 uppercase tracking-widest text-muted">Platform Node</h3>
               <div className="space-y-2 text-xs text-muted font-medium">
                 <p className="flex justify-between border-b border-border/50 pb-2"><span>Version</span> <span>1.0.4-beta</span></p>
                 <p className="flex justify-between border-b border-border/50 pb-2"><span>Kernel</span> <span>FastAPI v0.110</span></p>
                 <p className="flex justify-between"><span>Core AI</span> <span>llama-3-8b-instruct</span></p>
               </div>
            </MotionWrapper>
          </div>
        </div>
      </main>
    </div>
  )
}

