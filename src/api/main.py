from fastapi import FastAPI, Request
import uvicorn
from src.api.routes import data_routes, paper_routes, user_routes, extensions_routes
from src.core.i18n.translator import translator

# Create FastAPI app
app = FastAPI(
    title="4D-Paper API",
    description="API for Dynamic 4D Academic Paper System",
    version="1.0.0"
)

# Language middleware
@app.middleware("http")
async def language_middleware(request: Request, call_next):
    """Language detection middleware"""
    # Get language from request header
    accept_language = request.headers.get('Accept-Language', 'en')
    language = accept_language.split(',')[0].split(';')[0].split('-')[0]
    translator.set_language(language)
    
    # Continue processing request
    response = await call_next(request)
    return response

# Register routes
app.include_router(data_routes.router, prefix="/api/data", tags=["Data Management"])
app.include_router(paper_routes.router, prefix="/api/papers", tags=["Paper Management"])
app.include_router(user_routes.router, prefix="/api/users", tags=["User Management"])
app.include_router(extensions_routes.router, prefix="/api/extensions", tags=["Extensions"])

# Root endpoint
@app.get("/")
async def root():
    from src.core.i18n.translator import _
    return {
        "message": _("Welcome to 4D-Paper API"),
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Run the app if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )