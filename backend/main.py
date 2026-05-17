from fastapi import FastAPI

from database import Base, engine

from routers import auth_routes
from routers import user_routes
from routers import course_routes
from routers import assignment_routes
from routers import submission_routes
from routers import grade_routes
from routers import cache_routes
from routers import chat_routes


Base.metadata.create_all(bind=engine)

app = FastAPI(title="University LMS Lite API")


app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(course_routes.router)
app.include_router(assignment_routes.router)
app.include_router(submission_routes.router)
app.include_router(grade_routes.router)
app.include_router(cache_routes.router)
app.include_router(chat_routes.router)


@app.get("/")
def home():
    return {"message": "University LMS Lite API is running"}