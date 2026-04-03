"use client"

import { useEffect, useState } from 'react'
import { Command } from 'cmdk'
import { Search, FileText, Settings, Moon, Sun, Link, Database, Zap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export function CommandMenu() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      // Toggle on Cmd/Ctrl + K
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  return (
    <>
      {/* Global Button override (optional, just to show it globally) */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 bg-slate-900/30 backdrop-blur-sm flex items-start justify-center pt-[15vh] px-4"
            onClick={() => setOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.95, y: -10, opacity: 0, filter: "blur(4px)" }}
              animate={{ scale: 1, y: 0, opacity: 1, filter: "blur(0px)" }}
              exit={{ scale: 0.95, y: -10, opacity: 0, filter: "blur(4px)" }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-2xl bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-slate-200/60 ring-1 ring-black/5"
            >
              {/* Note: we use cmdk native styling logic combined with tailwind */}
              <Command className="flex flex-col h-full max-h-[450px]">
                <div className="flex items-center border-b border-slate-200/60 px-5">
                  <Search className="h-5 w-5 text-indigo-500 shrink-0 mr-3" />
                  <Command.Input 
                    autoFocus
                    placeholder="Search documents, actions, or settings..." 
                    className="flex-1 h-16 bg-transparent outline-none text-slate-800 placeholder:text-slate-400 font-medium text-lg" 
                  />
                  <div className="flex gap-1 ml-4">
                    <kbd className="bg-slate-100 text-slate-400 text-[10px] uppercase font-bold px-1.5 py-0.5 rounded border border-slate-200">esc</kbd>
                  </div>
                </div>

                <Command.List className="overflow-y-auto p-2 custom-scrollbar">
                  <Command.Empty className="py-12 text-center flex flex-col items-center justify-center">
                    <Zap className="h-8 w-8 text-slate-300 mb-2" />
                    <p className="text-sm font-medium text-slate-500">No results found.</p>
                  </Command.Empty>

                  {/* Tailwind classes for cmdk items: We map them via global or explicit children */}
                  <Command.Group heading="Knowledge Actions" className="p-2 py-3 [&>[cmdk-group-heading]]:text-xs [&>[cmdk-group-heading]]:font-bold [&>[cmdk-group-heading]]:text-slate-400 [&>[cmdk-group-heading]]:uppercase [&>[cmdk-group-heading]]:tracking-wider [&>[cmdk-group-heading]]:px-3 [&>[cmdk-group-heading]]:mb-2">
                    <Command.Item 
                      onSelect={() => setOpen(false)}
                      className="flex items-center px-4 py-3 rounded-xl hover:bg-slate-100 cursor-pointer text-sm text-slate-700 font-medium aria-selected:bg-indigo-50 aria-selected:text-indigo-700 transition"
                    >
                      <FileText className="mr-3 h-4 w-4 text-indigo-500 shrink-0" />
                      Upload a New Document
                    </Command.Item>
                    <Command.Item 
                      onSelect={() => setOpen(false)}
                      className="flex items-center px-4 py-3 rounded-xl hover:bg-slate-100 cursor-pointer text-sm text-slate-700 font-medium aria-selected:bg-emerald-50 aria-selected:text-emerald-700 transition"
                    >
                      <Database className="mr-3 h-4 w-4 text-emerald-500 shrink-0" />
                      Browse pgvector Database
                    </Command.Item>
                    <Command.Item 
                      onSelect={() => {
                        setOpen(false)
                        window.location.href = '/analytics'
                      }}
                      className="flex items-center px-4 py-3 rounded-xl hover:bg-slate-100 cursor-pointer text-sm text-slate-700 font-medium aria-selected:bg-indigo-50 aria-selected:text-indigo-700 transition"
                    >
                      <Zap className="mr-3 h-4 w-4 text-indigo-500 shrink-0" />
                      View System Analytics
                    </Command.Item>
                  </Command.Group>

                  <Command.Separator className="h-px bg-slate-100 mx-2 my-1" />

                  <Command.Group heading="Preferences" className="p-2 py-3 [&>[cmdk-group-heading]]:text-xs [&>[cmdk-group-heading]]:font-bold [&>[cmdk-group-heading]]:text-slate-400 [&>[cmdk-group-heading]]:uppercase [&>[cmdk-group-heading]]:tracking-wider [&>[cmdk-group-heading]]:px-3 [&>[cmdk-group-heading]]:mb-2">
                    <Command.Item 
                      onSelect={() => setOpen(false)}
                      className="flex items-center px-4 py-3 rounded-xl hover:bg-slate-100 cursor-pointer text-sm text-slate-700 font-medium aria-selected:bg-slate-100 transition"
                    >
                      <Moon className="mr-3 h-4 w-4 text-slate-500 shrink-0" />
                      Switch to Dark Mode
                    </Command.Item>
                    <Command.Item 
                      onSelect={() => setOpen(false)}
                      className="flex items-center px-4 py-3 rounded-xl hover:bg-slate-100 cursor-pointer text-sm text-slate-700 font-medium aria-selected:bg-slate-100 transition"
                    >
                      <Link className="mr-3 h-4 w-4 text-orange-500 shrink-0" />
                      Manage External API Connectors
                    </Command.Item>
                    <Command.Item 
                      onSelect={() => setOpen(false)}
                      className="flex items-center px-4 py-3 rounded-xl hover:bg-slate-100 cursor-pointer text-sm text-slate-700 font-medium aria-selected:bg-slate-100 transition"
                    >
                      <Settings className="mr-3 h-4 w-4 text-slate-500 shrink-0" />
                      System Settings
                    </Command.Item>
                  </Command.Group>
                </Command.List>
              </Command>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
