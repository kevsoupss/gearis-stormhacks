from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class IntentDetector:
    """Detects user intent for app opening requests"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        # self.llm = ChatOpenAI(model=model, temperature=0)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    def detect_app_request(self, message: str) -> tuple[bool, str]:
        """
        Uses LLM to detect if user wants to open an app
        
        Returns:
            (is_app_request, app_name)
        """
        prompt = f"""You are an intent classifier for a macOS automation system that CAN open applications.

Analyze if the user wants to open/launch/use a macOS application.

User message: "{message}"

Rules:
- If the user wants to open, launch, start, or use any application, respond YES
- Extract the most likely application name
- Common apps: Safari, Chrome, Firefox, Notion, Notes, Calendar, Mail, Messages, Spotify, Music, Calculator, Terminal, VS Code, Slack, Discord, etc.

Respond ONLY in this exact format (no other text):
INTENT: [YES or NO]
APP: [application name if YES, otherwise NONE]

Examples:
"I want to use Notion" -> INTENT: YES\\nAPP: Notion
"can you open notion" -> INTENT: YES\\nAPP: Notion
"open safari please" -> INTENT: YES\\nAPP: Safari
"launch spotify" -> INTENT: YES\\nAPP: Spotify
"what's the weather" -> INTENT: NO\\nAPP: NONE
"I need to take notes" -> INTENT: YES\\nAPP: Notes
"let me browse the web" -> INTENT: YES\\nAPP: Safari
"tell me about Notion" -> INTENT: NO\\nAPP: NONE

Your response:"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()
        
        print(f"[Intent Detection Raw] {response_text}")
        
        # Parse the response
        lines = response_text.split('\n')
        intent = "NO"
        app_name = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("INTENT:"):
                intent = line.split("INTENT:")[1].strip()
            elif line.startswith("APP:"):
                app_name = line.split("APP:")[1].strip()
        
        if intent == "YES" and app_name and app_name != "NONE":
            print(f"[Intent Detection] ✓ Detected app request: {app_name}")
            return True, app_name
        
        print(f"[Intent Detection] ✗ No app request detected")
        return False, ""