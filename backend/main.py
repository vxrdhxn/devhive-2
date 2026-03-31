import sys
import os
import traceback

# 0. Startup Checkpoint & Environment Setup
# Force unbuffered output for Render logs
os.environ["PYTHONUNBUFFERED"] = "1"
os.environ["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*50)
print("🚀 [BOOT] KTP Backend API initialization starting...")
print(f"📁 [BOOT] Current Working Directory: {os.getcwd()}")
print(f"📁 [BOOT] Added to PYTHONPATH: {os.environ['PYTHONPATH']}")
print("="*50 + "\n")

try:
    # 1. Path manipulation BEFORE anything else
    root_dir = os.environ["PYTHONPATH"]
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir) # Use insert(0) for priority
        print(f"✅ [BOOT] Added {root_dir} to sys.path at position 0")

    from fastapi import FastAPI, Depends
    from fastapi.middleware.cors import CORSMiddleware
    print("✅ [BOOT] Core FastAPI modules loaded")
    
    from backend.auth.dependencies import get_current_user
    try:
        from gotrue import User
    except ImportError:
        from gotrue.types import User
    print("✅ [BOOT] Auth dependencies loaded")

    # 2. Set Model Cache Environment Variables (Crucial for Render persistence)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_cache = os.path.join(base_dir, ".model_cache")
    os.makedirs(model_cache, exist_ok=True)
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = model_cache
    os.environ["TRANSFORMERS_CACHE"] = model_cache
    print(f"✅ [BOOT] Model cache path configured: {model_cache}")

    # 3. Import routers individually with logging to pinpoint hangs
    import backend.routers.documents as documents
    
    from backend.routers import search
    
    from backend.routers import integrations

    from backend.config import get_settings
    print("✅ [BOOT] Configuration loaded")

except Exception as e:
    print("\n❌ [CRITICAL] Backend failed to initialize!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\n[TRACEBACK]")
    traceback.print_exc()
    print("\n" + "="*50 + "\n")
    # We raise it again after logging so uvicorn knows we've failed
    raise e

settings = get_settings()
app = FastAPI(title="KTP Backend API")
print("✅ [BOOT] FastAPI application instance created")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(search.router)
app.include_router(integrations.router)

@app.get("/")
async def root():
    return {"message": "KTP Backend API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/me")
async def read_users_me(user: User = Depends(get_current_user)):
    """
    Protected endpoint to test Supabase JWT validation.
    Returns the current authenticated user's email.
    """
    return {"email": user.email, "id": user.id, "metadata": user.app_metadata}


