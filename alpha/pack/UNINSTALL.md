# Uninstall — no hard feelings

If Recall isn't working for you — for any reason
— this is the clean exit.

**Before you uninstall, please leave one line in
[FEEDBACK.md](FEEDBACK.md):**

> "Uninstalled because: ____"

That sentence is worth more than 100 hours of
the product feeling fine. It's the single
clearest signal we get.

---

## Step 1 — uninstall the desktop app

**Windows:** Settings → Apps → Recall → Uninstall.

This removes:

- `C:\Program Files\Recall\`
- Start-menu entry
- Tray icon
- The loopback API registration

This does **not** touch `~/.recall/`. Your event
log + indexes survive.

## Step 2 — remove the extension

`chrome://extensions` → Recall → Remove.

The extension forgets the pairing.

## Step 3 — wipe local data (optional)

If you want every trace of Recall gone:

```powershell
# Wipes ~/.recall/ entirely.
Remove-Item -Recurse -Force $env:USERPROFILE\.recall
```

Or, less aggressive — just the demo store:

```
python recall.py demo reset   # leaves your real events
```

Or the in-app reset, which preserves the install
but clears the event store, config, and indexes:

```
python recall.py reset
```

The reset CLI prints what it touches before
doing anything destructive.

## Step 4 — close the loop

Three options:

| Option                         | When                                    |
|--------------------------------|-----------------------------------------|
| Quick exit                     | Write one line in [FEEDBACK.md](FEEDBACK.md), close laptop. |
| 5-minute writeup               | Use the template in [FEEDBACK.md](FEEDBACK.md). |
| 15-minute call with founder    | Reply to the welcome email with a time. |

We owe you 15 minutes back for every hour you
spent on this. Cash it in.

---

## Coming back later

If you uninstall and want to try again in a few
months:

1. Grab the latest `Recall-Setup-lite.exe`.
2. Run it.
3. If you kept `~/.recall/`, your history is
   still there — Recall will pick up where you
   left off.

We don't track who came back. There's no
re-onboarding flow. You're just a user.

---

## A note from the founder

The hardest data point to get is *"why you
left."* If you have 30 seconds, the single most
useful sentence you can write is:

> "Recall did X but I needed Y, so it didn't
> fit."

Or:

> "Recall worked, but I never built the habit of
> opening it."

Or:

> "Recall scared me about Z (privacy /
> performance / scope) and I didn't trust it."

Any of those move us forward. Vague reasons
don't.

Thank you for the time you gave us.
