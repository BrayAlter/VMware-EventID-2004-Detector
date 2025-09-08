#!/usr/bin/env python3
"""
Configuration Settings
Centralized configuration for VMware VM Monitor.
"""

class Config:
    """Configuration constants for the VMware VM Monitor"""
    
    # Monitoring intervals (in seconds)
    CHECK_INTERVAL = 60  # How often to check VMs (60 seconds = 1 minute)
    
    # Event checking settings
    EVENT_CHECK_MINUTES = 1  # Check for events in the last N minutes
    EVENT_ID = 2004  # Windows Event ID to monitor
    
    # VM restart settings
    RESTART_DELAY = 5  # Seconds to wait between stop and start
    RESTART_TIME_THRESHOLD_MINUTES = 2  # Only restart if event is within this many minutes
    RESTART_MAX_RETRIES = 3  # Maximum retry attempts for restart operations
    RESTART_RETRY_DELAY = 10  # Seconds to wait between restart retries
    LOCK_FILE_CLEANUP_DELAY = 15  # Extra seconds to wait for lock files to clear
    
    # vmrun command timeout (in seconds)
    VMRUN_TIMEOUT = 30  # 30 seconds timeout for vmrun commands
    
    # Logging settings
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = "vmware_monitor.log"
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Event log names to check (in order of preference)
    EVENT_LOG_NAMES = [
        "Microsoft-Windows-Diagnostics-Performance/Operational",
        "Microsoft-Windows-Resource-Exhaustion-Detector/Operational",
        "System",
        "Application"
    ]
    
    # VMware installation paths (for finding vmrun)
    VMWARE_PATHS = [
        r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
        r"C:\Program Files\VMware\VMware Workstation\vmrun.exe",
        r"C:\Program Files (x86)\VMware\VMware Player\vmrun.exe",
        r"C:\Program Files\VMware\VMware Player\vmrun.exe"
    ]
    
    # vmrun executable path (will be set dynamically)
    VMRUN_PATH = None
    
    # Capture folder for temporary files
    CAPTURE_FOLDER = "capture"  # Relative to project root
    
    # PowerShell execution settings
    POWERSHELL_TIMEOUT = 30  # Timeout for PowerShell commands
    POWERSHELL_EXECUTION_POLICY = "Bypass"
    
    # VM guest credentials (if needed for remote access)
    # Note: These should be set via environment variables in production
    VM_USERNAME = "your-vmware-username"  # Set via environment variable VM_USERNAME
    VM_PASSWORD = "your-vmware-password"  # Set via environment variable VM_PASSWORD
    
    # Advanced settings
    MAX_CONCURRENT_CHECKS = 5  # Maximum number of VMs to check simultaneously
    RETRY_ATTEMPTS = 3  # Number of retry attempts for failed operations
    RETRY_DELAY = 10  # Seconds to wait between retry attempts
    
    # Debug settings
    DEBUG_MODE = False  # Enable debug logging and additional output
    DRY_RUN = False  # If True, don't actually restart VMs (for testing)
    
    @classmethod
    def load_from_yaml(cls, config_path="config.yaml"):
        """Load configuration from YAML file"""
        import os
        import sys
        
        # Determine the config file path relative to executable/script
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        yaml_path = os.path.join(base_dir, config_path)
        
        if os.path.exists(yaml_path):
            try:
                import yaml
                with open(yaml_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data:
                    # Update class attributes from YAML
                    for key, value in config_data.items():
                        if hasattr(cls, key.upper()):
                            setattr(cls, key.upper(), value)
                        elif hasattr(cls, key):
                            setattr(cls, key, value)
                
                print(f"Configuration loaded from: {yaml_path}")
            except ImportError:
                print("PyYAML not installed. Install with: pip install pyyaml")
            except Exception as e:
                print(f"Error loading config.yaml: {e}")
        else:
            print(f"Config file not found: {yaml_path}")
    
    @classmethod
    def load_from_env(cls):
        """Load configuration from environment variables"""
        import os
        
        # Override with environment variables if they exist
        cls.CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', cls.CHECK_INTERVAL))
        cls.EVENT_CHECK_MINUTES = int(os.getenv('EVENT_CHECK_MINUTES', cls.EVENT_CHECK_MINUTES))
        cls.RESTART_DELAY = int(os.getenv('RESTART_DELAY', cls.RESTART_DELAY))
        cls.RESTART_TIME_THRESHOLD_MINUTES = int(os.getenv('RESTART_TIME_THRESHOLD_MINUTES', cls.RESTART_TIME_THRESHOLD_MINUTES))
        cls.RESTART_MAX_RETRIES = int(os.getenv('RESTART_MAX_RETRIES', cls.RESTART_MAX_RETRIES))
        cls.RESTART_RETRY_DELAY = int(os.getenv('RESTART_RETRY_DELAY', cls.RESTART_RETRY_DELAY))
        cls.LOCK_FILE_CLEANUP_DELAY = int(os.getenv('LOCK_FILE_CLEANUP_DELAY', cls.LOCK_FILE_CLEANUP_DELAY))
        cls.VMRUN_TIMEOUT = int(os.getenv('VM_VMRUN_TIMEOUT', cls.VMRUN_TIMEOUT))
        
        cls.LOG_LEVEL = os.getenv('VM_LOG_LEVEL', cls.LOG_LEVEL)
        cls.LOG_FILE = os.getenv('VM_LOG_FILE', cls.LOG_FILE)
        
        cls.VM_USERNAME = os.getenv('VM_USERNAME', cls.VM_USERNAME)
        cls.VM_PASSWORD = os.getenv('VM_PASSWORD', cls.VM_PASSWORD)
        
        cls.CAPTURE_FOLDER = os.getenv('CAPTURE_FOLDER', cls.CAPTURE_FOLDER)
        
        cls.DEBUG_MODE = os.getenv('VM_DEBUG_MODE', 'false').lower() == 'true'
        cls.DRY_RUN = os.getenv('VM_DRY_RUN', 'false').lower() == 'true'
        
        cls.MAX_CONCURRENT_CHECKS = int(os.getenv('VM_MAX_CONCURRENT_CHECKS', cls.MAX_CONCURRENT_CHECKS))
        cls.RETRY_ATTEMPTS = int(os.getenv('VM_RETRY_ATTEMPTS', cls.RETRY_ATTEMPTS))
        cls.RETRY_DELAY = int(os.getenv('VM_RETRY_DELAY', cls.RETRY_DELAY))
    
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        errors = []
        
        if cls.CHECK_INTERVAL < 10:
            errors.append("CHECK_INTERVAL must be at least 10 seconds")
        
        if cls.EVENT_CHECK_MINUTES < 1:
            errors.append("EVENT_CHECK_MINUTES must be at least 1 minute")
        
        if cls.VMRUN_TIMEOUT < 30:
            errors.append("VMRUN_TIMEOUT must be at least 30 seconds")
        
        if cls.MAX_CONCURRENT_CHECKS < 1:
            errors.append("MAX_CONCURRENT_CHECKS must be at least 1")
        
        if cls.RETRY_ATTEMPTS < 1:
            errors.append("RETRY_ATTEMPTS must be at least 1")
        
        if errors:
            raise ValueError("Configuration validation failed: " + "; ".join(errors))
    
    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)"""
        print("VMware VM Monitor Configuration:")
        print(f"  Check Interval: {cls.CHECK_INTERVAL} seconds")
        print(f"  Event Check Window: {cls.EVENT_CHECK_MINUTES} minutes")
        print(f"  Event ID: {cls.EVENT_ID}")
        print(f"  Restart Delay: {cls.RESTART_DELAY} seconds")
        print(f"  vmrun Timeout: {cls.VMRUN_TIMEOUT} seconds")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Log File: {cls.LOG_FILE}")
        print(f"  Debug Mode: {cls.DEBUG_MODE}")
        print(f"  Dry Run: {cls.DRY_RUN}")
        print(f"  Max Concurrent Checks: {cls.MAX_CONCURRENT_CHECKS}")
        print(f"  Retry Attempts: {cls.RETRY_ATTEMPTS}")
        print(f"  Retry Delay: {cls.RETRY_DELAY} seconds")

# Load configuration on import - YAML first, then environment variables
Config.load_from_yaml()
Config.load_from_env()