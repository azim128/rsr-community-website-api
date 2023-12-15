from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def home():
    return {
        "status_code": 200,
        "message": "This is an api for RSR website. To know detail about the api call contact azimruet28@gmail.com and mridul.mte@gmail.com"
    }


@app.get("/health")
def check_api_health():
    return {"status_code": 200,
            "message": "API works fine."}
