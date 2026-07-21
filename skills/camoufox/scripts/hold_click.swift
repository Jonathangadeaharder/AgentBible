import CoreGraphics
import Foundation

// Swift CGEvent press-and-hold script for PerimeterX "PRESS & HOLD" captcha.
//
// Usage:
//   1. Focus Chrome via cua-driver: `~/.local/bin/cua-driver call bring_to_front '{"app_name": "Google Chrome"}'`
//   2. Screenshot to find the PRESS & HOLD button position (it's in a PX iframe invisible to AX tree)
//   3. Edit the `point` coordinates below to match the button center on screen
//   4. Compile: swiftc -O -o /tmp/hold_click /path/to/hold_click.swift
//   5. Run: /tmp/hold_click
//
// The script posts CGEvent leftMouseDown + 5 seconds of leftMouseDragged with 2px random jitter,
// then leftMouseUp. PX checks for continuous mouse-down duration + movement entropy (jitter).
// Without jitter, PX rejects the hold as robotic.
//
// Tested on Skyscanner.de PerimeterX captcha (2026-06-29).
// PX appId: PXrf8vapwA

let point = CGPoint(x: 726, y: 613)  // EDIT: button screen position

// Move to button position
CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: point, mouseButton: .left)?.post(tap: .cghidEventTap)

// Mouse down — start the hold
let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left)
down?.post(tap: .cghidEventTap)

// Hold for 5 seconds with 2px random jitter every 100ms
// PX checks for movement entropy during the hold — no jitter = rejected
for _ in 0..<50 {
    Thread.sleep(forTimeInterval: 0.1)
    let jitter = CGPoint(
        x: point.x + CGFloat.random(in: -2...2),
        y: point.y + CGFloat.random(in: -2...2)
    )
    let drag = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDragged, mouseCursorPosition: jitter, mouseButton: .left)
    drag?.post(tap: .cghidEventTap)
}

// Mouse up — release the hold
let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left)
up?.post(tap: .cghidEventTap)

print("Done: held for 5s with jitter")
