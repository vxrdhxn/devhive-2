import { login, signup } from "./actions"

export default async function LoginPage(props: { searchParams: Promise<{ message: string }> }) {
  const searchParams = await props.searchParams

  return (
    <div className="flex-1 flex flex-col w-full px-8 sm:max-w-md justify-center gap-2 m-auto mt-32">
      <form className="animate-in flex-1 flex flex-col w-full justify-center gap-6 text-foreground">
        <div className="space-y-2 mb-4">
           <h1 className="text-4xl font-black tracking-tighter text-center uppercase">DevHive</h1>
           <p className="text-[10px] font-bold text-muted text-center uppercase tracking-[0.4em]">Enterprise Access Portal</p>
        </div>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted ml-1" htmlFor="email">
              Identity
            </label>
            <input
              className="w-full rounded-xl px-5 py-4 bg-card border border-border focus:border-foreground focus:ring-0 focus:outline-none transition-all font-bold text-sm"
              name="email"
              placeholder="e.g. director@devhive.ai"
              required
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-[10px] font-black uppercase tracking-widest text-muted ml-1" htmlFor="password">
              Protocol Key
            </label>
            <input
              className="w-full rounded-xl px-5 py-4 bg-card border border-border focus:border-foreground focus:ring-0 focus:outline-none transition-all font-bold text-sm"
              type="password"
              name="password"
              placeholder="••••••••"
              required
            />
          </div>
        </div>

        <div className="flex flex-col gap-3 pt-4">
          <button
            formAction={login}
            className="bg-foreground text-background font-black rounded-xl px-4 py-4 uppercase tracking-[0.2em] text-xs hover:opacity-90 transition-opacity"
          >
            Authenticate
          </button>
          <button
            formAction={signup}
            className="border border-border text-foreground font-black rounded-xl px-4 py-4 uppercase tracking-[0.2em] text-xs hover:bg-foreground hover:text-background transition-all"
          >
            Request Access
          </button>
        </div>

        {searchParams?.message && (
          <p className="mt-4 p-4 border border-red-500/20 bg-red-500/5 text-red-500 text-center rounded-xl text-[10px] font-bold uppercase tracking-widest">
            {searchParams.message}
          </p>
        )}
      </form>
    </div>
  )
}
