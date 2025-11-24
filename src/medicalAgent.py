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
  name: str
  age: str
  gender: str

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

@function_tool
def get_user_reminders(userId: str):
    """Fetch user's reminders."""
    try:
        result = db.list_documents(
            DOC_ID, 
            "reminders",
            [Query.equal("userID", userId)]
            )
        return result["documents"]
    except Exception as e:
        print(f"There was an error calling the tool:{e}")

@function_tool
def get_user_medicines(userId: str):
    """Fetch user's medicines."""
    try:
        result = db.list_documents(
            DOC_ID, 
            "medicines",
            [Query.equal("userID", userId)]
            )
        return result["documents"]
    except Exception as e:
        print(f"There was an error calling the tool:{e}")

async def kickoff(question: str, userID: str):

  try:
    response = db.list_documents(
            collection_id="users",
            database_id=DOC_ID,
            queries=[Query.equal("userID", userID)]
            )
    
    if response['total'] > 0:
      doc = response['documents'][0]
      user_data = UserData(
        userId=userID,
        name=doc['name'],
        gender=doc['gender'],
        age=doc['age']
        )
    else:
      user_data = None
    
    Medical_Assistant: Agent = Agent[user_data](
    name="Medical Assistant",
    instructions=f"You are a Medical Assistant. Your role is to help users manage their health by using the tools and user data available to you.
                   Use the provided user data '{user_data}' and tools to access the user’s medical records, medicines, and health data.
                   Give personalized, context-aware assistance based on the user’s data.
                   Provide general health guidance such as diet tips, daily routines, wellness practices, and lifestyle recommendations tailored to the user’s medical profile.
                   Help users understand their medical information in simple terms.
                   Always rely on the available tools whenever medical data, records, or user-specific info is needed.
                   Never assume missing information—query the tool instead.
                   Only answer using information you have; if something is unknown, say so",
    model=model,
    tools=[get_user_notes, get_user_reminders, get_user_medicines]
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
