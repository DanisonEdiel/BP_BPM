from fastapi import FastAPI
from routes.ocr_routes import router as ocr_router

app = FastAPI(title="OCR + Gemini API")

app.include_router(ocr_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9008, reload=True)
