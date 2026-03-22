from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.config import GEMINI_API_KEY
from backend.agent.tools import (
    generate_trip_plan,
    get_trip_weather,
    search_uploaded_documents,
)

# List the tools the agent is allowed to use [cite: 49]
tools = [get_trip_weather, generate_trip_plan, search_uploaded_documents]

# System prompt — personality and instructions.
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert AI Travel Concierge.\n\n"
        "IMPORTANT RULES:\n"
        "1. ALWAYS use 'search_uploaded_documents' tool FIRST if documents exist.\n"
        "2. Use that information in your final answer.\n"
        "3. When the user provides a destination and trip start/end dates, call 'get_trip_weather' "
        "with ISO dates (YYYY-MM-DD) unless the user message already contains a complete forecast table.\n"
        "4. Call 'generate_trip_plan' with the same trip fields; pass the weather tool output (or the "
        "embedded forecast from the user) into the 'weather_summary' argument.\n"
        "5. In your final reply, briefly reflect the weather (packing, indoor/outdoor balance).\n"
        "6. Do NOT ignore uploaded documents.\n"
        "7. If no documents found, continue normally.\n"
    ),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

_agent_executor = None


def _get_agent_executor():
    """Build agent on first use so Google GenAI / cryptography DLLs load only when needed."""
    global _agent_executor
    if _agent_executor is None:
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.7,
        )
        agent = create_tool_calling_agent(llm, tools, prompt)
        _agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
        )
    return _agent_executor


def run_travel_agent(user_input: str) -> str:
    """
    Main entry point for the frontend to talk to the agent.
    """
    try:
        response = _get_agent_executor().invoke({"input": user_input})
        return response.get("output", "No response generated.")
    except Exception as e:
        return f"❌ Agent Error: {str(e)}"
