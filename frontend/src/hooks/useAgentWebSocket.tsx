import { useEffect, useRef, useState } from "react";

interface AgentEvent {
    type: "stt_start" | "transcript" | "agent_start" | "tool_call_start" | "tool_call_end" | "agent_complete" | "error";
    data: any;
}

interface AgentAction {
    id: string;
    type: "tool_call" | "tool_result" | "agent_response";
    tool?: string;
    args?: any;
    result?: string;
    response?: string;
    timestamp: number;
}

export function useAgentWebSocket(url: string = "ws://localhost:8000/ws") {
    const [actions, setActions] = useState<AgentAction[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [error, setError] = useState<string>("");
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        console.log("🔌 Attempting WebSocket connection to:", url);
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("✅ WebSocket connected");
            setIsConnected(true);
            setError("");
        };

        ws.onmessage = (event) => {
            console.log("📨 Raw message received:", event.data);
            try {
                const message: AgentEvent = JSON.parse(event.data);
                console.log("📦 Parsed event:", message.type, message.data);

                switch (message.type) {
                    case "stt_start":
                        console.log("🎤 STT started");
                        setActions([]);
                        setTranscript("");
                        break;

                    case "transcript":
                        console.log("📝 Transcript:", message.data.text);
                        setTranscript(message.data.text);
                        break;

                    case "agent_start":
                        console.log("🤖 Agent started");
                        setActions([]);
                        break;

                    case "tool_call_start":
                        console.log("🔧 Tool call started:", message.data.tool);
                        setActions((prev) => [
                            ...prev,
                            {
                                id: message.data.id || `${Date.now()}-${Math.random()}`,
                                type: "tool_call",
                                tool: message.data.tool,
                                args: message.data.args,
                                timestamp: Date.now(),
                            },
                        ]);
                        break;

                    case "tool_call_end":
                        console.log("✅ Tool call ended:", message.data.tool);
                        setActions((prev) => [
                            ...prev,
                            {
                                id: `${Date.now()}-${Math.random()}`,
                                type: "tool_result",
                                tool: message.data.tool,
                                result: message.data.output,
                                timestamp: Date.now(),
                            },
                        ]);
                        break;

                    case "agent_complete":
                        console.log("🎉 Agent complete");
                        setActions((prev) => [
                            ...prev,
                            {
                                id: `${Date.now()}-${Math.random()}`,
                                type: "agent_response",
                                response: message.data.response,
                                timestamp: Date.now(),
                            },
                        ]);
                        break;

                    case "error":
                        console.error("❌ Agent error:", message.data.message);
                        setError(message.data.message);
                        break;

                    default:
                        console.warn("⚠️ Unknown event type:", message);
                }
            } catch (err) {
                console.error("❌ Error parsing message:", err);
            }
        };

        ws.onerror = (error) => {
            console.error("❌ WebSocket error:", error);
            setError("WebSocket connection error");
        };

        ws.onclose = (event) => {
            console.log("🔌 WebSocket disconnected:", event.code, event.reason);
            setIsConnected(false);
        };

        return () => {
            console.log("🧹 Cleaning up WebSocket");
            ws.close();
        };
    }, [url]);

    return { actions, isConnected, transcript, error };
}
