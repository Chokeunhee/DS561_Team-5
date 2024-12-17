from openai import OpenAI
import openai
import json

######################################################
user_question = "목운 초등학교에서 가장 가까운 공원은 어디야?"
######################################################


def load_api_keys(config_file="config.text"):
    with open(config_file, "r") as file:
        config = json.load(file)
    return config

# API 키 로드
api_keys = load_api_keys()

# OpenAI API 키 설정
OPENAI_API_KEY = api_keys["openai_api_key"]

client = OpenAI(api_key=OPENAI_API_KEY)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content= user_question
)

run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id= 'asst_wZZWBR2jdIMNdEv3rdzKw5XC',
  instructions="You are a helpful assistant that provides detailed information about parks in Mokdong, such as their locations, facilities, operating hours, and activities."
)

if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  print(messages)
else:
  print(run.status)