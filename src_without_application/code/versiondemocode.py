from openai import OpenAI

client = OpenAI(api_key='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')

query = "양천도서관에서 파리공원가고싶은데 어떻게 가야될까?"


response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts the starting and destination locations from user queries. Respond in the exact format: Start: [start location]\nDestination: [destination location]"},
                {"role": "user", "content": f"Extract start and destination locations from this query: {query}"}
            ],
            max_tokens=100
        )

print(response.choices[0].message.content)