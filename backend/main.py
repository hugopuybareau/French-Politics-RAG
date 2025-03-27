# backend/app/main.py

import uvicorn
import logging

from chat.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

