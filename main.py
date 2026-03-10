from fastapi import FastAPI
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
@app.get('/patient/{patient_id}')
def get_patient(patient_id:str):
    data = load_data()

    if patient_id in data:
         print(f"Patient found {patient_id}")
         return {"patient_id":patient_id, "data":data[patient_id]}
    return {"error":"Patient not found"}