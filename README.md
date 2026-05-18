# Google Drive Cleanup & File Management System

## Problem Statement

Built a Python-based Google Drive Cleanup & File Management System to automate deletion of old files, detect duplicate files, and manage Drive storage efficiently for large collections of auto-generated PDF reports stored inside nested client folders.

---

# Features

- Secure Google Drive authentication using OAuth 2.0
- List all Drive files and folders
- Upload files directly to Google Drive
- Automatically clean files older than a selected duration
- Duplicate file detection using:
  - File name matching
  - MD5 checksum/content matching
- Safe deletion using Trash support
- Preview mode before deletion
- GUI-based desktop interface
- Support for nested client report folders

---

# Existing File Structure

```text
drive_cleanup/
│
├── cleanup.py
├── drive_gui.py
├── find_duplicates.py
├── credentials.json
├── token.pickle
│
├── secrets/
│   ├── client secrets
│   └── token files
```

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core backend logic |
| Google Drive API v3 | Google Drive operations |
| OAuth 2.0 | Authentication |
| Tkinter | Desktop GUI |
| tkcalendar | Calendar/date selection |
| Google API Client Library | API communication |
| MD5 Hashing | Duplicate detection |
| Threading | Non-blocking GUI operations |

---

# Real-World Problem Solved

Managing thousands of auto-generated PDF reports manually inside Google Drive was:

- repetitive
- time-consuming
- error-prone
- difficult to monitor at scale

This project automated:

- old file cleanup
- duplicate report detection
- storage management
- retention policy handling
- large-scale Drive maintenance

for nested client-based report directories.

# Functionalities

- Authenticate with Google Drive
- List Drive files
- Upload files
- Delete old files
- Preview cleanup before deletion
- Move files to Trash
- Detect duplicate files
- Handle nested Drive folders
- GUI-based interaction

---

---

# In Short

Developed a modular Python-based Google Drive management tool with automated cleanup, duplicate detection, and GUI-based storage administration using Google Drive API and OAuth authentication.

---
