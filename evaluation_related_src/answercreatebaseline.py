from openai import OpenAI
import openai
import pandas as pd

api_key = ""

model = "gpt-4o-mini-2024-07-18"

def query_openai_baseline(api_key, user_question):
    client = openai.OpenAI(api_key=api_key)
    chat = client.chat.completions.create(
        model = "gpt-4o-mini-2024-07-18",
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': user_question}],
    )
    messages = chat.choices[0].message.content.strip()
    print(messages)
    return messages

    
### main ###a
input_csv_path = "/Users/chokeunhee/Desktop/vscode/qa_questions_output_with_model_answer.csv"
output_csv_path = "/Users/chokeunhee/Desktop/vscode/qa_questions_output_with_both_answer.csv"

# CSV 파일 읽기
df = pd.read_csv(input_csv_path)

# 'Baseline' 컬럼이 없으면 생성
if 'Baseline' not in df.columns:
    df['Baseline'] = ''

# 데이터프레임을 리스트로 변환하여 작업
questions = df['Question'].tolist()
responses = []

for index, question in enumerate(questions):
    print(f"Processing question {index + 1}/{len(questions)}: {question}")
    response = query_openai_baseline(api_key,question)
    responses.append(response)

# 결과를 데이터프레임에 추가
df['Baseline'] = responses

# 결과를 새로운 CSV 파일로 저장
df.to_csv(output_csv_path, index=False, encoding="utf-8")
print(f"Responses saved to {output_csv_path}")