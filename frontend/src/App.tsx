import { invoke } from "@tauri-apps/api/tauri";
import { useRef, useState } from "react";
import "./App.css";
import reactLogo from "./assets/react.svg";

function App() {
  const [greetMsg, setGreetMsg] = useState("");
  const [name, setName] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [micStatus, setMicStatus] = useState("Not started");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  async function sendAudioToBackend(audioBlob: Blob) {
    try {
      setMicStatus("Uploading to server...");
      
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      
      const response = await fetch("http://localhost:8000/api/upload-audio", {
        method: "POST",
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        setMicStatus(`Upload successful! ${JSON.stringify(result)}`);
      } else {
        setMicStatus(`Upload failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Error uploading audio:", error);
      setMicStatus(`Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async function greet() {
    setGreetMsg(await invoke("greet", { name }));
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicStatus("Microphone access granted");
      
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
        setMicStatus(`Recording complete (${audioBlob.size} bytes)`);
        
        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
        
        // Send to backend
        await sendAudioToBackend(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setMicStatus("Recording...");
    } catch (err) {
      console.error("Microphone access denied:", err);
      setMicStatus(`Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }

  function stopRecording() {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }

  return (
    <main className="container">
      <h1>Welcome to Tauri + React</h1>

      <div className="row">
        <a href="https://vite.dev" target="_blank">
          <img src="/vite.svg" className="logo vite" alt="Vite logo" />
        </a>
        <a href="https://tauri.app" target="_blank">
          <img src="/tauri.svg" className="logo tauri" alt="Tauri logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <p>Click on the Tauri, Vite, and React logos to learn more.</p>

      <form
        className="row"
        onSubmit={(e) => {
          e.preventDefault();
          greet();
        }}
      >
        <input
          id="greet-input"
          onChange={(e) => setName(e.currentTarget.value)}
          placeholder="Enter a name..."
        />
        <button type="submit">Greet</button>
      </form>
      <p>{greetMsg}</p>

      <div className="row" style={{ marginTop: "2rem" }}>
        <h2>Microphone Test</h2>
        <div>
          <button 
            onClick={startRecording} 
            disabled={isRecording}
            style={{ marginRight: "10px" }}
          >
            Start Recording
          </button>
          <button 
            onClick={stopRecording} 
            disabled={!isRecording}
          >
            Stop Recording
          </button>
        </div>
        <p>Status: {micStatus}</p>
      </div>
    </main>
  );
}

export default App;