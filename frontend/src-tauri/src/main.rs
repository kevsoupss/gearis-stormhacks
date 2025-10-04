use std::process::{Command, Stdio};
use std::io::{BufRead, BufReader};
use std::thread;
use tauri::Manager;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn main() {
    tauri::Builder::default()
        .setup(|_app| {
            // Absolute or relative path to backend Python
            #[cfg(target_os = "windows")]
            let python_path = "..\\..\\backend\\venv\\Scripts\\python.exe";
            
            #[cfg(not(target_os = "windows"))]
            let python_path = "../../backend/venv/bin/python";
            
            // Spawn backend in a separate thread
            thread::spawn(move || {
                println!("Starting FastAPI backend...");

                let mut child = Command::new("../backend/venv/bin/python") // adjust for Windows if needed
                    .args(&["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"])
                    .current_dir("../../backend")  // src-tauri -> frontend -> backend
                    .stdout(Stdio::piped())
                    .stderr(Stdio::piped())
                    .spawn()
                    .expect("Failed to start FastAPI backend");
            
                // Capture stdout
                if let Some(stdout) = child.stdout.take() {
                    let reader = BufReader::new(stdout);
                    thread::spawn(move || {
                        for line in reader.lines() {
                            if let Ok(line) = line {
                                println!("[FastAPI] {}", line);
                            }
                        }
                    });
                }

                // Capture stderr
                if let Some(stderr) = child.stderr.take() {
                    let reader = BufReader::new(stderr);
                    thread::spawn(move || {
                        for line in reader.lines() {
                            if let Ok(line) = line {
                                eprintln!("[FastAPI ERROR] {}", line);
                            }
                        }
                    });
                }

                println!("FastAPI backend thread initialized.");
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
