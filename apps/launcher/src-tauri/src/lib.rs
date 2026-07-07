// Recall launcher — native shell.
//
// A thin, borderless, vibrant panel over the running engine at
// 127.0.0.1:4545. Every engine call goes through Rust (reqwest) so the
// webview never touches the network and there is no CORS surface.

use serde_json::Value;
use tauri::{
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager, PhysicalPosition, WebviewWindow, WindowEvent,
};
use tauri_plugin_global_shortcut::{
    Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState,
};
use tauri_plugin_opener::OpenerExt;

const ENGINE: &str = "http://127.0.0.1:4545";
const PANEL_WIDTH: f64 = 720.0;

// Gap between restoration opens. Racing `open` calls land in random
// z-order; a short stagger lets the OS layer windows in the plan's
// order (files → chats → tabs → searches), matching the extension's
// resume cadence.
const RESTORE_STAGGER_MS: u64 = 140;

// ----------------------------------------------------------------- engine I/O

async fn engine_get(path: &str) -> Result<Value, String> {
    reqwest::Client::new()
        .get(format!("{ENGINE}{path}"))
        .send()
        .await
        .map_err(|e| format!("engine unreachable: {e}"))?
        .json::<Value>()
        .await
        .map_err(|e| format!("bad engine response: {e}"))
}

async fn engine_post(path: &str) -> Result<Value, String> {
    reqwest::Client::new()
        .post(format!("{ENGINE}{path}"))
        .send()
        .await
        .map_err(|e| format!("engine unreachable: {e}"))?
        .json::<Value>()
        .await
        .map_err(|e| format!("bad engine response: {e}"))
}

// ----------------------------------------------------------------- commands

#[tauri::command]
async fn engine_health() -> Result<Value, String> {
    engine_get("/v1/health").await
}

#[tauri::command]
async fn recovery_recent(n: Option<u32>) -> Result<Value, String> {
    engine_get(&format!("/v1/recovery/recent?n={}", n.unwrap_or(3))).await
}

#[tauri::command]
async fn search(q: String) -> Result<Value, String> {
    let q = urlencode(&q);
    engine_get(&format!("/v1/search?q={q}")).await
}

#[tauri::command]
async fn threads_recent(n: Option<u32>) -> Result<Value, String> {
    engine_get(&format!("/v1/threads/recent?n={}", n.unwrap_or(6))).await
}

#[tauri::command]
async fn thread_evolution(id: String) -> Result<Value, String> {
    engine_get(&format!("/v1/threads/{id}/evolution")).await
}

#[tauri::command]
async fn search_files(q: String, n: Option<u32>) -> Result<Value, String> {
    let q = urlencode(&q);
    engine_get(&format!("/v1/search/files?q={q}&n={}", n.unwrap_or(4))).await
}

#[tauri::command]
async fn resurface_idle(n: Option<u32>) -> Result<Value, String> {
    engine_get(&format!("/v1/resurface/idle?n={}", n.unwrap_or(3))).await
}

// Resolve the candidate's restoration plan, then open every step in the
// engine's choreographed order (files → chats → tabs → searches). The
// endpoint orders the steps; we execute them with a stagger so the OS
// presents the windows in that order, tally what actually opened, and
// return the plan annotated with `requested`/`opened` — the plan is
// advisory, the tally is what happened.
#[tauri::command]
async fn recovery_restore(app: AppHandle, id: String) -> Result<Value, String> {
    let mut plan = engine_post(&format!("/v1/recovery/{id}/restore")).await?;
    let mut requested: u64 = 0;
    let mut opened: u64 = 0;
    if let Some(steps) = plan.get("steps").and_then(|s| s.as_array()).cloned() {
        for step in &steps {
            let kind = step.get("kind").and_then(|v| v.as_str()).unwrap_or("");
            let target = step.get("target").and_then(|v| v.as_str()).unwrap_or("");
            if target.is_empty() {
                continue;
            }
            requested += 1;
            if requested > 1 {
                tokio::time::sleep(std::time::Duration::from_millis(RESTORE_STAGGER_MS))
                    .await;
            }
            let opener = app.opener();
            let ok = match kind {
                "url" => opener.open_url(target, None::<&str>).is_ok(),
                _ => opener.open_path(target, None::<&str>).is_ok(),
            };
            if ok {
                opened += 1;
            }
        }
    }
    if let Some(obj) = plan.as_object_mut() {
        obj.insert("requested".into(), requested.into());
        obj.insert("opened".into(), opened.into());
    }
    Ok(plan)
}

// Open a single target — the search surface's Enter action. Same
// opener the restoration path uses; `kind` chooses url vs path.
#[tauri::command]
async fn open_target(app: AppHandle, kind: String, target: String) -> Result<(), String> {
    if target.is_empty() {
        return Ok(());
    }
    let opener = app.opener();
    let _ = match kind.as_str() {
        "url" => opener.open_url(&target, None::<&str>),
        _ => opener.open_path(&target, None::<&str>),
    };
    Ok(())
}

#[tauri::command]
fn resize_height(window: WebviewWindow, height: f64) {
    let h = height.clamp(64.0, 720.0);
    let _ = window.set_size(tauri::LogicalSize::new(PANEL_WIDTH, h));
}

fn urlencode(s: &str) -> String {
    s.bytes()
        .map(|b| match b {
            b'a'..=b'z' | b'A'..=b'Z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                (b as char).to_string()
            }
            b' ' => "+".to_string(),
            _ => format!("%{:02X}", b),
        })
        .collect()
}

// ----------------------------------------------------------------- window

fn position_upper_third(win: &WebviewWindow) {
    if let Ok(Some(monitor)) = win.current_monitor() {
        let screen = monitor.size();
        if let Ok(win_size) = win.outer_size() {
            let x = (screen.width as i32 - win_size.width as i32) / 2;
            let y = (screen.height as f64 * 0.22) as i32;
            let _ = win.set_position(PhysicalPosition::new(x.max(0), y.max(0)));
        }
    }
}

fn show_panel(win: &WebviewWindow) {
    position_upper_third(win);
    let _ = win.show();
    let _ = win.set_focus();
}

fn toggle_panel(win: &WebviewWindow) {
    if win.is_visible().unwrap_or(false) {
        let _ = win.hide();
    } else {
        show_panel(win);
    }
}

// ----------------------------------------------------------------- entry

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let toggle = Shortcut::new(Some(Modifiers::CONTROL), Code::Space);

    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                .with_handler(move |app, scut, event| {
                    if scut == &toggle && event.state() == ShortcutState::Pressed {
                        if let Some(win) = app.get_webview_window("main") {
                            toggle_panel(&win);
                        }
                    }
                })
                .build(),
        )
        .invoke_handler(tauri::generate_handler![
            engine_health,
            recovery_recent,
            search,
            search_files,
            resurface_idle,
            threads_recent,
            thread_evolution,
            recovery_restore,
            open_target,
            resize_height,
        ])
        .setup(move |app| {
            let win = app
                .get_webview_window("main")
                .expect("main window must exist");

            // Native macOS vibrancy + 13px corner radius. Warm graphite
            // tint comes from the web layer painted over the blur.
            #[cfg(target_os = "macos")]
            {
                use window_vibrancy::{apply_vibrancy, NSVisualEffectMaterial};
                let _ = apply_vibrancy(
                    &win,
                    NSVisualEffectMaterial::HudWindow,
                    None,
                    Some(13.0),
                );
            }

            // Global summon hotkey.
            app.global_shortcut().register(toggle)?;

            // Tray — the only mouse affordance. Left-click toggles.
            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .tooltip("Recall — continuity")
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        if let Some(win) = tray.app_handle().get_webview_window("main") {
                            toggle_panel(&win);
                        }
                    }
                })
                .build(app)?;

            // Hide on blur — the panel is summoned, never lingers.
            let hide_target = win.clone();
            win.on_window_event(move |event| {
                if let WindowEvent::Focused(false) = event {
                    let _ = hide_target.hide();
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Recall launcher");
}
