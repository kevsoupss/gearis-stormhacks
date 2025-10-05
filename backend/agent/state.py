from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State for ReAct agent"""
    messages: Annotated[list[BaseMessage], operator.add]