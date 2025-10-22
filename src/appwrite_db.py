from appwrite.query import Query
from appwrite.client import Client
from appwrite.services.databases import Databases
import os

APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")

client = Client()
client.set_endpoint("https://fra.cloud.appwrite.io/v1")  # or your self-hosted endpoint
client.set_project("684d8fd1002b5462c7ab")
client.set_key("APPWRITE_API_KEY")

db = Databases(client)
