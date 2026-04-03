"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area, Cell
} from 'recharts'
import { 
  TrendingUp, Users, Search, Activity, 
  ArrowUpRight, ArrowDownRight, Zap, Target
} from "lucide-react"
import { createClient } from "@/utils/supabase/client"

export default function AnalyticsPage() {
  const [stats, setStats] = useState<any>(null)
  const [trends, setTrends] = useState<any[]>([])
  const [topTerms, setTopTerms] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const supabase = createClient()

  useEffect(() => {
    async function fetchData() {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (!session) {
          setError("Unauthorized")
          return
        }

        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "/api"
        const headers = { 'Authorization': `Bearer ${session.access_token}` }

        const [statsRes, trendsRes, termsRes] = await Promise.all([
          fetch(`${backendUrl}/analytics/stats`, { headers }),
          fetch(`${backendUrl}/analytics/trends`, { headers }),
          fetch(`${backendUrl}/analytics/top-terms`, { headers })
        ])

        if (!statsRes.ok) throw new Error("Failed to fetch statistics")
        
        const statsData = await statsRes.json()
        const trendsData = await trendsRes.json()
        const termsData = await termsRes.json()

        setStats(statsData)
        setTrends(trendsData)
        setTopTerms(termsData)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) return (
    <div className="flex h-screen items-center justify-center bg-background">
      <motion.div 
        animate={{ rotate: 360 }} 
        transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
        className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full"
      />
    </div>
  )

  if (error) return (
    <div className="flex h-screen items-center justify-center bg-background text-destructive p-4 text-center">
      <div>
        <h1 className="text-2xl font-bold mb-2">Access Restricted</h1>
        <p className="text-muted-foreground">{error === "Unauthorized" ? "Admin or Manager role required." : error}</p>
      </div>
    </div>
  )

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <div className="min-h-screen bg-background p-8 md:p-12">
      <header className="mb-12">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3 mb-4"
        >
          <div className="p-2 bg-primary/10 rounded-lg">
            <Activity className="h-5 w-5 text-primary" />
          </div>
          <h1 className="text-sm font-black uppercase tracking-[0.3em] text-muted-foreground">Neural Intelligence Dashboard</h1>
        </motion.div>
        <motion.h2 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl md:text-5xl font-black tracking-tighter text-foreground"
        >
          System Analytics
        </motion.h2>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <StatCard 
          title="Total Queries" 
          value={stats?.total_queries} 
          icon={<Search className="h-4 w-4" />} 
          trend="+12.5%" 
          positive={true} 
        />
        <StatCard 
          title="Avg Confidence" 
          value={`${Math.round(stats?.avg_confidence * 100)}%`} 
          icon={<Target className="h-4 w-4" />} 
          trend="+2.1%" 
          positive={true} 
        />
        <StatCard 
          title="Active Users" 
          value={stats?.active_users} 
          icon={<Users className="h-4 w-4" />} 
          trend="-0.5%" 
          positive={false} 
        />
        <StatCard 
          title="System Latency" 
          value="1.2s" 
          icon={<Zap className="h-4 w-4" />} 
          trend="Optimized" 
          positive={true} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Line Chart: Queries over time */}
        <motion.div 
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 bg-card border border-border rounded-3xl p-8 shadow-sm"
        >
          <div className="flex items-center justify-between mb-8">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Query Velocity
            </h3>
            <select className="bg-muted/50 border border-border rounded-lg px-3 py-1.5 text-xs font-bold outline-none focus:border-primary transition-all">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" opacity={0.1} />
                <XAxis 
                  dataKey="date" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fontSize: 10, fontWeight: 700, fill: 'var(--muted-foreground)' }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fontSize: 10, fontWeight: 700, fill: 'var(--muted-foreground)' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--card)', 
                    borderColor: 'var(--border)', 
                    borderRadius: '16px',
                    fontSize: '12px',
                    fontWeight: 800,
                    boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="queries" 
                  stroke="var(--primary)" 
                  strokeWidth={4}
                  fillOpacity={1} 
                  fill="url(#colorQueries)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Bar Chart: Top Terms */}
        <motion.div 
          variants={cardVariants}
          initial="hidden"
          animate="visible"
          transition={{ delay: 0.5 }}
          className="bg-card border border-border rounded-3xl p-8 shadow-sm"
        >
          <h3 className="text-lg font-bold mb-8 flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            Top Intent Patterns
          </h3>
          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topTerms} layout="vertical">
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="term" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false} 
                  width={100}
                  tick={{ fontSize: 10, fontWeight: 700, fill: 'var(--foreground)' }}
                />
                <Tooltip 
                   cursor={{ fill: 'transparent' }}
                   contentStyle={{ 
                    backgroundColor: 'var(--card)', 
                    borderColor: 'var(--border)', 
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: 700
                  }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {topTerms.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={index === 0 ? 'var(--primary)' : 'var(--muted-foreground)'} 
                      opacity={1 - (index * 0.08)}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon, trend, positive }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="bg-card border border-border rounded-2xl p-6 shadow-sm group transition-all"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="h-8 w-8 bg-muted/50 rounded-lg flex items-center justify-center text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">
          {icon}
        </div>
        <div className={`flex items-center gap-1 text-[10px] font-black uppercase tracking-wider ${positive ? 'text-emerald-500' : 'text-rose-500'}`}>
          {positive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
          {trend}
        </div>
      </div>
      <div>
        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground mb-1">{title}</h4>
        <p className="text-3xl font-black tracking-tighter text-foreground">{value}</p>
      </div>
    </motion.div>
  )
}
