import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the app using import string
import uvicorn

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    uvicorn.run(
        "backend.main:app",  # Import string instead of app object
        host="0.0.0.0",
        port=8000,
        reload=True
    )