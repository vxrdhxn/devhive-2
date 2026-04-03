"use client"
 
import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Bot, LogOut, Search, Command } from "lucide-react"
import { ThemeToggle } from "./ThemeToggle"
import { logout } from "@/app/login/actions"
import { createClient } from "@/utils/supabase/client"
 
export function Navbar() {
  const pathname = usePathname()
  const [role, setRole] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    async function getProfile() {
      try {
        const { data: { user } } = await supabase.auth.getUser()
        if (user) {
          const { data: profile } = await supabase
            .from('profiles')
            .select('role')
            .eq('id', user.id)
            .single()
          
          if (profile) setRole(profile.role)
        }
      } catch (err) {
        console.error("Error fetching role:", err)
      } finally {
        setLoading(false)
      }
    }
    getProfile()
  }, [supabase])
  
  return (
    <nav className="border-b border-border bg-background/80 backdrop-blur-md sticky top-0 z-50">
      <div className="px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 group">
            <Bot className="h-6 w-6 text-foreground group-hover:scale-110 transition-transform" />
            <span className="font-bold text-xl tracking-tight">
              Dev<span className="text-muted">Hive</span>
            </span>
          </Link>
          
          <div className="hidden md:flex items-center gap-1 p-1 bg-muted/5 rounded-full border border-border">
            <Link 
              href="/" 
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                pathname === "/" 
                  ? "bg-foreground text-background shadow-sm" 
                  : "hover:bg-muted/10 text-muted-foreground"
              }`}
            >
              Workspace
            </Link>
            {!loading && (role === 'admin' || role === 'manager') && (
              <>
                <Link 
                  href="/overview" 
                  className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                    pathname === "/overview" 
                      ? "bg-foreground text-background shadow-sm" 
                      : "hover:bg-muted/10 text-muted-foreground"
                  }`}
                >
                  Overview
                </Link>
                <Link 
                  href="/analytics" 
                  className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
                    pathname === "/analytics" 
                      ? "bg-foreground text-background shadow-sm" 
                      : "hover:bg-muted/10 text-muted-foreground"
                  }`}
                >
                  Analytics
                </Link>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-muted/5 hover:bg-muted/10 transition-colors border border-border rounded-lg text-muted cursor-pointer group">
             <Search className="h-3.5 w-3.5" />
             <span className="text-xs font-medium">Search...</span>
             <kbd className="text-[10px] font-bold font-mono bg-background px-1.5 py-0.5 rounded border border-border text-muted flex items-center gap-0.5">
               <Command className="h-3 w-3" />K
             </kbd>
          </div>
          
          <div className="h-8 w-[1px] bg-border mx-2 hidden sm:block" />
          
          <ThemeToggle />
          
          <form action={logout}>
            <button className="h-9 w-9 flex items-center justify-center rounded-full border border-border hover:bg-red-50 hover:text-red-600 transition-all">
              <LogOut className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </nav>
  )
}
