from fastapi import FastAPI

app = FastAPI(
    title="Campfire API",
    description="Ephemeral discussion API",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "The campfire is lit."}
