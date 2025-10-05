from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from .state import AgentState
from .tools.tools import tools

from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools).with_config(verbose=True)


def agent_node(state: AgentState) -> AgentState:
    """
    The agent node - makes decisions and calls tools
    """
    messages = state["messages"]
    selected_app = state.get("selected_app", "")
    
    # Add system message if first interaction
    if len(messages) == 1:
        system_msg = SystemMessage(
            content=f"""You are a macOS automation assistant. You can:
            
1. Control desktop apps (open, close)
2. Adjust system settings (volume)
3. Perform browser actions (search, open URLs)
4. Type text and press keys
5. Create notes

When a user asks you to do something, think through the steps needed:
- If they want to search something, you might need to open a browser THEN search
- If they want to take notes, open Notes THEN type content
- Break down complex tasks into sequential tool calls

Current context:
- Selected app: {selected_app if selected_app else "None (user will specify)"}

IMPORTANT: If the user has already selected an app (selected_app is set), assume their requests 
are for that app unless they explicitly mention a different app. For example:
- If selected_app is "Discord" and user says "send a message", open Discord and send it
- If selected_app is "Notes" and user says "write this down", open Notes and write it down

If you cannot do any of the actions being asked, please respond with "I'm sorry, I cannot assist with that request."

Always explain what you're doing."""
        )
        messages = [system_msg] + messages
    else:
        # For subsequent messages, inject context about selected app if it exists
        if selected_app:
            context_msg = SystemMessage(
                content=f"Remember: The user is currently working with {selected_app}. "
                f"Unless they specify otherwise, assume actions relate to this app."
            )
            messages = [context_msg] + messages
        
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