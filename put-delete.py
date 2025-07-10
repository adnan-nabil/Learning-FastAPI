from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, computed_field
from fastapi.responses import JSONResponse
from typing import Annotated, Literal, Optional
import json


def data_loading():
    with open("patients.json", "r") as f:
        db = json.load(f)
        
    return db


def add_newdata(db):
    with open("patients.json", "w") as f:
        json.dump(db, f, indent=4)


app3 = FastAPI()

class update_data_validation(BaseModel):
    
    name: Annotated[Optional[str], Field(None, description="The name of the patient")]
    age: Annotated[Optional[int], Field(None, ge=0, description="The age of the patient")]
    gender: Annotated[Optional[Literal["male", "female", "other"]], 
                        Field(None, description="gender of the patient")]
    city: Annotated[Optional[str], Field(None, description="current city")]
    height: Annotated[Optional[float], Field(None, gt=0)]
    weight: Annotated[Optional[float], Field(None, gt=0)]


    @computed_field
    @property
    def bmi(self) -> Optional[float]:
        if self.height is None or self.weight is None:
            return None
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> Optional[str]:
        if self.bmi is None:
            return None
        
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
        


@app3.put("/edit/{pid}")
def update_pat_data(pid: str, d: update_data_validation):
    db = data_loading()
    if pid not in db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_info = db[pid]
    updated_info = d.model_dump(exclude_unset=True)
    
    for key, value in updated_info.items():
        existing_info[key] = value
    
    # now: old_data updated -> make pydantic object -> so generate new bmi+verdict -> make dict from pydantic object
    
    existing_info["id"] = pid # though this was not id 
    new_pydantic_object = update_data_validation(**existing_info) # make pydantic object
    
    existing_info = new_pydantic_object.model_dump(exclude="id") # make dict from pydantic object
    db[pid] = existing_info # now update to db   
    
    add_newdata(db) # write to file   
    
    return JSONResponse(status_code=200, content = "successfully updated patient data")




@app3.delete("/delete/{pid}")
def delete_patient_data(pid: str):
    db = data_loading()
    if pid not in db:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del db[pid]
    
    add_newdata(db)
    
    return JSONResponse(status_code=200, content="successfully deleted patient information")