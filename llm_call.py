from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def call(query: str):
    """Run the user request through a LangChain prompt/model/output pipeline."""
    if not GROQ_API_KEY:
        return "AI is not configured. Add GROQ_API_KEY to .env to enable assistant replies."
    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_groq import ChatGroq
        llm_model = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=2000,
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are PADs, a concise developer assistant. Respond in plain text only. You have no tools in this conversation, so never emit a tool call or pretend to browse. Never claim an external action was completed unless it was approved and executed."),
            ("human", "{query}"),
        ])
        chain = prompt | llm_model | StrOutputParser()
        try:
            return chain.invoke({"query": query})
        except Exception as error:
            if "tool" not in str(error).lower():
                raise
            retry_query = "Answer directly in plain text without browsing or calling tools. If the request needs GitHub data, tell the user to use PADs' GitHub tab. Request: " + query
            return chain.invoke({"query": retry_query})
    except ImportError:
        return "AI dependencies are missing. Install langchain-groq to enable assistant replies."
    except Exception as error:
        return f"AI request failed for model '{GROQ_MODEL}': {error}"

if __name__ == "__main__":
    call()    