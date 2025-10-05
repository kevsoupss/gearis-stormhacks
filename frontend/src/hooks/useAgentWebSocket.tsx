import { useEffect, useRef, useState } from "react";
import { appWindow } from "@tauri-apps/api/window";

interface AgentEvent {
    type: "status";
    data: {
        message: string;
        value: boolean | undefined;
    };
}

export function useAgentWebSocket(url: string = "ws://localhost:8000/ws") {
    const [isConnected, setIsConnected] = useState(false);
    const [statusMessage, setStatusMessage] = useState("Ready");
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
            setStatusMessage("Ready");
        };

        ws.onmessage = async (event) => {
            console.log("📨 Raw message received:", event.data);
            try {
                const message: AgentEvent = JSON.parse(event.data);
                console.log("📦 Parsed event:", message.type, message.data);

                if (message.type === "status") {
                    setStatusMessage(message.data.message);
                    setError("");
                } else if (message.type === "set_hidden") {
                    console.log(`👁️ Setting window hidden: ${message.data.value}`);

                    if (message.data.value) {
                        await appWindow.hide();
                        console.log(`✅ Window hidden`);
                    } else {
                        await appWindow.show();
                        console.log(`✅ Window shown`);
                    }
                }
            } catch (err) {
                console.error("❌ Error parsing message:", err);
                setError("Failed to parse message");
            }
        };

        ws.onerror = (error) => {
            console.error("❌ WebSocket error:", error);
            setError("Connection error");
            setStatusMessage("Connection error");
        };

        ws.onclose = (event) => {
            console.log("🔌 WebSocket disconnected:", event.code, event.reason);
            setIsConnected(false);
            setStatusMessage("Disconnected");
        };

        return () => {
            console.log("🧹 Cleaning up WebSocket");
            ws.close();
        };
    }, [url]);

    return { isConnected, statusMessage, error };
}
