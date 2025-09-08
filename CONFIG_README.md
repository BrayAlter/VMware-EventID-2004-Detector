# Configuration Options

The VM monitoring system now supports configurable settings in `config.py`:

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

All settings can be overridden using environment variables:
- `RESTART_TIME_THRESHOLD_MINUTES`
- `CHECK_INTERVAL`
- `RESTART_MAX_RETRIES`
- `RESTART_RETRY_DELAY`
- `LOCK_FILE_CLEANUP_DELAY`
- `CAPTURE_FOLDER`

## Example Usage

```bash
# Set restart threshold to 2 minutes and cycle interval to 30 seconds
set RESTART_TIME_THRESHOLD_MINUTES=2
set CHECK_INTERVAL=30
python main.py
```

## Log Output Examples

- `[RESTART] Event too old (15.9 min > 1 min), skipping restart`
- `[WAIT] Sleeping for 60 seconds until next cycle...`

Both messages now use the configurable values from `config.py`.