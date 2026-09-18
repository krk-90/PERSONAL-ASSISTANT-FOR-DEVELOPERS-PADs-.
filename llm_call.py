from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage,SystemMessage
from dotenv import load_dotenv
import os
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm_model = ChatGroq(model="openai/gpt-oss-safeguard-20b",
                      api_key = GROQ_API_KEY,
                        temperature=0.2,
                          max_tokens=2000,
                            top_p=1,
                              frequency_penalty=0,
                                presence_penalty=0)
def call(query:str):
    messages =[
        SystemMessage("you are a helpful desktop assistant who answer in short paragraph."),
        HumanMessage(query)
    ]
    response = None
    try:
        response = llm_model.invoke(messages)
    except Exception as e:
        print(e)
        return f"Error: {e}"
    return response.content

if __name__ == "__main__":
    call()    