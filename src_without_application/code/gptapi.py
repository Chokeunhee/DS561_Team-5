import os
import openai
from openai import OpenAI
import pdfplumber
import json

# API 키 로드 함수
def load_api_keys(config_file="config.text"):
    with open(config_file, "r") as file:
        config = json.load(file)
    return config

api_keys = load_api_keys()


# 발급받은 API 키 설정
OPENAI_API_KEY = api_keys["openai_api_key"]
# openai API 키 인증
openai.api_key = OPENAI_API_KEY
gptmodel = "gpt-4o-mini-2024-07-18"
#client = OpenAI()

# PDF 파일 경로 설정
pdf_path_1 = "parkinfo.pdf" #pdf 경로 입력
pdf_path_2 = "mokdong_keypoint.pdf" #pdf 경로 입력


# PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# 추출된 텍스트에서 질문 생성
def generate_qa_from_text(ref1,ref2):
    
    # 생성할 질문-답변 쌍의 프롬프트 설정
    prompt = f"""### Instruction ###
                Reference_1은 양천구 목동에 있는 공원들의 정보를 다루고 있는 텍스트이다.
                Reference_2는 양천구 목동에 있는 주요 시설 (학교,병원,백화점 등)의 위치 정보이다.
                
                실제 사용자가 목동에서 생활하면서 공원에 관하여 질문할 만한 사항을 질문해야된다.
                (공원의 위치, 공원 운영시간, 공원의 시설물, 공원 크기 등).
                사용자는 본인의 위치에 기반하여 공원 정보를 알고 싶어할수도 있다.
                Reference_2의 위치들은 사용자가 현재 위치하고 있는 지점들이다.
                Reference_2의 각 위치들은 가까운 공원의 공원명 정보를 가지고 있다.
                
                답변은 너무 길면 안되고, 너무 기계적으로 딱딱하면 안된다. 
                답변은 마치 친절하지만 전문성 있는 가이드가 답변하는 느낌을 주어야 한다.
                모르거나 정보가 없는 사항에 대해서는 답을 창조하지 말고, 해당 내용에 대한 정보가 없다는 답변을 해야된다.
                
                다음은 바람직한 답변 예시를 보여줄것이다, 답변 예시와 같이 질문 답변 쌍을 만들어라.
                답변 예시 이외에도 다양한 종류의 질문도 만들어 주면 좋을거 같아. Reference_1 과 Reference_2를 적극 활용해줘.

                그리고 없는 장소나 이름을 임의로 만들어서 사용하는건 절대 안되.
                output의 형식을 맞추어서 QA dataset 100개를 만들어줘. (다양한 공원 포함할 것)
                
                바람직한 답변 예시:
                질문 : 지금 목운중학교에 있는데 여기서 가장 가까운 공원은 어디인가요?
                답변 : 목운중학교에서 가장 가까운 공원은 오목공원이에요! 학교에서 걸어서 금방 도착할 수 있는 거리입니다. 공원에는 운동할 수 있는 공간과 산책로가 잘 마련되어 있어요. 궁금한 정보가 있으면 언제든 물어보세요!
                
                질문 : 목마공원에서는 어떤 시설이 있나요? 
                답변 : 목마공원에는 산책로, 지압로, 벤치, 작은 운동장, 게이트볼장, 농구장이 있어요. 이대목동병원 바로 맞은편에 위치해 있어서 접근성도 좋고, 지진 옥외대피장소로도 사용될 수 있어요. 다양한 운동과 휴식을 즐길 수 있는 공간이 마련되어 있습니다.
                
                질문 : 모세미어린이공원의 이용시간은 어떻게 되나요? 
                답변 : 모세미어린이공원은 한밤중에는 이용을 자제해야 합니다. 권장되는 이용시간은 오전 7시부터 오후 10시까지이며, 그 외 시간에는 조용한 공원 이용을 부탁드리고 있습니다.
                
                ### input ###
                Reference_1 : {ref1}.
                Reference_2 : {ref2}.
                ### output ###
                질문: 
                답변: 
                """
    
    completion = openai.chat.completions.create(
        model=gptmodel,
        messages=[
            {
                "role": "system",
                "content": "당신은 text를 참고하여 (QA) question answer 데이터셋을 만들어주는 전문가입니다.",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )
    
    return completion.choices[0].message.content

# PDF에서 텍스트 추출
pdf_text_1 = extract_text_from_pdf(pdf_path_1)
pdf_text_2 = extract_text_from_pdf(pdf_path_2)
#print(pdf_text_2)

# GPT를 이용해 질문-답변 생성
qa_result = generate_qa_from_text(pdf_text_1,pdf_text_2)

# 결과 출력
print(qa_result)

# 1. 결과를 txt 파일로 저장
with open("qa_dataset.txt", "w", encoding="utf-8") as txt_file:
    txt_file.write(qa_result)

'''
# 2. 결과를 json 파일로 저장 (포맷을 변환)
qa_pairs = []
lines = qa_result.split("\n")  # 줄 단위로 자르기

for i in range(0, len(lines), 2):  # 두 줄씩 묶어 질문과 답변 추출
    if i + 1 < len(lines):  # 마지막 라인은 짝이 없을 수 있음
        question = lines[i].strip()
        answer = lines[i + 1].strip()
        qa_pairs.append({"question": question, "answer": answer})

# JSON 파일로 저장
with open("qa_dataset.json", "w", encoding="utf-8") as json_file:
    json.dump(qa_pairs, json_file, ensure_ascii=False, indent=4)

'''