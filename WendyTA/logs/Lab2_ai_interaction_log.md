# Lab 2 AI Interaction Log - Interactive Prototyping with Raspberry Pi

This file automatically logs all significant interactions between students and WendyTA (GitHub Copilot Chat) during Lab 2.

## How to Use This Log
- **Automatic**: WendyTA appends entries when providing substantial help
- **Timestamped**: Each interaction includes date/time in YYYY-MM-DD HH:MM:SS format
- **Commit Required**: Students must commit this file with their lab submission
- **Attribution**: Reference this log in your Lab 2 README.md under "AI Usage"

## Log Entries
*Interactions will be automatically appended below with timestamps*

---

## [2025-09-22 11:30:00] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: suggested change to `Lab 2/pizza_clock.py` (display fallback on SPI errors); student made manual edits to `Lab 2/pizza_clock.py` during the session.
- **AI-Generated Code**: A display-fallback strategy and guidance for chunked SPI transfers and diagnostic tests were provided; no persistent README change was left in place at student's request.
- **Student Modifications**: Student unplugged and re-seated the display hardware which immediately resolved the ioctl timeout; student chose not to keep the README edit and requested this entry be added to the interaction log.

### Interaction Summary
- **Questions Asked**: Why am I seeing "ioctl timeout" when writing to the SPI display? Will changing baudrate help? Can we document the hardware fix?
- **Answers Provided**: Explained that ioctl timeouts are usually caused by either overly large SPI transfers or flaky hardware connections; gave prioritized fixes (lower baudrate, split transfers, re-seat hardware, inspect dmesg). Offered a non-invasive code fallback to retry with smaller images and described chunked-transfer approach.
- **Outcome**: Student unplugged and re-plugged the display; the device recovered and the timeout disappeared. Student asked the assistant to record the hardware fix in the Lab 2 AI interaction log.

### Next Steps
- Student should commit this log entry with their Lab 2 submission and, if desired, add a brief note to `Lab 2/README.md` describing the hardware fix under a "Troubleshooting" section.

---

## [2025-09-21 14:20:00] - Session Entry
**AI Assistant**: GitHub Copilot Chat (WendyTA)

### Code Changes
- **Files Modified**: `Lab 2/gif_player_pil.py`, `Lab 2/GIF_PLAY.md`
- **AI-Generated Code**: Example GIF player (Pillow to decode GIF frames, pygame to display); README with install/run notes.
- **Student Modifications**: Student requested a how-to explanation without full code for playing GIFs with only PIL.

### Interaction Summary
- **Questions Asked**: Can I play a GIF on Raspberry Pi with PIL only? How to do it (no code requested)?
- **Answers Provided**: Explained that Pillow (PIL) can decode GIF frames and read per-frame durations, but it doesn't provide a display/timing loop for playback; recommended options: use a display library (pygame, tkinter, or write to framebuffer) or implement your own loop that reads frames and drives the framebuffer. Described headless framebuffer notes and SDL_VIDEODRIVER hints.
- **Learning Objectives**: Student learned the separation between decoding (PIL) and display/timing; how to extract frames/durations and approaches to display them on Pi.

### Next Steps
- Student will use this explanation to implement playback themselves or ask for a lightweight CLI wrapper if they want.

---
