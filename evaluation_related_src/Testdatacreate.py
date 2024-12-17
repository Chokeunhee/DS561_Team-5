import os
import openai
from openai import OpenAI
import pdfplumber
import json

# 발급받은 API 키 설정
OPENAI_API_KEY = "" #key 입력할것
# openai API 키 인증
openai.api_key = OPENAI_API_KEY
gptmodel = "gpt-4o-mini-2024-07-18"
#client = OpenAI()

# PDF 파일 경로 설정
pdf_path_1 = "/Users/chokeunhee/Desktop/vscode/gptapi/vector_store/data/parkinfo.pdf" #pdf 경로 입력
pdf_path_2 = "/Users/chokeunhee/Desktop/vscode/gptapi/vector_store/data/mokdong_keypoint.pdf" #pdf 경로 입력


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
                                
                다음은 바람직한 질문 예시를 보여줄것이다,질문 예시 처럼 세부적인 질문을 많이 해줘
                질문 예시 이외에도 다양한 종류의 질문도 만들어 주면 좋을거 같아. 창의력을 발휘해봐
                Reference_1 과 Reference_2를 적극 활용해줘.

                그리고 없는 장소나 이름을 임의로 만들어서 사용하는건 절대 안되.
                output의 형식을 맞추어서 질문 dataset 만들어줘. (다양한 공원 포함할 것)
                반드시 output의 형식으로 100쌍 만들어줘. (생략하지말고)

                그리고 너무 뻔한 질문말고 공원의 사소한 부분에 대한 질문들도 물어봐줘 Reference_1의 정보를 적근 활용해서
                
                바람직한 질문 예시:
                아이랑 같이 가려고 하는데 목동의 진달래어린이공원에는 놀이터가 있어?
                목이 마른데 목동에 있는 정목어린이공원에서 물을 마실 수 있을까?
                목동의 모세미어린이공원에 2살 아이랑 같이 갈 생각인데 괜찮을까?
                목동의 백석어린이공원에서 여름에 물놀이 시 주의해야할게 있을까?
                목3동소공원에 가고싶은데 휠체어를 타고 가도 될까?
                지금 목동의 한두어린이공원인데 경로당이 있을까?
                목동의 오목공원에서 킥보드 탈 수 있는 공간이 마련되어 있어?
                오목수변공원에 있는 서울 청년 센터 이름이 뭐였지?
                목동 누리 어린이 공원에 주차장이 있어? 있으면 주차 요금을 알려줄래?
                오구어린이공원의 기획 테마가 뭐야?
                오목공원의 정확한 주소가 뭐야?
                파리공원의 크기는 어느정도로 커?

                
                
                ### input ###
                Reference_1 : {ref1}.
                Reference_2 : {ref2}.
                ### output ###
                질문: 
                """
    
    completion = openai.chat.completions.create(
        model=gptmodel,
        messages=[
            {
                "role": "system",
                "content": "당신은 text를 참고하여 question 데이터셋을 만들어주는 전문가입니다.",
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
#print(qa_result)

# 1. 결과를 txt 파일로 저장
with open("qa_testquestionset.txt", "w", encoding="utf-8") as txt_file:
    txt_file.write(qa_result)