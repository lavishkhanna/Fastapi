from fastapi import FastAPI, HTTPException,Path,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, computed_field, Field
from typing import Annotated, Literal, Optional
import json
import requests

class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
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
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]



app=FastAPI()

#skeleton apis
@app.get('/')
def home():
    return {"message":"Hello World"}

@app.get('/about')
def about():
    return {"message":"About Us"}


#path params

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=4)

# we pass param in url and we can access it in function, we must specify the type of param in function, here we are passing patient_id as string, this is specified in the arguments of function

# we are also using HTTPExecption here so that we can raise errors rather than just returning a json response, this is a better way to handle errors in fastapi, we can also specify the status code of the error, here we are using 404 for not found error


#path params
@app.get('/patient/{patient_id}')
def get_patient(patient_id:str=Path(..., description="The ID of the patient to retrieve",example="P001")):
    data = load_data()

    if patient_id in data:
         print(f"Patient found {patient_id}")
         return {"patient_id":patient_id, "data":data[patient_id]}
    # return {"error":"Patient not found"}
    raise HTTPException(status_code=404, detail="Patient not found")



# Query params => we can pass query params in the url after ? and we can access it in function, we must specify the type of param in function, here we are passing sort_by and order as string, this is specified in the arguments of function, we can also specify default values for query params, here we are setting default value of order as 'asc', if user does not provide any value for order then it will take 'asc' as default value


@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='Sort on the basis of height, weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail='Invalid order select between asc and desc')
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data


# difference between path params and query params is that path params are used to identify a specific resource and query params are used to filter or sort the data, path params are mandatory and query params are optional, path params are defined in the url and query params are passed after ? in the url, path params are accessed in function using Path and query params are accessed in function using Query.
#path params are used to identify a specific resource and query params are used to filter or sort the data, path params are mandatory and query params are optional, path params are defined in the url and query params are passed after ? in the url, path params are accessed in function using Path and query params are accessed in function using Query.


# POST API
@app.post('/create-patient')
def create_patient(patient:Patient):

    data=load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient with this ID already exists')
    
    data[patient.id] = patient.model_dump(exclude=['id'])
    save_data(data)
    return JSONResponse(content={"message": "Patient created successfully", "patient_id": patient.id}, status_code=201)



# PUT AND DELETE API


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})