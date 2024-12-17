from function import *
import sys
import json

api_keys = load_api_keys()
openai.api_key = api_keys["openai_api_key"]
kakao_api_key = api_keys["kakao_api_key"]
google_maps_api_key = api_keys["google_maps_api_key"]
tmap_api_key = api_keys["tmap_api_key"]
assistant_id = 'asst_wZZWBR2jdIMNdEv3rdzKw5XC'


            
if __name__ == "__main__":
    while True:
        try:
            query = input().strip()
            if not query:
                continue

            result, route_q = get_optimal_route(openai.api_key,query)

            if result:
                if route_q:
                    response = {"type": "route", "response": result}

                else:
                    assistant_response = query_openai_assistant(openai.api_key, query, assistant_id)
                    response = {"type": "assistant", "response": assistant_response}
                
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            
        except Exception as e:
            error_response = {"type": "error", "response": str(e)}
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()