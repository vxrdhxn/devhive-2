"use client"

import { useState } from "react"
import { createClient } from "@/utils/supabase/client"
import { Shield, User, Star, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"

interface Profile {
  id: string
  email: string | null
  role: string | null
  created_at: string
}

interface MemberDirectoryProps {
  initialProfiles: Profile[]
  currentUserRole: string
}

export function MemberDirectory({ initialProfiles, currentUserRole }: MemberDirectoryProps) {
  const [profiles, setProfiles] = useState(initialProfiles)
  const [updating, setUpdating] = useState<string | null>(null)
  const supabase = createClient()
  const router = useRouter()

  const handleRoleChange = async (userId: string, newRole: string) => {
    if (currentUserRole !== 'admin') return
    
    setUpdating(userId)
    try {
      const { error } = await supabase
        .from('profiles')
        .update({ role: newRole })
        .eq('id', userId)

      if (error) throw error

      setProfiles(prev => prev.map(p => p.id === userId ? { ...p, role: newRole } : p))
      router.refresh()
    } catch (err) {
      console.error("Failed to update role:", err)
      alert("Failed to update user role. Permissions denied.")
    } finally {
      setUpdating(null)
    }
  }

  const roles = [
    { id: 'admin', icon: Star, label: 'Admin', color: 'text-amber-500' },
    { id: 'manager', icon: Shield, label: 'Manager', color: 'text-blue-500' },
    { id: 'employee', icon: User, label: 'Employee', color: 'text-muted' }
  ]

  return (
    <div className="bg-card rounded-2xl border border-border overflow-hidden col-span-12">
      <div className="px-8 py-6 border-b border-border flex justify-between items-center bg-muted/5">
        <h2 className="text-xs font-black uppercase tracking-[0.2em] flex items-center gap-3">
          <Shield className="h-4 w-4" /> Member Directory
        </h2>
        <span className="text-[10px] font-bold text-muted-foreground uppercase">{profiles.length} Total Members</span>
      </div>
      <div className="p-0 overflow-x-auto">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-muted/5 text-muted font-black border-b border-border">
            <tr>
              <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Member</th>
              <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Status</th>
              <th className="px-8 py-4 text-[9px] tracking-widest uppercase">Privileges</th>
              <th className="px-8 py-4 text-[9px] tracking-widest uppercase text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {profiles.map((profile) => (
              <tr key={profile.id} className="hover:bg-muted/5 transition-colors group">
                <td className="px-8 py-5">
                  <div className="flex flex-col">
                    <span className="font-bold text-foreground text-xs tracking-tight uppercase">
                      {profile.email?.split('@')[0]}
                    </span>
                    <span className="text-[10px] text-muted font-bold lowercase opacity-60">
                      {profile.email}
                    </span>
                  </div>
                </td>
                <td className="px-8 py-5">
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[8px] font-black uppercase tracking-widest border border-emerald-500/20">
                    Active_Node
                  </span>
                </td>
                <td className="px-8 py-5">
                  <div className="flex items-center gap-2">
                    {roles.find(r => r.id === profile.role)?.label || 'Employee'}
                  </div>
                </td>
                <td className="px-8 py-5 text-right">
                  {currentUserRole === 'admin' ? (
                    <div className="flex items-center justify-end gap-2">
                       {updating === profile.id ? (
                         <Loader2 className="h-4 w-4 animate-spin text-muted" />
                       ) : (
                         roles.map((role) => (
                           <button
                             key={role.id}
                             onClick={() => handleRoleChange(profile.id, role.id)}
                             disabled={profile.role === role.id}
                             className={`px-3 py-1 text-[9px] font-black uppercase tracking-widest border transition-all rounded-md ${
                               profile.role === role.id
                                 ? `${role.color} border-current bg-current/5 opacity-40 cursor-default`
                                 : 'border-border hover:border-foreground text-muted hover:text-foreground'
                             }`}
                           >
                             {role.id.charAt(0)}
                           </button>
                         ))
                       )}
                    </div>
                  ) : (
                    <span className="text-[10px] text-muted font-bold uppercase opacity-40 italic">Read Only</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
