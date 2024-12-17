import openai
import requests
import json
from typing import Tuple, Optional
from selenium import webdriver
import os
import time
import folium

# API 키 로드 함수
def load_api_keys(config_file="config.text"):
    with open(config_file, "r") as file:
        config = json.load(file)
    return config

# API 키 로드
api_keys = load_api_keys()
openai.api_key = api_keys["openai_api_key"]
kakao_api_key = api_keys["kakao_api_key"]
google_maps_api_key = api_keys["google_maps_api_key"]
tmap_api_key = api_keys["tmap_api_key"]

# 질문이 경로 관련 질문인지 GPT API를 사용하여 확인
def is_route_query(query: str) -> bool:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that determines if a user's query is related to route finding or navigation."},
                {"role": "user", "content": f"Is the following query related to finding a route or navigation? Respond with 'Yes' or 'No'.\n\nQuery: {query}"}
            ],
            max_tokens=10
        )
        decision = response['choices'][0]['message']['content'].strip()
        print(f"GPT 판단: {decision}")
        return decision.lower() == "yes"
    except Exception as e:
        print(f"Error in route query detection: {e}")
        return False

# 위치 추출 함수
def extract_locations_from_question(question: str) -> Tuple[str, str]:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts the starting and destination locations from user queries. Respond in the exact format: Start: [start location]\nDestination: [destination location]"},
                {"role": "user", "content": f"Extract start and destination locations from this query: {question}"}
            ],
            max_tokens=100
        )
        extracted_text = response['choices'][0]['message']['content'].strip()
        print(f"OpenAI Response: {extracted_text}")
        lines = extracted_text.split('\n')
        start_location = lines[0].split('Start:')[1].strip() if 'Start:' in lines[0] else ""
        destination_location = lines[1].split('Destination:')[1].strip() if 'Destination:' in lines[1] else ""
        return start_location, destination_location
    except Exception as e:
        print(f"Error extracting locations: {e}")
        return "", ""

# 카카오 API를 사용한 좌표 변환
def get_coordinates(location_name: str) -> Optional[Tuple[float, float]]:
    if not location_name:
        return None, None
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
    params = {"query": location_name}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if data['documents']:
            location = data['documents'][0]
            coords = (round(float(location['y']), 6), round(float(location['x']), 6))
            return coords
        return None, None
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return None, None

# Tmap 도보 경로 검색
def get_tmap_route(start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> Optional[dict]:
    walk_url = "https://apis.openapi.sk.com/tmap/routes/pedestrian"
    headers = {"appKey": tmap_api_key, "Content-Type": "application/json"}
    data = {
        "startX": start_lng, "startY": start_lat,
        "endX": end_lng, "endY": end_lat,
        "reqCoordType": "WGS84GEO", "resCoordType": "WGS84GEO",
        "startName": "출발지", "endName": "목적지"
    }
    try:
        response = requests.post(walk_url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result if result['features'][0]['properties']['totalTime'] <= 15 * 60 else None
    except Exception as e:
        print(f"Tmap API error: {e}")
        return None

# Google Maps 대중교통 경로 검색
def get_google_transit_route(start_lat: float, start_lng: float, end_lat: float, end_lng: float) -> Optional[dict]:
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{start_lat},{start_lng}",
        "destination": f"{end_lat},{end_lng}",
        "mode": "transit",
        "language": "ko",
        "alternatives": "true",
        "key": google_maps_api_key
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        return result if result['status'] == 'OK' else None
    except Exception as e:
        print(f"Google Maps API error: {e}")
        return None

# Tmap 도보 경로 응답 생성 (한국어로 소요 시간 및 경로 설명 추가)
def generate_tmap_response(tmap_result: dict) -> str:
    try:
        total_time = tmap_result['features'][0]['properties']['totalTime']  # 총 소요 시간 (초 단위)
        total_distance = tmap_result['features'][0]['properties']['totalDistance']  # 총 이동 거리 (미터 단위)
        total_time_minutes = total_time // 60  # 분 단위로 변환

        # GPT 응답 요청
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 도보 경로를 한국어로 명확히 안내하는 도우미입니다."},
                {"role": "user", "content": f"다음 정보를 바탕으로 도보 경로 설명을 작성해주세요:\n\n총 소요 시간: {total_time_minutes}분\n총 이동 거리: {total_distance}미터\n세부 경로 정보: {tmap_result}"}
            ],
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generating Tmap response: {e}")
        return f"도보 경로 생성 중 오류가 발생했습니다: {str(e)}"

# Google Maps 대중교통 경로 응답 생성
def generate_google_transit_response(google_result: dict) -> str:
    try:
        routes = google_result['routes'][:3]  # 최대 3개 경로
        transit_info = []
        for route_index, route in enumerate(routes, 1):
            leg = route['legs'][0]
            route_details = [
                f"=== 경로 {route_index} ===",
                f"총 소요 시간: {leg['duration']['text']}",
                f"총 이동 거리: {leg['distance']['text']}"
            ]

            for step_index, step in enumerate(leg['steps'], 1):
                if step['travel_mode'] == 'WALKING':
                    instructions = step['html_instructions'].replace('<b>', '').replace('</b>', '')
                    route_details.append(f"[구간 {step_index}] 도보: {instructions} ({step['distance']['text']})")
                elif step['travel_mode'] == 'TRANSIT':
                    transit_details = step['transit_details']
                    route_details.append(
                        f"[구간 {step_index}] {transit_details['line']['vehicle']['name']} - {transit_details['line']['short_name']} \n"
                        f"출발: {transit_details['departure_stop']['name']} ({transit_details['departure_time']['text']}) \n"
                        f"도착: {transit_details['arrival_stop']['name']} ({transit_details['arrival_time']['text']})"
                    )
            transit_info.append('\n'.join(route_details))
        return '\n\n'.join(transit_info)
    except Exception as e:
        print(f"Error generating Google Maps response: {e}")
        return ""

# 최적 경로 처리
def get_optimal_route(query: str):
    
    start, dest = extract_locations_from_question(query)
    if not start or not dest:
        print("Unable to extract locations.")
        return None

    start_lat, start_lng = get_coordinates(start)
    end_lat, end_lng = get_coordinates(dest)

    if not all([start_lat, start_lng, end_lat, end_lng]):
        print("Coordinates could not be determined.")
        return None

    # Tmap 도보 경로 처리
    tmap_result = get_tmap_route(start_lat, start_lng, end_lat, end_lng)
    if tmap_result:
        print("Walking route available (Tmap).")
        tmap_response = generate_tmap_response(tmap_result)
        print(tmap_response)

        # 이미지를 저장하고 경로 출력
        image_path = save_tmap_route_as_image(tmap_result)
        if image_path:
            print(f"Tmap 경로 이미지를 저장했습니다: {image_path}")
        else:
            print("Tmap 경로 이미지를 저장하지 못했습니다.")
        return tmap_response # 텍스트와 이미지를 조합해 사용자에게 응답

    # Google Maps 대중교통 경로 처리
    google_result = get_google_transit_route(start_lat, start_lng, end_lat, end_lng)
    if google_result:
        print("Transit route available (Google Maps).")
        google_response = generate_google_transit_response(google_result)
        print(google_response)
        return google_response

    print("No route found.")
    return None

# Tmap 경로 데이터를 이미지로 저장 (확대 옵션 추가)
def save_tmap_route_as_image(tmap_result: dict, output_image_path: str = "tmap_route.png"):
    try:
        # Tmap 경로 데이터를 Folium 지도에 추가
        start_point = tmap_result['features'][0]['geometry']['coordinates']
        
        # 경로 중심 계산
        line_coords = [
            (coord[1], coord[0]) 
            for feature in tmap_result['features'] 
            if feature['geometry']['type'] == "LineString"
            for coord in feature['geometry']['coordinates']
        ]
        if line_coords:
            center_lat = sum(coord[0] for coord in line_coords) / len(line_coords)
            center_lng = sum(coord[1] for coord in line_coords) / len(line_coords)
            bounds = [(min(coord[0] for coord in line_coords), min(coord[1] for coord in line_coords)),
                      (max(coord[0] for coord in line_coords), max(coord[1] for coord in line_coords))]
        else:
            center_lat, center_lng = start_point[1], start_point[0]
            bounds = [(center_lat - 0.01, center_lng - 0.01), (center_lat + 0.01, center_lng + 0.01)]

        m = folium.Map(location=[center_lat, center_lng], zoom_start=16)  # 기본 줌 레벨을 높게 설정

        for feature in tmap_result['features']:
            if feature['geometry']['type'] == "LineString":
                line_coords = [(coord[1], coord[0]) for coord in feature['geometry']['coordinates']]
                folium.PolyLine(locations=line_coords, color="blue", weight=5, opacity=0.7).add_to(m)
            elif feature['geometry']['type'] == "Point":
                point_coords = (feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0])
                description = feature['properties'].get('description', '지점 정보 없음')
                folium.Marker(location=point_coords, popup=description).add_to(m)

        # 지도의 경계를 경로에 맞춤
        m.fit_bounds(bounds)

        # HTML 파일 저장
        html_path = "tmap_route.html"
        m.save(html_path)

        # Selenium을 사용해 HTML 파일을 이미지로 캡처
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1600x1200")  # 창 크기를 더 크게 설정
        driver = webdriver.Chrome(options=options)

        driver.get(f"file://{os.path.abspath(html_path)}")
        time.sleep(2)  # 지도 로드 대기
        driver.save_screenshot(output_image_path)
        driver.quit()

        print(f"지도 이미지를 저장했습니다: {output_image_path}")
        return output_image_path

    except Exception as e:
        print(f"이미지 저장 중 오류 발생: {e}")
        return None

# 실행 예제
if __name__ == "__main__":
    while True:
        query = input("챗봇에게 질문 (종료하려면 'exit' 입력): ").strip()
        if query.lower() == "exit":
            print("프로그램을 종료합니다.")
            break
        result = get_optimal_route(query)
        result = get_optimal_route(query)
        if result is not None:  # result 값이 None이 아닌 경우
            print("\n응답:\n")
            print(result)
        else:  # result가 None인 경우 다른 함수 호출
            print("None")
            #query_openai_assistant(openai.api_key, query, assistant_id)