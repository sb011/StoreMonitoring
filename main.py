from fastapi import FastAPI
from Routes.ReportRoutes import router as report_routes

app = FastAPI()
app.include_router(report_routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)