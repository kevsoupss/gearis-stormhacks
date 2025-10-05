from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import agent_node, tool_node, should_continue


def create_graph():
    """
    Creates a ReAct agent graph with tool calling loop
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)  # The thinking/planning node
    workflow.add_node("tools", tool_node)   # Tool execution node
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {   
            "tools": "tools",  # If tools needed, execute them
            "end": END         # If done, finish
        }
    )
    
    # After tools execute, go back to agent to see results
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


def save_graph_visualization(output_file: str = "react_graph.mmd"):
    """
    Saves the ReAct graph structure as a Mermaid diagram (.mmd file)
    """
    app = create_graph()
    
    # Get the Mermaid representation
    mermaid_graph = app.get_graph().draw_mermaid()
    
    # Save to file
    with open(output_file, "w") as f:
        f.write(mermaid_graph)
    
    print(f"✓ Graph visualization saved to: {output_file}")
    print("\nYou can view this file:")
    print("  1. On GitHub (auto-renders .mmd files)")
    print("  2. https://mermaid.live (paste the content)")
    print("  3. VS Code with Mermaid extension")
    print("\nMermaid code preview:")
    print("-" * 50)
    print(mermaid_graph)
    print("-" * 50)
    
    return mermaid_graph