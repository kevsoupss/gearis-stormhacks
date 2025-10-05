import { useRef, useState } from "react";
import "./App.css";
import { Command } from '@tauri-apps/api/shell';

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [micStatus, setMicStatus] = useState("Ready to record");
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunksRef = useRef<Blob[]>([]);

    async function sendNotificationWithDebug(title: string, body: string) {
      console.log("🔔 Attempting to send notification:", { title, body });
      
      try {
        // Use AppleScript instead of Tauri notification API
        const timestamp = Date.now();
        const script = `display notification "${body}" with title "${title} - ${timestamp}" sound name "Glass"`;
        const command = new Command('osascript', ['-e', script]);
        await command.execute();
        
        console.log("✅ Notification sent via AppleScript");
        setMicStatus(prev => prev + " [Notification sent]");
      } catch (error) {
        console.error("❌ Notification failed:", error);
        setMicStatus(prev => prev + " [Notification failed]");
      }
    }

    async function sendAudioToBackend(audioBlob: Blob) {
        try {
            setMicStatus("Uploading to server...");

            const formData = new FormData();
            formData.append("audio", audioBlob, "recording.webm");

            console.log(formData);

            const response = await fetch("http://localhost:8000/api/upload-audio", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                console.log(result);
                setMicStatus(`✓ Text: ${result.transcript}`);
                await sendNotificationWithDebug("Success", "Response has been set");
            } else {
                setMicStatus(`✗ Upload failed: ${response.statusText}`);
            }
        } catch (error) {
            console.error("Error uploading audio:", error);
            setMicStatus(`✗ Error: ${error instanceof Error ? error.message : "Unknown error"}`);
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
            setMicStatus("🎤 Recording...");
        } catch (err) {
            console.error("Microphone access denied:", err);
            setMicStatus(`✗ ${err instanceof Error ? err.message : "Unknown error"}`);
        }
    }

    function stopRecording() {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    }

    return (
        <div className="app-container">
            <div className="content-wrapper">
                <header className="header">
                    <h1 className="title">Voice Recorder</h1>
                    <p className="subtitle">Record audio and save as MP3</p>
                </header>

                <div className="recorder-card">
                    <div className="status-indicator">
                        <div className={`pulse-dot ${isRecording ? "recording" : ""}`}></div>
                        <span className="status-text">{micStatus}</span>
                    </div>

                    <div className="controls">
                        <button onClick={startRecording} disabled={isRecording} className={`btn btn-primary ${isRecording ? "disabled" : ""}`}>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                                <line x1="12" y1="19" x2="12" y2="23"></line>
                                <line x1="8" y1="23" x2="16" y2="23"></line>
                            </svg>
                            Start Recording
                        </button>

                        <button onClick={stopRecording} disabled={!isRecording} className={`btn btn-secondary ${!isRecording ? "disabled" : ""}`}>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <rect x="6" y="6" width="12" height="12" rx="2"></rect>
                            </svg>
                            Stop Recording
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
