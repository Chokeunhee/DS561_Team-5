from function import *

api_keys = load_api_keys()
openai.api_key = api_keys["openai_api_key"]
kakao_api_key = api_keys["kakao_api_key"]
google_maps_api_key = api_keys["google_maps_api_key"]
tmap_api_key = api_keys["tmap_api_key"]
assistant_id = 'asst_wZZWBR2jdIMNdEv3rdzKw5XC'

'''
if __name__ == "__main__":
    while True:
        query = input("챗봇에게 질문 (종료하려면 'exit' 입력): ").strip()
        if query.lower() == "exit":
            print("프로그램을 종료합니다.")
            break
        result = get_optimal_route(query)
        if result is not None:  # result 값이 None이 아닌 경우
            print("\n응답:\n")
            print(result)
        else:  # result가 None인 경우 다른 함수 호출
            print("assistant run")
            query_openai_assistant(openai.api_key, query, assistant_id)
            print("messages")
'''
            
if __name__ == "__main__":
    while True:
        query = input("챗봇에게 질문 (종료하려면 'exit' 입력): ").strip()
        if query.lower() == "exit":
            print("프로그램을 종료합니다.")
            break
        result, route_q, start, dest, total_time, total_distance ,T_map = get_optimal_route(openai.api_key,query)
        print("route_q :", route_q, "start :",start,"dest :", dest,"T_map :", T_map,"Total time :", total_time,"Total dist :", total_distance)
        if result:
            if route_q:
                if T_map:
                    #print("\n경로 안내:\n")
                    print(f"요청해주신 {start}에서 {dest}까지의 경로 안내입니다. 도보로 약 {total_time}분이 소요되며, 총 이동 거리는 약 {total_distance}미터입니다. 충분히 걸어서 이동하기에 적합한 거리로 보입니다. 아래에 추천 도보 경로를 안내드립니다:\n")
                    print(result)
                else:
                    print(f"요청하신 {start}에서 '{dest}'까지의 경로 안내입니다. 도보로 약 {total_time}분이 소요되며, 총 이동 거리는 약 {total_distance}미터입니다. 이는 도보로 이동하기에는 다소 긴 거리로, 보다 효율적인 이동을 위해 대중교통의 추천 경로를 안내드립니다.\n")
                    print(result)
            else:
                print("경로에 관한 질문이 아님")
                query_openai_assistant(openai.api_key, query, assistant_id)
        else:
            print("\n경로를 찾을 수 없습니다. 다시 시도해주세요.\n")