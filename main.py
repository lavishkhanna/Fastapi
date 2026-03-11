from fastapi import FastAPI, HTTPException,Path,Query
import json
import requests

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