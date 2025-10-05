import { useAgentWebSocket } from "../hooks/useAgentWebSocket";

export function ToolsCalled() {
    const { actions, isConnected, transcript, error } = useAgentWebSocket();

    return (
        <div className="tools-called-container">
            <div className="connection-status">{isConnected ? "🟢 Connected to Agent" : "🔴 Disconnected"}</div>

            {error && (
                <div className="error-message" style={{ color: "red", padding: "8px", border: "1px solid red", borderRadius: "4px", marginBottom: "8px" }}>
                    ❌ {error}
                </div>
            )}

            {transcript && (
                <div className="transcript">
                    <h3>You said:</h3>
                    <p>{transcript}</p>
                </div>
            )}

            <div className="agent-actions">
                <h3>Agent Activity:</h3>
                {actions.length === 0 ? (
                    <p style={{ color: "#666" }}>Waiting for actions...</p>
                ) : (
                    actions.map((action) => (
                        <div key={action.id} className="action-item">
                            {action.type === "tool_call" && (
                                <div className="tool-call">
                                    <div>
                                        🔧 <strong>{action.tool}</strong>
                                    </div>
                                    <pre style={{ fontSize: "12px", background: "#f5f5f5", padding: "8px", borderRadius: "4px" }}>{JSON.stringify(action.args, null, 2)}</pre>
                                </div>
                            )}

                            {action.type === "tool_result" && (
                                <div className="tool-result">
                                    <div>
                                        ✅ <strong>{action.tool}</strong> completed
                                    </div>
                                    <p>{action.result}</p>
                                </div>
                            )}

                            {action.type === "agent_response" && (
                                <div className="agent-response">
                                    <div>
                                        💬 <strong>Agent:</strong>
                                    </div>
                                    <p>{action.response}</p>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
