from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import agent_node, tool_node, output_formatter_node, should_format_output


def create_graph():
    """
    Creates a ReAct agent graph with tool calling loop and output formatting
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("format_output", output_formatter_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_format_output,  # Use the new routing function
        {   
            "tools": "tools",
            "format_output": "format_output",
            "end": END
        }
    )
    
    # After tools execute, go back to agent
    workflow.add_edge("tools", "agent")
    
    # After formatting, we're done
    workflow.add_edge("format_output", END)
    
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