from state import AgentState

def route_after_input(state: AgentState) -> str:
    """
    Determines which node to go to after processing input
    """
    return state["next_step"]