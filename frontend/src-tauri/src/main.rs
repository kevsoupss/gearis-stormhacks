// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, SystemTray, SystemTrayEvent, SystemTrayMenu, Manager};

// Learn more about Tauri commands at https://v1.tauri.app/v1/guides/features/command
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn main() {
    // Create system tray menu
    let show_hide = CustomMenuItem::new("toggle".to_string(), "Show/Hide");
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show_hide)
        .add_item(quit);
    
    let tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .system_tray(tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "toggle" => {
                        let window = app.get_window("main").unwrap();
                        if window.is_visible().unwrap() {
                            window.hide().unwrap();
                        } else {
                            window.show().unwrap();
                        }
                    }
                    "quit" => {
                        std::process::exit(0);
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            
            // Set window size first
            window.set_size(tauri::LogicalSize::new(400, 250))?;
            window.set_decorations(false)?;

            // Get screen size
            let monitor = window.current_monitor()?.unwrap();
            let screen_size = monitor.size();
            
            // Position at top right
            let x = (screen_size.width as i32)/2-400; // 20px padding from right
            let y = 0; // 20px from top
            
            window.set_position(tauri::PhysicalPosition::new(x, y))?;
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}