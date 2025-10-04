
export default function App() {
  const callBackend = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/ping");
      const data = await response.json();
      console.log("Backend response:", data);
      alert(JSON.stringify(data)); // optional popup to show result
    } catch (err) {
      console.error("Failed to reach backend:", err);
      alert("Backend not reachable. Check logs.");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Tauri + FastAPI Test</h1>
      <button onClick={callBackend}>Ping Backend</button>
    </div>
  );
}
