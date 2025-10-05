import { Command } from "@tauri-apps/api/shell";
import { useEffect, useRef, useState } from "react";
import "./App.css";
import { useAgentWebSocket } from "./hooks/useAgentWebSocket";
// import Switch from "./components/Switch";
import { appWindow, LogicalSize } from "@tauri-apps/api/window";

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [toggleVoice, setToggleVoice] = useState(true);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    const { isConnected, statusMessage, error } = useAgentWebSocket();

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

            const response = await fetch(`http://localhost:8000/api/upload-audio?toggle_voice=${toggleVoice}`, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                await sendNotificationWithDebug("Success", "Task completed");
            }
        } catch (error) {
            console.error("Error uploading audio:", error);
            await sendNotificationWithDebug("Failure", "Request failed");
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
                const audioBlob = new Blob(audioChunksRef.current, {
                    type: "audio/webm",
                });
                stream.getTracks().forEach((track) => track.stop());
                await sendAudioToBackend(audioBlob);
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Microphone access denied:", err);
        }
    }

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const resizeWindow = async () => {
            if (containerRef.current) {
                const height = containerRef.current.scrollHeight + 40; // Add padding
                const width = Math.min(Math.max(containerRef.current.scrollWidth + 40, 300), 600);

                await appWindow.setSize(new LogicalSize(width, height));
            }
        };

        resizeWindow();
    }, [isRecording, statusMessage]);

    function stopRecording() {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    }

    const getStatusText = () => {
        if (error) return `Error: ${error}`;
        if (!isConnected) return "Disconnected";
        if (isRecording) return "Recording...";
        return statusMessage;
    };

    return (
        <div className="app-container" ref={containerRef}>
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
                    <button onClick={() => setToggleVoice(!toggleVoice)} className={`btn-icon ${toggleVoice ? "enabled" : ""}`}>
                    {toggleVoice ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-volume-up-fill" viewBox="0 0 16 16">
                      <path d="M11.536 14.01A8.47 8.47 0 0 0 14.026 8a8.47 8.47 0 0 0-2.49-6.01l-.708.707A7.48 7.48 0 0 1 13.025 8c0 2.071-.84 3.946-2.197 5.303z"/>
                      <path d="M10.121 12.596A6.48 6.48 0 0 0 12.025 8a6.48 6.48 0 0 0-1.904-4.596l-.707.707A5.48 5.48 0 0 1 11.025 8a5.48 5.48 0 0 1-1.61 3.89z"/>
                      <path d="M8.707 11.182A4.5 4.5 0 0 0 10.025 8a4.5 4.5 0 0 0-1.318-3.182L8 5.525A3.5 3.5 0 0 1 9.025 8 3.5 3.5 0 0 1 8 10.475zM6.717 3.55A.5.5 0 0 1 7 4v8a.5.5 0 0 1-.812.39L3.825 10.5H1.5A.5.5 0 0 1 1 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06"/>
                    </svg>
                    ): (<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-volume-off-fill" viewBox="0 0 16 16">
                      <path d="M10.717 3.55A.5.5 0 0 1 11 4v8a.5.5 0 0 1-.812.39L7.825 10.5H5.5A.5.5 0 0 1 5 10V6a.5.5 0 0 1 .5-.5h2.325l2.363-1.89a.5.5 0 0 1 .529-.06"/>
                    </svg>) }
                    </button>
                </div>

                <div className="status-indicator">
                    <div className={`pulse-dot ${isRecording ? "recording" : ""}`}></div>
                    <span className="status-text">{getStatusText()}</span>
                </div>
                {/* <Switch label={"Toggle voice"} checked={toggleVoice} setChecked={setToggleVoice} /> */}
            </div>
        </div>
    );
}

export default App;
