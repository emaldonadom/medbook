from fastapi import FastAPI

app = FastAPI(
    title="MedBook API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "MedBook API",
        "version": "1.0.0"
    }