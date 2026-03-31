"use client"

import { Sun, Moon } from "lucide-react"
import { useTheme } from "./ThemeProvider"
import { useEffect, useState } from "react"
import { motion } from "framer-motion"

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return <div className="h-9 w-9" />

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={toggleTheme}
      className="p-2.5 rounded-full border border-border bg-card text-foreground hover:bg-muted/10 transition-all flex items-center justify-center shadow-sm"
      aria-label="Toggle theme"
    >
      {theme === "light" ? (
        <Moon className="h-4 w-4" />
      ) : (
        <Sun className="h-4 w-4 text-yellow-400" />
      )}
    </motion.button>
  )
}
