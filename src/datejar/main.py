from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to DateJar Mike!"}


@app.get("/healthz")
def health_check():
    return {"status": "healthy"}