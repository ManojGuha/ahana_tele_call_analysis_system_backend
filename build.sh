   #!/usr/bin/env bash
   
   # Exit on error
   set -e
   
   # Install dependencies with specific flags
   pip install -U pip
   pip install --no-cache-dir -r requirements.txt
