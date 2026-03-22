from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY
from backend.agent.tools import generate_trip_plan, search_uploaded_documents

# 1. Initialize the LLM specifically for the Agent [cite: 131]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7 # Slight creativity for travel planning
)

# 2. List the tools the agent is allowed to use [cite: 49]
tools = [generate_trip_plan, search_uploaded_documents]

# 3. Define the System Prompt
# This gives the Agent its "personality" and instructions.
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert AI Travel Concierge.\n\n"
        "IMPORTANT RULES:\n"
        "1. ALWAYS use 'search_uploaded_documents' tool FIRST if documents exist.\n"
        "2. Use that information in your final answer.\n"
        "3. Then create itinerary using 'generate_trip_plan'.\n"
        "4. Do NOT ignore uploaded documents.\n"
        "5. If no documents found, continue normally.\n"
    ),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 4. Construct the Tool-Calling Agent [cite: 50]
agent = create_tool_calling_agent(llm, tools, prompt)

# 5. Create the Executor (The loop that runs the agent)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, # This helps you see the AI's "thought process" in the terminal
    handle_parsing_errors=True
)

def run_travel_agent(user_input: str) -> str:
    """
    Main entry point for the frontend to talk to the agent.
    """
    try:
        response = agent_executor.invoke({"input": user_input})
        return response.get("output", "No response generated.")
    except Exception as e:
        return f"❌ Agent Error: {str(e)}"