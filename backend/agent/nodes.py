# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from .state import AgentState
from .tools.tools import tools

from dotenv import load_dotenv
load_dotenv()

# Initialize LLM with tools
# llm = ChatOpenAI(model="gpt-4o", temperature=0)  # Use GPT-4 for better tool use
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState) -> AgentState:
    """
    The agent node - makes decisions and calls tools
    """
    messages = state["messages"]
    
    # Add system message if first interaction
    if len(messages) == 1:
        system_msg = HumanMessage(
            content="""You are a macOS automation assistant. You can:
            
1. Control desktop apps (open, close)
2. Adjust system settings (volume)
3. Perform browser actions (search, open URLs)
4. Type text and press keys
5. Create notes

When a user asks you to do something, think through the steps needed:
- If they want to search something, you might need to open a browser THEN search
- If they want to take notes, open Notes THEN type content
- Break down complex tasks into sequential tool calls

If you cannot do any of the actions being asked, please respond with "I'm sorry, I cannot assist with that request."

Always explain what you're doing."""
        )
        messages = [system_msg] + messages
    
    # Call LLM with tools
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}


# Create tool execution node
tool_node = ToolNode(tools)


def should_continue(state: AgentState) -> str:
    """
    Routing function: check if agent wants to use tools or finish
    """
    last_message = state["messages"][-1]
    
    # If the LLM makes a tool call, route to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end
    return "end"