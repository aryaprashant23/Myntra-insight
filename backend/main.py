from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Myntra Wishlist Hesitation API",
    description="Backend for collecting, processing, and analyzing comments",
    version="1.0.0"
)

# CORS config to allow the frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change this to the Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Myntra Wishlist Hesitation API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # For local development
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
