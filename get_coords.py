#!/usr/bin/env python3
"""
Quick coordinate capture tool.
Hover your mouse over a button, then press Enter to print its coordinates.
Run from the terminal alongside your open windows.

Usage:
    python get_coords.py
"""
import pyautogui
import time

def capture(label):
    input(f"\n  → Hover your mouse over the [{label}] then press Enter: ")
    x, y = pyautogui.position()
    print(f"     {label}: x={x}, y={y}")
    return x, y

print("=" * 55)
print("  Loggy3 Coordinate Capture")
print("  Screen resolution:", pyautogui.size())
print("=" * 55)
print("\nOpen Loggy3 and YouTube now, then follow the prompts.\n")

start_x,    start_y    = capture("Loggy3 START button")
stop_x,     stop_y     = capture("Loggy3 STOP button")
minimize_x, minimize_y = capture("Loggy3 MINIMIZE (-) icon  [top-right corner of app]")

print("\n" + "=" * 55)
print("  Paste these into your .env file:")
print("=" * 55)
print(f"START_BUTTON_X={start_x}")
print(f"START_BUTTON_Y={start_y}")
print(f"STOP_BUTTON_X={stop_x}")
print(f"STOP_BUTTON_Y={stop_y}")
print(f"MINIMIZE_BUTTON_X={minimize_x}")
print(f"MINIMIZE_BUTTON_Y={minimize_y}")
print()

# Also print window titles
import subprocess
result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
if result.stdout.strip():
    print("Open windows (copy the Loggy3 and YouTube titles):")
    print("-" * 55)
    for line in result.stdout.strip().split('\n'):
        parts = line.split(None, 3)
        if len(parts) >= 4:
            print(f"  {parts[3]}")
    print()
