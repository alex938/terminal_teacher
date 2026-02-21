#!/bin/bash
# Setup script to capture terminal commands and send to Terminal Teacher

# Configuration
SERVER_URL="${TEACHER_SERVER_URL:-http://localhost:7777}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"

# Check if password is set
if [ -z "$ADMIN_PASSWORD" ]; then
    echo "Error: ADMIN_PASSWORD environment variable must be set"
    echo "Example: export ADMIN_PASSWORD='your-password-here'"
    exit 1
fi

# Create the capture function - simpler approach without duplicate checking
# Let the server handle any duplicates if needed
CAPTURE_FUNC="
# Terminal Teacher - Command Capture
TEACHER_SERVER_URL=\"$SERVER_URL\"
TEACHER_ADMIN_PASSWORD=\"$ADMIN_PASSWORD\"

__terminal_teacher_capture() {
    # Get the last command from history
    local cmd=\$(HISTTIMEFORMAT= history 1 | sed 's/^[ ]*[0-9]*[ ]*//')
    
    # Skip empty commands
    [ -z \"\$cmd\" ] && return
    
    # Skip the capture function itself
    [[ \"\$cmd\" == *\"__terminal_teacher_capture\"* ]] && return
    
    
    # Send to server in background subshell (no job control)
    (
        exec 0</dev/null
        exec 1>/dev/null
        exec 2>/dev/null
        curl -s -X POST \"\${TEACHER_SERVER_URL}/api/submit/\" \\
            -H \"Authorization: Bearer \${TEACHER_ADMIN_PASSWORD}\" \\
            --data-urlencode \"command=\${cmd}\" &
    ) &
    disown
}

# Only add to PROMPT_COMMAND if not already there
if [[ \"\$PROMPT_COMMAND\" != *\"__terminal_teacher_capture\"* ]]; then
    export PROMPT_COMMAND=\"\${PROMPT_COMMAND:+\$PROMPT_COMMAND; }__terminal_teacher_capture\"
fi
"

# Check if already installed
if grep -q "__terminal_teacher_capture" ~/.bashrc 2>/dev/null; then
    echo "Terminal Teacher capture is already installed in ~/.bashrc"
    echo "To reinstall, remove the relevant section from ~/.bashrc first"
    exit 0
fi

# Add to .bashrc
echo "" >> ~/.bashrc
echo "# Terminal Teacher - Auto-capture commands" >> ~/.bashrc
echo "$CAPTURE_FUNC" >> ~/.bashrc

echo "✅ Terminal Teacher capture installed!"
echo ""
echo "To activate in current terminal:"
echo "  source ~/.bashrc"
echo ""
echo "Or open a new terminal window."
echo ""
echo "Configuration:"
echo "  Server URL: $SERVER_URL"
echo "  Password: [hidden]"
echo ""
echo "To uninstall, remove the 'Terminal Teacher' section from ~/.bashrc"
