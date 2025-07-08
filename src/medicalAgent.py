from agents import Agent, Runner, set_tracing_disabled, function_tool, RunContextWrapper
from agents.extensions.models.litellm_model import LitellmModel
from dataclasses import dataclass
from pydantic import BaseModel
import os

set_tracing_disabled(disabled=True)

API_KEY = os.getenv("API_KEY")

@dataclass
class Profile:
  name: str
  age: int | float
  health_condition: str

@dataclass
class Diet:
  breakfast: str
  brunch: str
  lunch: str
  dinner: str
  before_sleep: str

@dataclass
class Illnesses:
  allergies_types: list[str]

@dataclass
class User_Data:
  profile: Profile
  diet: Diet
  illnesses: Illnesses


# Test data for Medical Assistant, Will remove it after setting up a database. 
user_data = Profile(
    name="Zulkifl", age=7.5, health_condition="CP Child"
)
user_diet = Diet(
    breakfast="Rice Flakes", brunch="Two boiled eggs", lunch="Boiled Apple", dinner="Fresh cooked Pumpkin", before_sleep="PediaSure Vanilla"
)
illnesses = Illnesses(
    allergies_types=["Wheat allergy", "Lactose intolerant", "Gluten intolerance" ,"Pollen Allergy"]
)


@function_tool
def get_user_data(context: RunContextWrapper) -> User_Data:
  return User_Data(profile=user_data, diet=user_diet, illnesses=illnesses)

Medical_Assistant = Agent[User_Data](
    name="Medical Assistant",
    instructions=f"You are an experienced Medical Assistant. After checking all the data of the user, provide personalized medical advice and answer health-related questions based on the provided {user_data}, {user_diet}, and {illnesses}. Ensure your advice is tailored to the user's age, health condition, diet, and known allergies. Always prioritize the user's safety and well-being. Do not provide a diagnosis or prescribe medication. If a question is outside your scope, advise the user to consult a medical professional.",
    model=LitellmModel(
        model="gemini/gemini-2.0-flash", 
        api_key=API_KEY
    ),
    tools=[get_user_data]
)

async def ask():
  result = await Runner.run(Medical_Assistant, "What preventive measures can be taken for my pollen allergies?")
  return result.final_output

# if __name__ == "__main__":
#   print(await ask())
