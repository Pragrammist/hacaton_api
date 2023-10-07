from fastapi import FastAPI, WebSocket
import influxdb_client, os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from fastapi.middleware.cors import CORSMiddleware
import os



class DictObj:
    def __init__(self, in_dict: dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)

class ReadDataRepo:
    
    def __init__(self, client:InfluxDBClient, bucket:str, org:str):
        self.query_api = client.query_api()
        self.bucket = bucket
        self.org = org
    def read_temperature(self, timestamp):

        
        query = """from(bucket: "sensors")
        |> range(start: """ + timestamp + """)
        """
        tables = self.query_api.query(query, org=self.org)
        metricsData = self.__readTable(tables);
        return metricsData;
    def __readTable(self, tables):
        records = []
        for t in tables:
            record = t.records
            valuesAsDict = record[0].values
            my_obj = DictObj(valuesAsDict)
            records.append(my_obj)
        return record;









app = FastAPI()

originsEnvValue = os.getenv("ORIGIGINS", "*")


origins = originsEnvValue.split(";")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



token = os.getenv("INFLUX_TOKEN", "my-super-secret-auth-token") 
org = os.getenv("INFLUX_ORG", "my-org")
url = os.getenv("INFLUX_URL", "http://62.109.26.57:8086") 
bucket = os.getenv("INFLUX_BUCKET", "sensors")

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
repo = ReadDataRepo(client, bucket=bucket, org=org)

query_api = client.query_api()
write_api = client.write_api(write_options=SYNCHRONOUS)


@app.get("/api/get")
async def root(timestamp: str):
    return repo.read_temperature(timestamp)


@app.post("/api/set")
async def set_data(sensor_id: int, temperature: float, humidity: float):
    bucket = "sensors"
    point = (
        Point("temperature_sensor").tag("temperature", temperature).tag("humidity", humidity).field("id", sensor_id)
    )
    return write_api.write(bucket=bucket, org=org, record=point)


@app.websocket("/get/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        t = await websocket.receive_text()
        await websocket.send_json(repo.read_temperature(t))

