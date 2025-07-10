from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json
from fastapi.responses import JSONResponse


def data_loading():
    with open("patients.json", "r") as f:
        db = json.load(f)
    return db

def add_newdata(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)
 
app2 = FastAPI()    

class patient_data_validation(BaseModel):
    
    id: Annotated[str, Field(..., description="The ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient")]
    age: Annotated[int, Field(..., ge=0, description="The age of the patient")]
    gender: Annotated[Literal["male", "female", "other"], 
                        Field(..., description="gender of the patient")]
    city: Annotated[str, Field(..., description="current city")]
    height: Annotated[float, Field(..., gt=0, description="height in meters")]
    weight: Annotated[float, Field(..., gt=0, description="weight in kg")]


    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"






@app2.get("/")
def func():
    return {"message": "Patient Management System API"}

@app2.post("/create")
def func(x: patient_data_validation):
    data = data_loading()
    if x.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    data[x.id] = x.model_dump(exclude = ["id"])
    
    add_newdata(data)
    
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})
     