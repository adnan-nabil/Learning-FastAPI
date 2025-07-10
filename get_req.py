from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def data_load():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data


@app.get("/")
def hello():
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "This is a Patient Management System API built with FastAPI."}
    
@app.get("/view")
def view():    
    data = data_load()
    return data

@app.get("/patient/{patient_id}")
def call_by_id(patient_id: str = Path(..., description="The ID of the patient to retrieve", example ="P001")):
    
    data = data_load()
    
    for x, y in data.items():
        if x == patient_id:
            return y
        
    raise HTTPException(status_code=404, detail="Patient not found")
            

@app.get("/sorted_patient")
def func(sort_by: str = Query(..., description="sort by height, weight and bmi"), 
         order: str = Query("asc", description="sort order")):
    
    data = data_load()
    valid_fields = ["height", "weight", "bmi"]
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code = 400, detail=f"valid fields are: {valid_fields}") 
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code = 400, detail="invalid sort order. Use 'asc' or 'desc'")
    
    sorted_data = sorted(data.values(), 
                         key = lambda x: x.get(sort_by, 0),
                         reverse=True if order == "desc" else False
                         )  
    
    return sorted_data