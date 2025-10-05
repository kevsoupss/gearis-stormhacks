// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::Manager;

// Learn more about Tauri commands at https://v1.tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            
            // Set window size first
            window.set_size(tauri::LogicalSize::new(400, 100))?;
            window.set_decorations(false)?;

            // Get screen size
            let monitor = window.current_monitor()?.unwrap();
            let screen_size = monitor.size();
            
            // Position at top right
            let x = (screen_size.width as i32)/2-400; // 20px padding from right
            let y = 30; // 20px from top
            
            window.set_position(tauri::PhysicalPosition::new(x, y))?;
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}