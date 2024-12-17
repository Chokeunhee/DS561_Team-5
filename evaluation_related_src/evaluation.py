import openai
from openai import OpenAI
import pandas as pd
import pdfplumber

# 발급받은 API 키 설정
OPENAI_API_KEY = ""
# openai API 키 인증
#client=OpenAI(api_key=OPENAI_API_KEY)

pdf_path_1 = "/Users/chokeunhee/Desktop/vscode/gptapi/vector_store/data/parkinfo.pdf" #pdf 경로 입력
pdf_path_2 = "/Users/chokeunhee/Desktop/vscode/gptapi/vector_store/data/mokdong_keypoint.pdf" #pdf 경로 입력

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

pdf_text_1 = extract_text_from_pdf(pdf_path_1)
pdf_text_2 = extract_text_from_pdf(pdf_path_2)

def evaluate_answer(question, model_answer, baseline_answer,info1,info2,output_path):
    prompt = f"""
    You are a user of a chatbot and you are evaluating two chatbot answers based on the following criteria:
    
    1. Accuracy: How correct is the response base on the Info provided ? look mainly into numbers and names.
    2. Completeness: Does the response answer the full question?
    3. Readability: Is the language clear, fluent, and easy to understand? (if the answer is too long for user to read or if it is not in a chat format it is considered not Readable, since it is a chatbot.)
    4. Relevance: Does the response stay on topic and address the question directly?

    And here is the actual information that you must check to help you evaluate the answers, especially accuracy:
    Info : {info1} and {info2}. 
    You must Check accuarcy base on the info provided. Please read it very carefully before evaluating the answers.

    ==============================================
    Please evaluate the following answers:
    Question: {question}
    Baseline Answer: {baseline_answer}
    Model Answer: {model_answer}
    

    For each of the four criteria, rate both answers on a scale of 1 to 10, where 1 is the lowest and 10 is the highest.
    Return a score for both answers

    Print out the form in the following order : baseline_Accuracy, baseline_Completeness, baseline_Readability, baseline_Relevance, Model_Accuracy, Model_Completeness, Model_Readability, Model_Relevance

    Remember you must only print 8 numbers like above do not print other words
    
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    chat = client.chat.completions.create(
      model = "gpt-4o-mini-2024-07-18",
      messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': prompt}],
    )
    #return print(chat.choices[0].message.content)

    result = chat.choices[0].message.content.strip()

        # 결과를 파일에 저장
    with open(output_path, "a") as f:
        #f.write(f"Question: {question}\n")
        #f.write(f"Baseline Answer: {baseline_answer}\n")
        #f.write(f"Model Answer: {model_answer}\n")
        #f.write(f"Scores: {result}\n")
        #f.write("=" * 50 + "\n")  # 구분선 추가
        f.write(f"{result}\n")

df = pd.read_csv('/Users/chokeunhee/Desktop/vscode/qa_questions_output_with_both_answer.csv')
#print(df.head(3))

for index, row in df.iterrows():
    question = row['Question']
    baseline_answer = row['Baseline']
    model_answer = row['Model']
    evaluate_answer(question, model_answer, baseline_answer, pdf_text_1, pdf_text_2,"/Users/chokeunhee/Desktop/vscode/evaluation_results.txt" )

