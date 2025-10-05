from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from graph import save_graph_visualization

from graph import create_graph

load_dotenv()


def main():
    print("=== ReAct Desktop Automation Agent ===")
    print("Examples:")
    print("  - 'search how to make pizza'")
    print("  - 'open Notion and create a note'")
    print("  - 'increase volume by 20'")
    print("  - 'open Spotify'\n")
    
    app = create_graph()
    conversation_history = []
    
    while True:
        user_input = input("\nYou: ")
        if not user_input.strip():
            continue
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        # Add user message
        conversation_history.append(HumanMessage(content=user_input))
        
        # Run the agent - it will loop through tools as needed
        result = app.invoke({"messages": conversation_history})
        
        # Update history with all messages (including tool calls/results)
        conversation_history = result["messages"]
        
        # Print the final response
        final_message = result["messages"][-1]
        if hasattr(final_message, 'content'):
            print(f"\nAssistant: {final_message.content}")


if __name__ == "__main__":
    # save_graph_visualization()
    main()