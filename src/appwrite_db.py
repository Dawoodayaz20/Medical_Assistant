from appwrite.query import Query
from appwrite.client import Client
from appwrite.services.databases import Databases
from dotenv import load_dotenv, find_dotenv 
import os

load_dotenv(find_dotenv())

APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")

client = Client()
client.set_endpoint("https://fra.cloud.appwrite.io/v1")  # or your self-hosted endpoint
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)

db = Databases(client)
