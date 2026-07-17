// Recall launcher — native shell.
//
// A thin, borderless, vibrant panel over the running engine at
// 127.0.0.1:4545. Every engine call goes through Rust (reqwest) so the
// webview never touches the network and there is no CORS surface.

use std::{
    path::PathBuf,
    str::FromStr,
    sync::atomic::{AtomicU64, Ordering},
    time::{SystemTime, UNIX_EPOCH},
};

use serde_json::{json, Value};
use tauri::{
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Manager, PhysicalPosition, WebviewWindow, WindowEvent,
};
use tauri_plugin_autostart::{MacosLauncher, ManagerExt as _};
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

const DEFAULT_HOTKEY: &str = "ctrl+space";

// ------------------------------------------------------- launcher config
//
// Launcher-only preferences live in ~/.recall/launcher.json — plain
// JSON like everything else in ~/.recall, hand-editable, safe to
// delete (deleting resets to defaults). The engine's config.json is
// read-only from here; the launcher never writes engine state.

fn recall_path(name: &str) -> Option<PathBuf> {
    std::env::var_os("HOME").map(|h| PathBuf::from(h).join(".recall").join(name))
}

fn read_json_file(path: Option<PathBuf>) -> Value {
    path.and_then(|p| std::fs::read_to_string(p).ok())
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or_else(|| json!({}))
}

fn load_hotkey_spec() -> String {
    read_json_file(recall_path("launcher.json"))
        .get("hotkey")
        .and_then(|v| v.as_str())
        .map(str::to_string)
        .unwrap_or_else(|| DEFAULT_HOTKEY.to_string())
}

fn save_hotkey_spec(spec: &str) {
    let Some(path) = recall_path("launcher.json") else { return };
    let mut cfg = read_json_file(Some(path.clone()));
    if let Some(obj) = cfg.as_object_mut() {
        obj.insert("hotkey".into(), spec.into());
    }
    if let Some(dir) = path.parent() {
        let _ = std::fs::create_dir_all(dir);
    }
    if let Ok(body) = serde_json::to_string_pretty(&cfg) {
        let _ = std::fs::write(path, body);
    }
}

// "ctrl+shift+k" → (CONTROL|SHIFT, Code::KeyK). Requires at least one
// modifier so a stored spec can never hijack plain typing. Returns
// None on anything unrecognized — callers fall back to the default.
fn parse_hotkey(spec: &str) -> Option<Shortcut> {
    let mut mods = Modifiers::empty();
    let mut key: Option<Code> = None;
    for part in spec.split('+') {
        match part.trim().to_lowercase().as_str() {
            "" => return None,
            "ctrl" | "control" => mods |= Modifiers::CONTROL,
            "alt" | "option" | "opt" => mods |= Modifiers::ALT,
            "shift" => mods |= Modifiers::SHIFT,
            "cmd" | "command" | "super" | "meta" => mods |= Modifiers::SUPER,
            other => {
                if key.is_some() {
                    return None;
                }
                key = code_for(other);
                key?;
            }
        }
    }
    if mods.is_empty() {
        return None;
    }
    Some(Shortcut::new(Some(mods), key?))
}

// "k" → Code::KeyA-style names, "3" → Digit3, "space"/"f5" →
// capitalized variant names.
fn code_for(name: &str) -> Option<Code> {
    let n = name.trim();
    let canonical = if n.len() == 1 && n.chars().all(|c| c.is_ascii_alphabetic()) {
        format!("Key{}", n.to_uppercase())
    } else if n.len() == 1 && n.chars().all(|c| c.is_ascii_digit()) {
        format!("Digit{n}")
    } else {
        let mut chars = n.chars();
        let first = chars.next()?;
        first.to_uppercase().collect::<String>() + chars.as_str()
    };
    Code::from_str(&canonical).ok()
}

// Render a parsed spec back in canonical order so the stored value
// and the settings row always read the same way.
fn normalize_spec(spec: &str) -> Option<String> {
    let shortcut = parse_hotkey(spec)?;
    let mods = shortcut.mods;
    let mut parts: Vec<&str> = Vec::new();
    if mods.contains(Modifiers::CONTROL) {
        parts.push("ctrl");
    }
    if mods.contains(Modifiers::ALT) {
        parts.push("alt");
    }
    if mods.contains(Modifiers::SHIFT) {
        parts.push("shift");
    }
    if mods.contains(Modifiers::SUPER) {
        parts.push("cmd");
    }
    let key = format!("{:?}", shortcut.key)
        .trim_start_matches("Key")
        .trim_start_matches("Digit")
        .to_lowercase();
    Some(format!("{}+{}", parts.join("+"), key))
}

fn default_shortcut() -> Shortcut {
    Shortcut::new(Some(Modifiers::CONTROL), Code::Space)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_and_normalizes_hotkey_specs() {
        assert_eq!(normalize_spec("ctrl+space").as_deref(), Some("ctrl+space"));
        assert_eq!(normalize_spec("CMD+Shift+K").as_deref(), Some("shift+cmd+k"));
        assert_eq!(normalize_spec("option+3").as_deref(), Some("alt+3"));
        assert_eq!(normalize_spec("ctrl+f5").as_deref(), Some("ctrl+f5"));
        assert_eq!(normalize_spec("meta+comma").as_deref(), Some("cmd+comma"));
    }

    #[test]
    fn rejects_unsafe_or_malformed_specs() {
        // A bare key would hijack plain typing.
        assert!(normalize_spec("space").is_none());
        assert!(normalize_spec("k").is_none());
        assert!(normalize_spec("ctrl+").is_none());
        assert!(normalize_spec("ctrl+notakey").is_none());
        assert!(normalize_spec("ctrl+k+j").is_none());
        assert!(normalize_spec("").is_none());
    }
}

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

// ------------------------------------------------- daily-loop marks
//
// The launcher is the surface that proves the continuity loop is
// *used* (Phase 6F), so it marks its own moments: summoned today,
// recoveries shown, one resumed, the resume actually opened work.
// Counts only, fire-and-forget — a missed mark is a statistics
// smudge, never an error, and it must not add a millisecond to any
// hot path.

fn loop_bump(bin: &'static str) {
    tauri::async_runtime::spawn(async move {
        let _ = reqwest::Client::new()
            .post(format!("{ENGINE}/v1/loop/bump"))
            .json(&serde_json::json!({ "bin": bin }))
            .send()
            .await;
    });
}

// `day_started` is once per day and idempotency is the caller's job
// (daily_loop's contract) — dedupe on the epoch-day so repeat
// summons don't inflate it.
static DAY_STARTED_EPOCH_DAY: AtomicU64 = AtomicU64::new(0);

fn mark_day_started_once() {
    let day = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs() / 86_400)
        .unwrap_or(0);
    if DAY_STARTED_EPOCH_DAY.swap(day, Ordering::Relaxed) != day {
        loop_bump("day_started");
    }
}

// ----------------------------------------------------------------- commands

#[tauri::command]
async fn engine_health() -> Result<Value, String> {
    engine_get("/v1/health").await
}

#[tauri::command]
async fn recovery_recent(n: Option<u32>) -> Result<Value, String> {
    let out = engine_get(&format!("/v1/recovery/recent?n={}", n.unwrap_or(3))).await?;
    // Only this command serves the launcher's resting state, so a
    // non-empty answer here IS "the launcher surfaced recoveries".
    let shown = out
        .get("candidates")
        .and_then(|c| c.as_array())
        .map_or(false, |a| !a.is_empty());
    if shown {
        loop_bump("recoveries_shown");
    }
    Ok(out)
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
    // Drilling into a thread's phases is the launcher's
    // "investigation opened" moment.
    loop_bump("investigations_opened");
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
    // The user pressed Resume — that's `recoveries_used` regardless
    // of how the opens go; `resume_success` waits for the tally.
    loop_bump("recoveries_used");
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
    if opened > 0 {
        loop_bump("resume_success");
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

// ------------------------------------------------------- settings

#[tauri::command]
fn settings_get(app: AppHandle) -> Value {
    let autostart = app.autolaunch().is_enabled().unwrap_or(false);
    let engine_cfg = read_json_file(recall_path("config.json"));
    let folders = engine_cfg
        .get("indexed_folders")
        .and_then(|v| v.as_array())
        .map(|a| a.len())
        .unwrap_or(0);
    let config_path = recall_path("config.json")
        .map(|p| p.display().to_string())
        .unwrap_or_default();
    json!({
        "hotkey": load_hotkey_spec(),
        "autostart": autostart,
        "folders": folders,
        "config_path": config_path,
    })
}

// Re-register the summon hotkey live. On any failure the previous
// working hotkey is restored — the panel must never end up
// unsummonable.
#[tauri::command]
fn settings_set_hotkey(app: AppHandle, spec: String) -> Result<String, String> {
    let normalized =
        normalize_spec(&spec).ok_or_else(|| "unrecognized combination".to_string())?;
    let shortcut =
        parse_hotkey(&normalized).ok_or_else(|| "unrecognized combination".to_string())?;
    let gs = app.global_shortcut();
    let previous = load_hotkey_spec();
    let _ = gs.unregister_all();
    if gs.register(shortcut).is_err() {
        let prev = parse_hotkey(&previous).unwrap_or_else(default_shortcut);
        let _ = gs.register(prev);
        return Err("that combination is unavailable".to_string());
    }
    save_hotkey_spec(&normalized);
    Ok(normalized)
}

#[tauri::command]
fn settings_set_autostart(app: AppHandle, on: bool) -> Result<bool, String> {
    let manager = app.autolaunch();
    let result = if on { manager.enable() } else { manager.disable() };
    result.map_err(|e| format!("couldn't change login item: {e}"))?;
    Ok(manager.is_enabled().unwrap_or(on))
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
    mark_day_started_once();
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
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_autostart::init(
            MacosLauncher::LaunchAgent,
            None,
        ))
        .plugin(
            tauri_plugin_global_shortcut::Builder::new()
                // Only one shortcut is ever registered (the summon
                // hotkey), so any firing means "toggle the panel".
                .with_handler(move |app, _scut, event| {
                    if event.state() == ShortcutState::Pressed {
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
            settings_get,
            settings_set_hotkey,
            settings_set_autostart,
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

            // Global summon hotkey — from ~/.recall/launcher.json,
            // quietly falling back to ⌃Space on a missing or
            // unparseable spec.
            let shortcut =
                parse_hotkey(&load_hotkey_spec()).unwrap_or_else(default_shortcut);
            app.global_shortcut().register(shortcut)?;

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
