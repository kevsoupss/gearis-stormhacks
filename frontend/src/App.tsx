import { useRef, useState } from "react";
import "./App.css";
import { Command } from "@tauri-apps/api/shell";
import { useAgentWebSocket } from "./hooks/useAgentWebSocket";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    const { actions, isConnected, transcript, error } = useAgentWebSocket();

    async function sendNotificationWithDebug(title: string, body: string) {
        console.log("🔔 Attempting to send notification:", { title, body });

        try {
            const timestamp = Date.now();
            const script = `display notification "${body}" with title "${title} - ${timestamp}" sound name "Glass"`;
            const command = new Command("osascript", ["-e", script]);
            await command.execute();

            console.log("✅ Notification sent via AppleScript");
        } catch (error) {
            console.error("❌ Notification failed:", error);
        }
    }

    async function sendAudioToBackend(audioBlob: Blob) {
        try {
            const formData = new FormData();
            formData.append("audio", audioBlob, "recording.webm");

            const response = await fetch("http://localhost:8000/api/upload-audio", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                await sendNotificationWithDebug("Success", "Response has been set");
            }
        } catch (error) {
            console.error("Error uploading audio:", error);
            await sendNotificationWithDebug("Failure", "Response has not be recorded");
        }
    }

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
                stream.getTracks().forEach((track) => track.stop());
                await sendAudioToBackend(audioBlob);
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Microphone access denied:", err);
        }
    }

    function stopRecording() {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    }

    // Determine status text based on state
    const getStatusText = () => {
        if (error) return `Error: ${error}`;
        if (!isConnected) return "Disconnected";
        if (isRecording) return "Recording...";
        if (transcript) return transcript;

        // Show latest action if available
        if (actions.length > 0) {
            const lastAction = actions[actions.length - 1];
            if (lastAction.type === "tool_call") {
                return `🔧 ${lastAction.tool}`;
            } else if (lastAction.type === "tool_result") {
                return `✅ ${lastAction.tool}`;
            } else if (lastAction.type === "agent_response") {
                return lastAction.response || "Complete";
            }
        }

        return "Ready";
    };

    return (
        <div className="app-container">
            <div className="main-layout">
                <div className="controls">
                    <button onClick={startRecording} disabled={isRecording} className={`btn-icon ${isRecording ? "disabled active" : ""}`}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                    </button>

                    <button onClick={stopRecording} disabled={!isRecording} className={`btn-icon ${!isRecording ? "disabled" : "active"}`}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="6" y="6" width="12" height="12" rx="2"></rect>
                        </svg>
                    </button>
                </div>

                <div className="status-indicator">
                    <div className={`pulse-dot ${isRecording ? "recording" : ""}`}></div>
                    <span className="status-text">{getStatusText()}</span>
                </div>
            </div>
        </div>
    );
}

export default App;
