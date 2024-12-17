from openai import OpenAI
import openai
import pandas as pd
import re

api_key = ""

assistant_id = 'asst_wZZWBR2jdIMNdEv3rdzKw5XC'



def query_openai_assistant(api_key, user_question, assistant_id):
    # Initialize OpenAI client
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        
        # Create a user message in the thread
        print("creating client")
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_question
        )
        
        # Run the assistant with the given instructions
        print("Run assistant")
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=(
                "You are a helpful assistant that provides detailed information "
                "about parks in Mokdong, such as their locations, facilities, "
                "operating hours, and activities."
            )
        )
        
        # Return messages if the run is completed
        if run.status == 'completed':
            print("run complet")
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            #value = next((message.content[0].text.value for message in messages.data if message.role == 'assistant'),None)
            value = next((re.sub(r'【.*?†source】', '', message.content[0].text.value).strip() for message in messages.data if message.role == 'assistant' and message.content),None)
            print(value)
            return value
        else:
            return {"status": run.status}
    
    except Exception as e:
        return {"error": str(e)}
    
### main ###a
input_csv_path = "/Users/chokeunhee/Desktop/vscode/qa_questions_output.csv"
output_csv_path = "/Users/chokeunhee/Desktop/vscode/qa_questions_output_with_model_answer.csv"

# CSV 파일 읽기
df = pd.read_csv(input_csv_path)

# 'Model' 컬럼이 없으면 생성
if 'Model' not in df.columns:
    df['Model'] = ''

# 데이터프레임을 리스트로 변환하여 작업
questions = df['Question'].tolist()
responses = []

for index, question in enumerate(questions):
    print(f"Processing question {index + 1}/{len(questions)}: {question}")
    response = query_openai_assistant(api_key, question, assistant_id)
    responses.append(response)

# 결과를 데이터프레임에 추가
df['Model'] = responses

# 결과를 새로운 CSV 파일로 저장
df.to_csv(output_csv_path, index=False, encoding="utf-8")
print(f"Responses saved to {output_csv_path}")