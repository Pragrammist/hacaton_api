from pydantic import Field
from fastapi import Body, FastAPI, Query, Response
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi import status
from pydantic import BaseModel
from influxdb_client_3  import InfluxDBClient3, Point

client = InfluxDBClient3(token="my-super-secret-auth-token",
                         host="http://62.109.26.57:8086",
                         org="my-org",
                         database="my-bucket",
                         )

point = Point("measurement").tag("location", "london").field("temperature", 42)
client.write(point)


app = FastAPI()

class Person(BaseModel):
    name: str = Field(default="Undefined", min_length=3, max_length=20)
    age: int= Field(default=18, ge=18, lt=111)




@app.get("/msg/{text}", response_class=JSONResponse, status_code=status.HTTP_200_OK)
def root(response: Response,
    text:str, text2:str = Query(min_length=3)):
    if(text2 == None):
        response.status_code = 400;
        response.charset = "not inited" 
    return {"message": text, "mes3": text2}

@app.get("/old", response_class=RedirectResponse)


def redirect():
    point = Point("measurement").tag("location", "london").field("temperature", 42)
    client.write(point)
    client.query();
    return "/"

@app.get("/", response_class=FileResponse)
def public():
    return "public/index.html"

@app.post("/hello")
def hello(data = Body()):
    name = data["name"]
    age = data["age"]
    return {"message": f"{name}, ваш возраст - {age}"}