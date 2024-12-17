from openai import OpenAI
import openai
import json

def load_api_keys(config_file="config.text"):
    with open(config_file, "r") as file:
        config = json.load(file)
    return config

# API 키 로드
api_keys = load_api_keys()


def query_openai_assistant(api_key, user_question, assistant_id):
    """
    Queries the OpenAI Assistant API and returns the result.
    
    Parameters:
        api_key (str): Your OpenAI API key.
        user_question (str): The question or input from the user.
        assistant_id (str): The ID of the assistant to interact with.
        
    Returns:
        dict: Response messages if completed, or the status if not completed.
    """
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    try:
        # Create a new thread
        thread = client.beta.threads.create()
        
        # Create a user message in the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_question
        )
        
        # Run the assistant with the given instructions
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
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            return messages
        else:
            return {"status": run.status}
    
    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    API_KEY = api_keys["openai_api_key"]
    ASSISTANT_ID = "asst_wZZWBR2jdIMNdEv3rdzKw5XC"
    user_input = "목운초등학교에 가까운 공원 이름이랑 주소 알려줘"

    result = query_openai_assistant(API_KEY, user_input, ASSISTANT_ID)
    print(result)