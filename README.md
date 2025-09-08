# VMware VM Monitor Event ID 2004

A Python-based monitoring system that automatically detects Windows Event ID 2004 (Resource Exhaustion Detector) in VMware VMs and restarts affected VMs when the event occurs within the last minute.

## Features

- **Automatic VM Detection**: Discovers all powered-on VMware VMs
- **Event Monitoring**: Monitors Windows Event Viewer for Event ID 2004
- **Smart Restart**: Automatically restarts VMs when resource exhaustion is detected
- **Enhanced Restart Logic**: Retry mechanism with lock file handling to prevent VM restart errors
- **Configurable**: Customizable monitoring intervals, thresholds, and retry settings
- **Environment Variables**: Override all settings via environment variables
- **Logging**: Comprehensive logging for monitoring and debugging
- **Safe Operations**: Uses vmrun for reliable VM management

## Requirements

### System Requirements
- Windows operating system
- Python 3.7 or higher
- VMware Workstation or VMware Player installed
- Administrator privileges (for VM operations)

### VMware Requirements
- VMware Workstation Pro/Player with `vmrun` utility
- VMs must be running Windows with Event Viewer accessible
- VMs should have VMware Tools installed for optimal functionality

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BrayAlter/VMware-EventID-2004-Detector.git
   cd VMware-EventID-2004-Detector
   ```

2. **Install Python dependencies** (optional, uses mostly standard library):
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify VMware installation**:
   - Ensure `vmrun.exe` is accessible in your PATH or in standard VMware installation directories
   - Test with: `vmrun list`

## Configuration

### Basic Configuration
Edit `config.py` to customize monitoring behavior:

```python
class Config:
    CHECK_INTERVAL = 60                    # Check VMs every 60 seconds
    RESTART_TIME_THRESHOLD_MINUTES = 2     # Only restart if event is within last 2 minutes
    RESTART_DELAY = 5                      # Wait 5 seconds between stop/start
    RESTART_MAX_RETRIES = 3                # Maximum restart attempts
    RESTART_RETRY_DELAY = 10               # Delay between restart retries (seconds)
    LOCK_FILE_CLEANUP_DELAY = 5            # Wait time for lock file cleanup (seconds)
    VMRUN_TIMEOUT = 120                    # Timeout for vmrun commands
```

### Environment Variables
You can override settings using environment variables:

```bash
set CHECK_INTERVAL=30
set RESTART_TIME_THRESHOLD_MINUTES=2
set LOG_LEVEL=DEBUG
set DRY_RUN=true
```

### Available Environment Variables
- `CHECK_INTERVAL`: How often to check VMs (seconds)
- `RESTART_TIME_THRESHOLD_MINUTES`: Event detection window (minutes)
- `RESTART_DELAY`: Delay between VM stop/start (seconds)
- `RESTART_MAX_RETRIES`: Maximum restart attempts (default: 3)
- `RESTART_RETRY_DELAY`: Delay between restart retries in seconds (default: 10)
- `LOCK_FILE_CLEANUP_DELAY`: Wait time for lock file cleanup in seconds (default: 5)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DRY_RUN`: Test mode - don't actually restart VMs (true/false)
- `DEBUG_MODE`: Enable debug output (true/false)

## Usage

### Basic Usage
Run the monitor with default settings:
```bash
python main.py
```

### Test Mode
Run in dry-run mode to test without restarting VMs:
```bash
set DRY_RUN=true
python main.py
```

### Debug Mode
Run with detailed logging:
```bash
set LOG_LEVEL=DEBUG
python main.py
```

## How It Works

1. **VM Discovery**: Uses `vmrun list` to find all powered-on VMs
2. **Event Checking**: For each VM, checks Windows Event Viewer for Event ID 2004
3. **Time Window**: Only considers events from the last 2 minutes (configurable)
4. **Restart Logic**: If Event ID 2004 is found, performs a soft restart with retry logic and lock file handling
5. **Monitoring Loop**: Repeats the process every minute (configurable)

### Event ID 2004 Details
Event ID 2004 is typically found in:
- `Microsoft-Windows-Diagnostics-Performance/Operational`
- `Microsoft-Windows-Resource-Exhaustion-Detector/Operational`
- `System` log
- `Application` log

This event indicates resource exhaustion issues that may require a VM restart.

## File Structure

```
VMware-EventID-2004-Detector/
├── main.py              # Main execution script
├── vm_manager.py        # VM operations using vmrun
├── event_checker.py     # Windows Event Viewer monitoring
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── CONFIG_README.md    # Detailed configuration documentation
├── README.md          # This file
├── .gitignore          # Git ignore rules
├── capture/            # Event count files (auto-generated)
└── vmware_monitor.log # Log file (created at runtime)
```

## Logging

The application creates detailed logs in `vmware_monitor.log`:
- VM discovery and status
- Event detection results
- Restart operations
- Error conditions

Log levels:
- `INFO`: Normal operations
- `WARNING`: Event ID 2004 detected
- `ERROR`: Failed operations
- `DEBUG`: Detailed diagnostic information

## Troubleshooting

### Common Issues

1. **"vmrun executable not found"**
   - Ensure VMware Workstation/Player is installed
   - Add VMware installation directory to PATH
   - Check `config.py` VMWARE_PATHS for correct paths

2. **"Failed to get VM list"**
   - Run as Administrator
   - Ensure VMs are powered on
   - Check VMware services are running

3. **"Event checking failed"**
   - Ensure VMs are running Windows
   - Verify VMware Tools are installed
   - Check VM network connectivity

4. **"Permission denied"**
   - Run PowerShell/Command Prompt as Administrator
   - Check Windows UAC settings
   - Verify VM file permissions

### Debug Steps

1. **Test VM detection**:
   ```bash
   vmrun list
   ```

2. **Test event detection**:
   ```python
   from event_checker import EventChecker
   checker = EventChecker()
   checker.test_event_detection()
   ```

3. **Enable debug logging**:
   ```bash
   set LOG_LEVEL=DEBUG
   set DEBUG_MODE=true
   python main.py
   ```

## Security Considerations

- Run with minimum required privileges
- Store VM credentials securely (use environment variables)
- Monitor log files for sensitive information
- Consider network security for remote VM access

## Limitations

- Currently supports Windows VMs only
- Requires VMware Workstation/Player (not vSphere)
- Event checking requires guest OS access
- May require VM credentials for remote event checking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Create an issue on GitHub with:
   - Operating system version
   - VMware version
   - Python version
   - Error messages and logs

## Changelog

### v1.1.0
- Enhanced restart logic with retry mechanism
- Lock file handling to prevent VM restart errors
- New configuration options: RESTART_MAX_RETRIES, RESTART_RETRY_DELAY, LOCK_FILE_CLEANUP_DELAY
- Updated environment variable names (removed VM_ prefix)
- Added CONFIG_README.md for detailed configuration documentation
- Improved error handling and logging
- Added .gitignore files for cleaner repository

### v1.0.0
- Initial release
- Basic VM monitoring and restart functionality
- Event ID 2004 detection
- Configurable monitoring intervals
- Comprehensive logging