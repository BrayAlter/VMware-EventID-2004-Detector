# Configuration Options

The VM monitoring system supports multiple configuration methods:

## Configuration Priority

Settings are loaded in this order (highest priority first):
1. **Environment Variables** (highest priority)
2. **YAML Configuration** (`config.yaml`) 
3. **Default Values** (in `config.py`)

## YAML Configuration (Recommended)

Create a `config.yaml` file in the same directory as `main.exe` (or the script directory) to configure the application:

```yaml
# VM Credentials
vm_username: "your_vm_username"
vm_password: "your_vm_password"

# Timing Settings (in seconds)
check_interval: 60          # How often to check VMs
event_check_minutes: 1      # Check for events in the last N minutes
restart_delay: 5            # Seconds to wait between stop and start
vmrun_timeout: 30           # Timeout for vmrun commands

# Restart Behavior
restart_time_threshold_minutes: 2  # Only restart if event is within this many minutes
restart_max_retries: 3             # Maximum retry attempts for restart operations
restart_retry_delay: 10            # Seconds to wait between restart retries
lock_file_cleanup_delay: 15        # Extra wait time for VMware lock files to clear

# File Paths
capture_folder: "capture"          # Folder for temporary event count files

# Logging
log_level: "INFO"           # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_file: "vmware_monitor.log"

# Performance
max_concurrent_checks: 5    # Maximum number of VMs to check simultaneously
retry_attempts: 3           # Number of retry attempts for failed operations
retry_delay: 10             # Seconds to wait between retry attempts

# Debug Options
debug_mode: false           # Enable debug logging and additional output
dry_run: false              # If true, don't actually restart VMs (for testing)
```

### YAML Configuration Notes
- File must be named exactly `config.yaml`
- Place in the same directory as `main.exe` (for releases) or script directory (for development)
- Keys are case-insensitive
- Boolean values: `true`/`false` (lowercase)
- String values should be quoted
- Comments start with `#`

## Legacy Configuration (config.py)

Alternatively, you can modify settings directly in `config.py`:

## Key Configuration Parameters

### RESTART_TIME_THRESHOLD_MINUTES
- **Default**: 2 minutes
- **Purpose**: Only restart VMs if Event ID 2004 occurred within this time window
- **Example**: If set to 2, only events ≤2 minutes old will trigger a restart

### CHECK_INTERVAL
- **Default**: 60 seconds
- **Purpose**: Sleep time between monitoring cycles
- **Example**: System waits this many seconds before starting the next scan

### RESTART_MAX_RETRIES
- **Default**: 3 attempts
- **Purpose**: Maximum number of restart attempts if lock files cause failures
- **Example**: System will try up to 3 times to restart a VM

### RESTART_RETRY_DELAY
- **Default**: 10 seconds
- **Purpose**: Wait time between restart retry attempts
- **Example**: After a failed restart, wait 10 seconds before trying again

### LOCK_FILE_CLEANUP_DELAY
- **Default**: 15 seconds
- **Purpose**: Extra wait time for VMware lock files to clear
- **Example**: Total wait = RESTART_DELAY (5s) + LOCK_FILE_CLEANUP_DELAY (15s) = 20s

### CAPTURE_FOLDER
- **Default**: "capture"
- **Purpose**: Folder name for temporary event count files (relative to project root)
- **Example**: Files like "event_count_VM1.txt" are stored in this folder

## Environment Variable Override

All settings can be overridden using environment variables (highest priority):
- `VM_USERNAME`
- `VM_PASSWORD`
- `CHECK_INTERVAL`
- `RESTART_TIME_THRESHOLD_MINUTES`
- `RESTART_MAX_RETRIES`
- `RESTART_RETRY_DELAY`
- `LOCK_FILE_CLEANUP_DELAY`
- `CAPTURE_FOLDER`
- `LOG_LEVEL`
- `DEBUG_MODE`
- `DRY_RUN`

## Example Usage

### Using YAML Configuration
```yaml
# config.yaml
check_interval: 30
restart_time_threshold_minutes: 2
log_level: "DEBUG"
```

### Using Environment Variables
```bash
# Override YAML settings with environment variables
set RESTART_TIME_THRESHOLD_MINUTES=2
set CHECK_INTERVAL=30
set LOG_LEVEL=DEBUG
python main.py
```

### Mixed Configuration
```bash
# Use YAML for most settings, environment variables for sensitive data
set VM_USERNAME=admin
set VM_PASSWORD=secret123
python main.py
```

## Log Output Examples

- `[RESTART] Event too old (15.9 min > 1 min), skipping restart`
- `[WAIT] Sleeping for 60 seconds until next cycle...`

Both messages now use the configurable values from `config.py`.