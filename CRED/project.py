from fastapi import FastAPI, Path, HTTPException,Query,Body
from pydantic import BaseModel, Field,computed_field
from fastapi.responses import JSONResponse
from typing import Optional,Literal,Annotated
import csv

import json

app= FastAPI()
class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of the patient',examples=['P001'])]
    name:Annotated[str,Field(...,description='Name of the patient',examples=['yamuna'])]
    city:Annotated[str,Field(...,description='City where the patient belongs',examples=['Bangalore'])]
    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of a patient')]
    gender:Annotated[Literal['male',"female","others"],Field(...,description='Gender of the patient')]
    height:Annotated[float,Field(...,gt=0,description='Height of the patient in cm')]
    weight:Annotated[float,Field(...,gt=0,description='Height of the patient in kgs')]

    @computed_field
    def bmi(self) -> float:
        h_m = self.height / 100
        return round(self.weight / (h_m ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
class PatientUpdate(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None)]
    gender:Annotated[Optional[Literal['male','female']],Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

@app.get("/")
def webpage():
    return {"message":"Patient Mangement System API"}

@app.get("/about")
def about():
    return {"message":"A fully function ApI to mange patient records"}

def load_data():
    with open("patients.json","r") as f:
        data= json.load(f)
    return data

@app.get("/view")
def view():
    data= load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str= Path(...,description="Id of the patient in the db",examples="P001")):
    #load all the patients
    data= load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="patient not found")
      
def save_data(data):
    with open("patients.json","w") as f:
        json.dump(data,f)

@app.post("/create")
def create_patient(patient:Patient):
    data=load_data()
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient already exist")
    
    data[patient.id]=patient.model_dump(exclude="id")
    save_data(data)

    return JSONResponse(status_code=200, content={"message":f"{patient.id} patient data add successfully"})

@app.put("/patient/{patient_id}")
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate = Body(...)
):
    # load all the patients
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing_patient_info = data[patient_id]

    # only update fields sent by user
    updated_patient_info = patient_update.model_dump(exclude_unset=True) # Only include the fields the user actually sent. Ignore everything they didn’t provide.

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    # validate with main Patient schema
    existing_patient_info["id"] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)

    # remove id before saving
    data[patient_id] = patient_pydantic_obj.model_dump(exclude={"id"})
    save_data(data)

    return {"message": "Patient updated successfully"}


@app.delete("/patient/{patient_id}")
def delete_patient(  patient_id: str):
    data= load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)
    return JSONResponse(status_code=200, content={'message':'patient deleted'})


@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    # load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False
    print(sort_order)

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    return sorted_data


# update the particular data based on id
@app.put("/patient_id/{patient_id}")
def update_field_values(
    patient_id: str,
    update_by: str = Query(..., description="Field name to update"),
    value: str = Query(..., description="New value for the field"),   
   ):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    keys = Patient.model_fields.keys()
    if update_by not in keys:
        raise HTTPException(status_code=400,detail=f"Invalid field. Choose from {list(keys)}")
    
    existing_patient_info = data[patient_id]
    # Finds the expected data type of that field age:int, height:in
    field_type = Patient.model_fields[update_by].annotation

    try:
        # Converts the query string into the correct type.
        cast_value = field_type(value)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value type for {update_by}. Expected {field_type}"
        )
    
    existing_patient_info[update_by] = cast_value
    existing_patient_info["id"] = patient_id

    # Re-checks everything using Pydantic rules.
    validated = Patient(**existing_patient_info)

    # Saves back without duplicating ID.
    data[patient_id] = validated.model_dump(exclude={"id"})
    save_data(data)

    return {"message": f"{update_by} updated to {cast_value}"}


# Search api based on city, name, age,gender (filter the data)
@app.get("/search")
def filter_data(
    city: Optional[str] = Query(None),       # keep the parameter optional according to your search
    name: Optional[str] = Query(None),
    age: Optional[int] = Query(None),
    gender: Optional[str] = Query(None)
):
    data= load_data().values()

    if city:
        data = [p for p in data if p["city"].lower() == city.lower().strip()]

    if name:
        data = [p for p in data if p["name"].lower()== name.lower().strip() or name.lower().strip() in p["name"].lower()]

    if age:
        data = [p for p in data if p["age"] == age]
        print(data)

    if gender:
        data = [p for p in data if p["gender"] == gender.strip()]
        print(data)

    return list(data)


@app.get("/stats")
def stats():
    data = load_data().values()
    ages = [p["age"] for p in data]
    return {
        "total_patients": len(ages),
        "avg_age": round(sum(ages)/len(ages),2),
        "max_age": max(ages),
        "min_age": min(ages)
    }


@app.get("/export")
def export():
    data = list(load_data().values())
    if not data:
        return {"message": "No data to export"}
    with open("patients.csv","w",newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return {"message":"Exported to patients.csv"}
