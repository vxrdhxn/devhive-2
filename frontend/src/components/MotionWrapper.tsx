"use client"

import { motion } from "framer-motion"
import { ReactNode } from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

// Utility function to merge tailwind classes safely (since we installed clsx and tailwind-merge)
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function MotionWrapper({ 
  children, 
  className,
  delay = 0 
}: { 
  children: ReactNode, 
  className?: string,
  delay?: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.5, 
        ease: [0.16, 1, 0.3, 1], // Custom apple-like ease out
        delay: delay 
      }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  )
}
