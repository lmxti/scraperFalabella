from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BRAVE_PATH = os.getenv("BRAVE_PATH")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
DATABASE_URL_PG = os.getenv("DATABASE_URL_PG")

