from fastapi import FastAPI
import requests

app=FastAPI()

@app.get('/')
def home():
    return {"message":"Hello World"}

@app.get('/about')
def about():
    return {"message":"About Us"}