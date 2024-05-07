from fastapi import FastAPI
from pydantic import BaseModel

class Testrequest(BaseModel):
    id: int

app = FastAPI()

@app.get('/health/', status_code=200)
async def healthcheck():
    return {
        'serviceStatus': 'OK',
        'message': "Have a good time"
    }

if __name__ == '__main__':

    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)