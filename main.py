from fastapi import FastAPI
from routes.report_routes import router as report_routes

app = FastAPI()
app.include_router(report_routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)