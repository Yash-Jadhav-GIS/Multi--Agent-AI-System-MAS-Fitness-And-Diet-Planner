from fastapi import FastAPI
from app.routers import plan

app = FastAPI(title="Fitness & Diet Planner API", description="AI-powered fitness and diet planning backend")
app.include_router(plan.router)