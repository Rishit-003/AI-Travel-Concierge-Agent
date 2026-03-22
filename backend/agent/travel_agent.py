from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import GEMINI_API_KEY
from backend.agent.tools import generate_trip_plan, search_uploaded_documents

# 1. Initialize the LLM specifically for the Agent [cite: 131]
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
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
        "You are an expert AI Travel Concierge. "
        "Provide high-quality travel advice.\n\n"
        "Rules:\n"
        "- If user asks about uploaded documents → use 'search_uploaded_documents'\n"
        "- If user asks for itinerary → use 'generate_trip_plan'\n"
        "- Be clear, helpful, and structured in responses"
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