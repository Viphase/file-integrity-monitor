# **File-Integrity-Monitor (FIM)**

- ## status:

  - **`In development ⚙️`**
  - [x] File hash calculation (SHA-256)
  - [x] Periodic file system scan
  - [x] Real-time monitoring (watchdog)
  - [x] File create / modify / delete detection
  - [x] SQLite database storage
  - [x] Logging system
  - [ ] Telegram notifications
  - [ ] Email notifications

---

- ## description

  - A lightweight **File Integrity Monitoring (FIM)** utility written in Python.

  - The program, that monitors selected files and directories and can detect **unauthorized file changes** using cryptographic hash comparison and real-time filesystem events.

  > The utility creates a database of file hashes and continuously monitors the system.  
  > When a file is created, modified, or deleted, the event is logged and an alert can be sent to the administrator via telegram or email.

  - Supported events:
    - File creation 📄
    - File modification ✏️
    - File deletion 🗑️

  - Monitoring methods:
    - Real-time event monitoring (`watchdog`)
    - Periodic full directory scan

---

- ## installation & use

  0. You need to have `Python 3.8+` and `pip` installed
  1. Open terminal and clone the repository:
     ```
     git clone https://github.com/your-username/file-integrity-monitor.git
     cd FileIntegrityMonitor
     ```
  2. Create and activate virtual environment  

     **macOS / Linux**
     ```
     python -m venv .venv
     source .venv/bin/activate
     ```

     **Windows**
     ```
     python -m venv .venv
     .\.venv\Scripts\activate
     ```

  3. Install dependencies:
     ```
     pip install -r requirements.txt
     ```
  4. Configure monitoring settings in `config.json`
  5. Run the program!
     ```
     python run_fim.py
     ```

---

- ## configuration

  - Main configuration file: **`config.json`**

  - Key parameters:
    - `paths` — directories to monitor
    - `file_masks` — file patterns (`*.py`, `*.txt`, etc., `*` - for all files)
    - `scan_interval_seconds` — periodic scan interval
    - `hash_algorithm` — hash algorithm (default: `sha256`)
    - `alerts` — notification settings (Telegram / Email)

---

- ## examples

  * Example 1 — file modification detected:
    ```text
    WARNING modified /home/user/project/main.py
    ```

  * Example 2 — file deletion detected:
    ```text
    WARNING deleted /home/user/project/config.yaml
    ```

---