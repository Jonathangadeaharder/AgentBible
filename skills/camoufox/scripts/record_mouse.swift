// macOS CGEvent tap recorder — captures all mouse events globally.
// Compile: swiftc -O -o /tmp/record_mouse record_mouse.swift
// Run: /tmp/record_mouse output.json &
// Kill: kill -INT <pid>  (saves JSON on SIGINT)
//
// Output: JSON array of {t, type, x, y} where:
//   t = milliseconds since start
//   type = "move" | "down" | "drag" | "up"
//   x, y = screen coordinates (top-left origin)
//
// Used for recording real human mouse trajectories to replay via CDP.

import Cocoa
import Foundation

var events: [[String: Any]] = []
let startTime = Date()
var running = true

signal(SIGINT) { _ in
    running = false
    CFRunLoopStop(CFRunLoopGetCurrent())
}

let callback: CGEventTapCallBack = { proxy, type, event, refcon in
    let elapsed = Date().timeIntervalSince(startTime) * 1000
    let location = event.location

    var eventType = "other"
    switch type {
    case .mouseMoved: eventType = "move"
    case .leftMouseDown: eventType = "down"
    case .leftMouseDragged: eventType = "drag"
    case .leftMouseUp: eventType = "up"
    default: return Unmanaged.passUnretained(event)
    }

    events.append([
        "t": round(elapsed * 10) / 10,
        "type": eventType,
        "x": Int(location.x),
        "y": Int(location.y),
    ])

    if events.count % 10 == 0 {
        FileHandle.standardError.write(" \(events.count) events\r".data(using: .utf8)!)
    }

    return Unmanaged.passUnretained(event)
}

guard let tap = CGEvent.tapCreate(
    tap: .cgSessionEventTap,
    place: .headInsertEventTap,
    options: .listenOnly,
    eventsOfInterest: CGEventMask(1 << CGEventType.mouseMoved.rawValue |
                                   1 << CGEventType.leftMouseDown.rawValue |
                                   1 << CGEventType.leftMouseDragged.rawValue |
                                   1 << CGEventType.leftMouseUp.rawValue),
    callback: callback,
    userInfo: nil
) else {
    print("ERROR: Could not create CGEvent tap. Need Accessibility permission.")
    exit(1)
}

let source = CFMachPortCreateRunLoopSource(nil, tap, 0)
CFRunLoopAddSource(CFRunLoopGetCurrent(), source, .commonModes)
CGEvent.tapEnable(tap: tap, enable: true)

print("Recording mouse events. Press Ctrl+C when done.")
fflush(stdout)

CFRunLoopRun()

let outputPath = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/mouse_trajectory.json"
let data = try! JSONSerialization.data(withJSONObject: events, options: .prettyPrinted)
try! data.write(to: URL(fileURLWithPath: outputPath))
print("\nSaved \(events.count) events to \(outputPath)")
