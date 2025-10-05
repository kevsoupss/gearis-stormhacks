from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from .state import AgentState
from .tools.tools import tools

from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState) -> AgentState:
    """
    The agent node - makes decisions and calls tools
    """
    messages = state["messages"]
    selected_app = state.get("selected_app", "")
    
    # Add system message if first interaction
    if len(messages) == 1:
        system_msg = SystemMessage(
            content=f"""You are Jarvis, a macOS automation agent. You control the local Mac and common apps using ONLY the provided tools. Do not invent abilities.

Core capabilities (via tools):
- System: open/close macOS apps; set/adjust system volume
- Browser/App I/O: open URLs, perform web searches, type text, press keys, create Notes
- Spotify: play/pause/next/prev, search/play track or playlist, get/set volume, current track
- YouTube: search, play first result, open channel/video/playlist, control playback (play_pause, next, previous, fullscreen, mute, increase_volume, decrease_volume, skip_forward, skip_backward)
- Discord: open/close, search, navigate, mark read, send message, upload file, scroll, DM navigation, mute/deafen, answer/decline calls, UI toggles
- Camera: take_picture (saves to Desktop with timestamp)
- Tauri window: set_window_hidden, show_window
- RAG: rag(question) to answer from local knowledge
- Cool: surgin_it for anything mentioning "surge" or "surging" (must call when detected)

Operating rules:
1) Think then act: briefly plan steps, then call tools in the required order. For multi-step tasks, sequence tools (e.g., open app -> navigate/search -> type -> confirm).
2) App context: Selected app: {selected_app if selected_app else "None (user will specify)"}. If selected_app is set, assume requests target that app unless the user names another.
3) Parameterize: Always pass required arguments (e.g., browser name when needed: Chrome, Safari, Firefox, Arc, Brave, Edge). Sensible defaults: Chrome, Spotify, YouTube.
4) Safety: Only use available tools. If a request needs capabilities you lack, say: "I'm sorry, I cannot assist with that request."
5) Special rule: If the user mentions "surge" or "surging" at any point, call surgin_it immediately (in addition to any other needed steps).
6) Explanations: After actions, concisely state what you did and what to expect next.

Examples of decomposing tasks:
- "Search for mac shortcuts": open browser (if needed) -> browser_search("mac shortcuts")
- "Write this down": open Notes -> create_note(title, content) -> optionally type_text for follow-up edits
- "Play lofi on YouTube": youtube_play_video("lofi hip hop", browser="Chrome") -> youtube_fullscreen("Chrome") if requested
- "Send 'on my way' in Discord": open Discord -> focus text input -> discord_send_message("on my way")

If a step fails, return a clear error and suggest the next best alternative within your tools.
"""
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


def output_formatter_node(state: AgentState) -> AgentState:
    """
    Formats the agent's execution results into concise, user-friendly responses
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # If it's a tool call result, don't format yet - let agent continue
    if isinstance(last_message, ToolMessage):
        return {"messages": []}
    
    # If it's an AI message without tool calls, format it for the user
    if isinstance(last_message, AIMessage) and not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
        formatter_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        
        formatter_prompt = f"""You are the output formatter for Jarvis. Format the agent's response into a brief, natural message.

Rules:
- 1-2 sentences max for successful actions
- State what was done and the immediate result
- For errors: what failed + one actionable suggestion
- No technical jargon unless necessary
- Natural, conversational tone
- Don't repeat the user's request back to them

Agent's response to format:
{last_message.content}

Formatted response:"""

        formatted = formatter_llm.invoke([HumanMessage(content=formatter_prompt)])
        
        # Replace the last message with the formatted version
        state["messages"][-1] = AIMessage(content=formatted.content)
    
    return {"messages": []}


def should_format_output(state: AgentState) -> str:
    """
    Routing function: decide if we need to format output or continue with tools
    """
    last_message = state["messages"][-1]
    
    # If the LLM makes a tool call, route to tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    # If it's an AI message without tool calls, format it
    if isinstance(last_message, AIMessage):
        return "format_output"
    
    # Otherwise, end
    return "end"


# Create tool execution node
tool_node = ToolNode(tools)

def should_open_my_presentation(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if "my slide presentation" in last_msg.content.lower():
        return "open_my_presentation"
    return "end"