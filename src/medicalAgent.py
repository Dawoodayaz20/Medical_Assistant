from agents import Agent, Runner, function_tool, RunContextWrapper, RunHooks, AgentHooks, set_tracing_disabled, AsyncOpenAI, RunConfig, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import os, asyncio
# from agents import Agent, Runner, set_tracing_disabled, function_tool, RunContextWrapper
# from agents.extensions.models.litellm_model import LitellmModel
# from dataclasses import dataclass
# from pydantic import BaseModel
# import os

# set_tracing_disabled(disabled=True)

# API_KEY = os.getenv("API_KEY")

# @dataclass
# class Profile:
#   name: str
#   age: int | float
#   health_condition: str

# @dataclass
# class Diet:
#   breakfast: str
#   brunch: str
#   lunch: str
#   dinner: str
#   before_sleep: str

# @dataclass
# class Illnesses:
#   allergies_types: list[str]

# @dataclass
# class User_Data:
#   profile: Profile
#   diet: Diet
#   illnesses: Illnesses


# # Test data for Medical Assistant, Will remove it after setting up a database. 
# user_data = Profile(
#     name="Zulkifl", age=7.5, health_condition="CP Child"
# )
# user_diet = Diet(
#     breakfast="Rice Flakes", brunch="Two boiled eggs", lunch="Boiled Apple", dinner="Fresh cooked Pumpkin", before_sleep="PediaSure Vanilla"
# )
# illnesses = Illnesses(
#     allergies_types=["Wheat allergy", "Lactose intolerant", "Gluten intolerance" ,"Pollen Allergy"]
# )


# @function_tool
# def get_user_data(context: RunContextWrapper) -> User_Data:
#   return User_Data(profile=user_data, diet=user_diet, illnesses=illnesses)

# Medical_Assistant = Agent[User_Data](
#     name="Medical Assistant",
#     instructions=f"You are an experienced Medical Assistant. After checking all the data of the user, provide personalized medical advice and answer health-related questions based on the provided {user_data}, {user_diet}, and {illnesses}. Ensure your advice is tailored to the user's age, health condition, diet, and known allergies. Always prioritize the user's safety and well-being. Do not provide a diagnosis or prescribe medication. If a question is outside your scope, advise the user to consult a medical professional.",
#     model=LitellmModel(
#         model="gemini/gemini-1.5-flash", 
#         api_key=API_KEY
#     ),
#     tools=[get_user_data]
# )

# async def ask(question: str):
#   result = await Runner.run(Medical_Assistant, question)
#   return result.final_output

# # if __name__ == "__main__":
# #   print(await ask())

API_KEY = os.getenv("API_KEY")

MCP_SERVER_URL = "http://localhost:8000/mcp/"

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

# user_data = Profile(name="Zulkifl", age=7.5, health_condition="CP Child")
# user_diet = Diet(breakfast="Rice Flakes", brunch="Two boiled eggs", lunch="Boiled Apple", dinner="Fresh cooked Pumpkin", before_sleep="PediaSure Vanilla")
# illnesses = Illnesses(allergies_types=["Wheat allergy", "Lactose intolerant", "Gluten intolerance" ,"Pollen Allergy"])

async def kickoff(question: str, userID: str):
    load_dotenv(find_dotenv())
    user_data = UserData(userId=userID)
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)

    async with MCPServerStreamableHttp(params=mcp_params, name="MCPServerClient") as mcp_server_client:
        try:
            Medical_Assistant: Agent = Agent[user_data](
                name="Medical Assistant",
                instructions=f"You are an experienced Medical Assistant. By using {user_data} to access the database, assist the users.",
                model=model,
                mcp_servers=[mcp_server_client]
            )

            print(f"Agent '{Medical_Assistant.name}' initialized with MCP server: '{mcp_server_client.name}'.")

            result = await Runner.run(
                Medical_Assistant,
                question,
                context=user_data,
                run_config=config
            )

            # Close any remaining async tasks before exit
            await mcp_server_client.aclose()
            print(result.final_output)
            return result.final_output

        except Exception as e:
            print(f"There was an error connecting the Server: {e}")
            return {"error": str(e)}


# ". After checking all the data of the user, provide personalized medical advice and answer health-related questions based on the provided {user_data}, {user_diet}, and {illnesses}. Ensure your advice is tailored to the user's age, health condition, diet, and known allergies. Always prioritize the user's safety and well-being. Do not provide a diagnosis or prescribe medication. If a question is outside your scope, advise the user to consult a medical professional."
