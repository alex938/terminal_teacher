# Terminal Teacher

Display your terminal commands in real-time to students via web browser.

## Quick Start

### 1. Start Server
```bash
docker compose up --build -d
```

Server runs on **port 7777**

### 2. Setup Terminal Capture
```bash
export ADMIN_PASSWORD='teacher123'
./setup_terminal_capture.sh
source ~/.bashrc
```

### 3. Share with Students
Find your IP:
```bash
hostname -I
```

Students visit: **`http://YOUR_IP:7777`**

### 4. Start Teaching
Type commands normally - they appear on student screens automatically!

## Teacher Panel

Login at: **`http://localhost:7777/admin-panel/`**

Password: Your `ADMIN_PASSWORD` from step 2

**Features:**
- Delete commands
- Bulk delete (checkboxes)
- Clear session
- Nuke database (Clear Session → Cancel → Confirm)
- Manual command entry
- Auto-refresh

## Configuration

Edit `.env` file:
```bash
ADMIN_PASSWORD=your-password
DJANGO_SECRET_KEY=generate-random-key
ALLOW_ALL_HOSTS=true
```

## Cleanup

Remove terminal capture:
```bash
./remove_terminal_capture.sh
```

Stop server:
```bash
docker compose down
```

Delete everything:
```bash
docker compose down -v
```

## Ports & Access

- **Server**: `http://localhost:7777`
- **Student View**: `http://YOUR_IP:7777`  
- **Admin Panel**: `http://YOUR_IP:7777/admin-panel/`

## Requirements

- Docker & Docker Compose
- Bash terminal
- Network connection

---

**That's it!** Type commands → Students see them in real-time.
