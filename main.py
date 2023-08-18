import joblib
import pandas as pd
from fastapi import FastAPI, Body
from pydantic import BaseModel, ConfigDict, Field, PositiveInt, NonNegativeInt

from format import *
from model import inference

# Instantiate the app.
app = FastAPI(
    title="Census API",
    description="An API that classifies individuals into high salary (>50k) and low salary (<=50k) from Census Bureau data.",
    version="1.0.0",
)


############################################# Startup

# Load model
@app.on_event('startup')
async def load_model():
    app.model = joblib.load("model/rfc_model.pkl")


############################################# Endpoint 1

# Define a GET on the root endpoint.
@app.get("/")
async def say_hello():
    return {"greeting": "Hello World!"}


############################################# Endpoint 2


def hypenize(string: str) -> str:
    return string.replace("_", "-")


class Input(BaseModel):
    Body(model_config=ConfigDict(alias_generator=hypenize))

    class Config:
        use_enum_values = True

    age: PositiveInt
    workclass: Workclass
    fnlgt: PositiveInt
    education: Education
    education_num: PositiveInt = Field(alias="education-num")
    marital_status: Marital = Field(alias="marital-status")
    occupation: Occupation
    relationship: Relationship
    race: Race
    sex: Sex
    capital_gain: NonNegativeInt = Field(alias="capital-gain")
    capital_loss: NonNegativeInt = Field(alias="capital-loss")
    hours_per_week: NonNegativeInt = Field(alias="hours-per-week")
    native_country: Country = Field(alias="native-country")
    Body(
        examples=
        [
            {
                'age': 39,
                'workclass': 'State-gov',
                'fnlgt': 77516,
                'education': 'Bachelors',
                'education-num': 13,
                'marital-status': 'Never-married',
                'occupation': 'Adm-clerical',
                'relationship': 'Not-in-family',
                'race': 'White',
                'sex': 'Male',
                'capital-gain': 2174,
                'capital-loss': 0,
                'hours-per-week': 40,
                'native-country': 'United-States'
            }
        ]
    )


# Parameters which are not declared in the path are automatically query parameters
@app.post("/predict")
async def predict_from_data(data: Input):
    input = pd.DataFrame([data.dict()])
    input.columns = input.columns.str.replace("_", "-")
    return {"prediction": inference(app.model, input)}