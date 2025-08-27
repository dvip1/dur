# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",   # points to app object inside app/main.py
        host="127.0.0.1",
        port=8000,
        reload=True       # auto-reload on code change
    )
