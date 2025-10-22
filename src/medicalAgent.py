from agents import Agent, Runner, function_tool, RunContextWrapper, RunHooks, AgentHooks, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
from src.appwrite_db import db
from appwrite.query import Query
import os

load_dotenv(find_dotenv())
set_tracing_disabled(disabled=True)

API_KEY = os.getenv("API_KEY")
DOC_ID = os.getenv("APPWRITE_DOC_ID")

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

@dataclass
class UserData:
  userId : str

@function_tool
def get_user_notes(userId: str):
    """Fetch user's medical notes from Appwrite."""
    try:
        result = db.list_documents(
            DOC_ID, 
            "medical_notes",
            [Query.equal("userId", userId)]
            )
        return result["documents"]
    except Exception as e:
        print(f"There was an error calling the tool:{e}")

# user_data = Profile(name="Zulkifl", age=7.5, health_condition="CP Child")
# user_diet = Diet(breakfast="Rice Flakes", brunch="Two boiled eggs", lunch="Boiled Apple", dinner="Fresh cooked Pumpkin", before_sleep="PediaSure Vanilla")
# illnesses = Illnesses(allergies_types=["Wheat allergy", "Lactose intolerant", "Gluten intolerance" ,"Pollen Allergy"])
async def kickoff(question: str, userID: str):

  user_data = UserData(userId = userID)

  try:
    Medical_Assistant: Agent = Agent[user_data](
    name="Medical Assistant",
    instructions=f"You are an experienced Medical Assistant. By using the {user_data} provided in the context, assist the users.",
    model=model,
    tools=[get_user_notes]
    )

    result = await Runner.run(
      Medical_Assistant, 
      question,
      context=user_data,
      run_config=config
    )
    print(result.final_output)
    return result.final_output
  except Exception as e:
      print(f"There was an error connecting the Server:{e}")

# ". After checking all the data of the user, provide personalized medical advice and answer health-related questions based on the provided {user_data}, {user_diet}, and {illnesses}. Ensure your advice is tailored to the user's age, health condition, diet, and known allergies. Always prioritize the user's safety and well-being. Do not provide a diagnosis or prescribe medication. If a question is outside your scope, advise the user to consult a medical professional."
