import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys

def pre_download():
    print("Pre-download step skipped: Using HuggingFace Inference API instead of local models.")

if __name__ == "__main__":
    pre_download()
