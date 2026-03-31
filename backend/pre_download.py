import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from backend.config import get_settings

def pre_download():
    settings = get_settings()
    model_name = settings.embedding_model
    
    # Define a local cache directory in the project root
    # This ensures the model is cached IN the build slug and preserved on Render
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_folder = os.path.join(base_dir, ".model_cache")
    os.makedirs(cache_folder, exist_ok=True)
    
    print(f"Pre-downloading SentenceTransformer model: {model_name}...")
    print(f"Using local cache folder: {cache_folder}")
    
    # This will download the model during build time
    try:
        model = SentenceTransformer(model_name, cache_folder=cache_folder)
        print("Successfully pre-downloaded and cached the model.")
    except Exception as e:
        print(f"Error pre-downloading model: {e}")
        # We don't want to fail the entire build just because of this, 
        # as it can still download at runtime if needed.
        sys.exit(0)

if __name__ == "__main__":
    pre_download()
