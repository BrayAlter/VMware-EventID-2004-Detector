# VMware VM Monitor

A Python-based monitoring system that automatically detects Windows Event ID 2004 (Resource Exhaustion Detector) in VMware VMs and restarts affected VMs when the event occurs within the last minute.

## Features

- **Automatic VM Detection**: Discovers all powered-on VMware VMs
- **Event Monitoring**: Monitors Windows Event Viewer for Event ID 2004
- **Smart Restart**: Automatically restarts VMs when resource exhaustion is detected
- **Configurable**: Customizable monitoring intervals and settings
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
   git clone https://github.com/yourusername/vmware-monitor.git
   cd vmware-monitor
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
    CHECK_INTERVAL = 60          # Check VMs every 60 seconds
    EVENT_CHECK_MINUTES = 1      # Look for events in last 1 minute
    RESTART_DELAY = 5           # Wait 5 seconds between stop/start
    VMRUN_TIMEOUT = 120         # Timeout for vmrun commands
```

### Environment Variables
You can override settings using environment variables:

```bash
set VM_CHECK_INTERVAL=30
set VM_EVENT_CHECK_MINUTES=2
set VM_LOG_LEVEL=DEBUG
set VM_DRY_RUN=true
```

### Available Environment Variables
- `VM_CHECK_INTERVAL`: How often to check VMs (seconds)
- `VM_EVENT_CHECK_MINUTES`: Event detection window (minutes)
- `VM_RESTART_DELAY`: Delay between VM stop/start (seconds)
- `VM_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `VM_DRY_RUN`: Test mode - don't actually restart VMs (true/false)
- `VM_DEBUG_MODE`: Enable debug output (true/false)

## Usage

### Basic Usage
Run the monitor with default settings:
```bash
python main.py
```

### Test Mode
Run in dry-run mode to test without restarting VMs:
```bash
set VM_DRY_RUN=true
python main.py
```

### Debug Mode
Run with detailed logging:
```bash
set VM_LOG_LEVEL=DEBUG
python main.py
```

## How It Works

1. **VM Discovery**: Uses `vmrun list` to find all powered-on VMs
2. **Event Checking**: For each VM, checks Windows Event Viewer for Event ID 2004
3. **Time Window**: Only considers events from the last minute (configurable)
4. **Restart Logic**: If Event ID 2004 is found, performs a soft restart of the VM
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
vmware-monitor/
├── main.py              # Main execution script
├── vm_manager.py        # VM operations using vmrun
├── event_checker.py     # Windows Event Viewer monitoring
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
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
   set VM_LOG_LEVEL=DEBUG
   set VM_DEBUG_MODE=true
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

### v1.0.0
- Initial release
- Basic VM monitoring and restart functionality
- Event ID 2004 detection
- Configurable monitoring intervals
- Comprehensive logging