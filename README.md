# Terminal Teacher

Display your terminal commands in real-time to students via web browser.

### Why:
I created this small application to mirror only the commands I type into a live web interface. Since I teach a lot of Linux and networking, it helps me share commands with students in real time. They can quickly open the student panel and see each command as it’s entered, without me needing to scroll back through the terminal or repeat myself. This makes it much easier for students to keep up and follow along during lessons.

### Quick Setup once container is running:
![setup1](https://github.com/user-attachments/assets/e31af0ca-3ee1-4e13-80e6-87b9f156f9d0)

### Commands sent to Terminal Teacher:
![setup2](https://github.com/user-attachments/assets/3a43c278-a326-4f19-8334-cdebc8680c21)

### Teacher Panel:
![setup3](https://github.com/user-attachments/assets/442ba0df-1a8a-4f6e-8165-84a9b00294c0)

### Student View:
![setup4](https://github.com/user-attachments/assets/d51e43b1-4f64-4c33-984d-614ff84c673d)

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
