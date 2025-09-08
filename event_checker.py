#!/usr/bin/env python3
"""
Event Checker
Monitors Windows Event Viewer for Event ID 2004 in VMs.
"""

import subprocess
import logging
import json
from datetime import datetime, timedelta
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)

class EventChecker:
    """Checks Windows Event Viewer for Event ID 2004 in VMs"""
    
    def __init__(self):
        self.vm_manager = None  # Will be set if needed for IP resolution
        self.latest_event_time = None  # Latest Event ID 2004 timestamp
        self.vm_restart_times = {}  # Track restart times per VM to prevent duplicates
    
    def should_restart_vm(self, vm_path: str) -> bool:
        """
        Check if VM should be restarted based on recent events and restart history.
        Returns True if event is within 1 minute and VM hasn't been restarted for same event.
        """
        if not self.latest_event_time:
            return False
            
        try:
            # Parse the latest event time
            event_time = datetime.strptime(self.latest_event_time, '%Y-%m-%d %H:%M:%S')
            current_time = datetime.now()
            
            # Check if event is within configured time threshold
            time_diff = (current_time - event_time).total_seconds() / 60
            if time_diff > Config.RESTART_TIME_THRESHOLD_MINUTES:
                print(f"[RESTART] Event too old ({time_diff:.1f} min > {Config.RESTART_TIME_THRESHOLD_MINUTES} min), skipping restart")
                return False
                
            # Check if we already restarted for this event time
            vm_name = self._get_vm_name_from_path(vm_path)
            last_restart = self.vm_restart_times.get(vm_name)
            
            if last_restart and last_restart >= event_time:
                print(f"[RESTART] Already restarted for this event time, skipping")
                return False
                
            print(f"[RESTART] Event is recent ({time_diff:.1f} min ≤ {Config.RESTART_TIME_THRESHOLD_MINUTES} min), restart needed")
            return True
            
        except ValueError as e:
            print(f"[RESTART ERROR] Could not parse event time: {e}")
            return False
    
    def mark_vm_restarted(self, vm_path: str):
        """
        Mark that a VM has been restarted, storing the current time.
        """
        vm_name = self._get_vm_name_from_path(vm_path)
        self.vm_restart_times[vm_name] = datetime.now()
        print(f"[RESTART] Marked {vm_name} as restarted at {self.vm_restart_times[vm_name]}")
    
    def check_event_2004(self, vm_path: str, minutes_back: int = 1) -> bool:
        """
        Check if Event ID 2004 occurred in the VM within the specified time window.
        
        Args:
            vm_path: Path to the VM .vmx file
            minutes_back: How many minutes back to check for the event
            
        Returns:
            True if Event ID 2004 is found within the time window, False otherwise
        """
        vm_name = self._get_vm_name_from_path(vm_path)
        print(f"[EVENT CHECK] Checking {vm_name} for Event ID 2004 (last {minutes_back} minutes)")
        
        try:
            # Calculate the time window
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes_back)
            print(f"[TIME WINDOW] {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
            
            # Try different methods to check events
            methods = [
                self._check_via_vmrun_script,
                self._check_via_simple_fallback
            ]
            
            for method in methods:
                method_name = method.__name__.replace('_check_via_', '').replace('_', ' ').title()
                print(f"[METHOD] Trying {method_name}...")
                try:
                    result = method(vm_path, start_time, end_time)
                    if result is not None:
                        status = "FOUND" if result else "NOT FOUND"
                        print(f"[RESULT] Event ID 2004: {status}")
                        return result
                except Exception as e:
                    print(f"[ERROR] {method_name} failed: {str(e)}")
                    logger.debug(f"Method {method.__name__} failed: {str(e)}")
                    continue
            
            logger.warning(f"All event checking methods failed for VM: {vm_path}, assuming no events")
            return False
            
        except Exception as e:
            logger.error(f"Error checking Event ID 2004 for VM {vm_path}: {str(e)}")
            return False
    
    def _check_via_vmrun_script(self, vm_path: str, start_time: datetime, end_time: datetime) -> Optional[bool]:
        """
        Check events using vmrun to execute PowerShell directly in the VM.
        
        Args:
            vm_path: Path to the VM .vmx file
            start_time: Start time for event search
            end_time: End time for event search
            
        Returns:
            True if Event ID 2004 is found, False if not found, None if method fails
        """
        try:
            # Format times for PowerShell
            start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Create fixed filename per VM (overwrites previous)
            vm_name = self._get_vm_name_from_path(vm_path)
            temp_filename = f"event_count_{vm_name}.txt"
            guest_temp_path = f"C:\\{temp_filename}"
            host_capture_path = f"C:\\Users\\brian\\Documents\\GitHub\\vmware-monitor\\capture\\{temp_filename}"
            
            # Create PowerShell command that writes count and latest event time to file in C:\
            ps_command = f"""$events = Get-EventLog -LogName System -After '{start_str}' -Before '{end_str}' -ErrorAction SilentlyContinue | Where-Object {{$_.EventID -eq 2004}} | Sort-Object TimeGenerated -Descending; $count = ($events | Measure-Object).Count; $latestTime = if ($events) {{ $events[0].TimeGenerated.ToString('yyyy-MM-dd HH:mm:ss') }} else {{ 'None' }}; @{{count=$count; latest_time=$latestTime}} | ConvertTo-Json -Compress | Out-File -FilePath '{guest_temp_path}' -Encoding ASCII"""
            print(f"[VMRUN] Writing event count to guest file: {guest_temp_path}")
            
            # Get vmrun path from VM manager
            if not self.vm_manager:
                from vm_manager import VMManager
                self.vm_manager = VMManager()
            
            # Step 1: Execute PowerShell command to write count to file
            vmrun_cmd = [
                self.vm_manager.vmrun_path,
                "-T", "ws",
                "-gu", Config.VM_USERNAME,
                "-gp", Config.VM_PASSWORD,
                "runProgramInGuest",
                vm_path,
                "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "-Command", ps_command
            ]
            
            print(f"[VMRUN] Command timeout: {Config.VMRUN_TIMEOUT}s")
            result = subprocess.run(
                vmrun_cmd,
                capture_output=True,
                text=True,
                timeout=Config.VMRUN_TIMEOUT
            )
            
            if result.returncode != 0:
                print(f"[VMRUN ERROR] PowerShell command failed: {result.returncode}")
                print(f"[STDERR] {result.stderr.strip()}")
                logger.warning(f"vmrun PowerShell command failed: {result.stderr}")
                return None
            
            print(f"[VMRUN] PowerShell command executed successfully")
            
            # Step 2: Copy file from guest to host
            copy_cmd = [
                self.vm_manager.vmrun_path,
                "-T", "ws",
                "-gu", Config.VM_USERNAME,
                "-gp", Config.VM_PASSWORD,
                "copyFileFromGuestToHost",
                vm_path,
                guest_temp_path,
                host_capture_path
            ]
            
            result = subprocess.run(
                copy_cmd,
                capture_output=True,
                text=True,
                timeout=Config.VMRUN_TIMEOUT
            )
            
            if result.returncode != 0:
                print(f"[VMRUN ERROR] File copy failed: {result.returncode}")
                print(f"[STDERR] {result.stderr.strip()}")
                logger.warning(f"vmrun file copy failed: {result.stderr}")
                return None
            
            print(f"[VMRUN] File copied successfully to: {host_capture_path}")
            
            # Step 3: Read the JSON data from the copied file
            try:
                with open(host_capture_path, 'r') as f:
                    json_str = f.read().strip()
                data = json.loads(json_str)
                count = data['count']
                latest_time = data['latest_time']
                print(f"[EVENTS] Found {count} Event ID 2004 occurrences, latest: {latest_time}")
                
                # Keep the file for debugging - don't clean up
                print(f"[DEBUG] Event data file saved: {host_capture_path}")
                
                # Store the latest event time for restart logic
                self.latest_event_time = latest_time if latest_time != 'None' else None
                return count > 0
            except (ValueError, FileNotFoundError, IOError) as e:
                print(f"[FILE ERROR] Could not read count from file: {e}")
                logger.warning(f"Could not read event count from file: {e}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] vmrun command timed out after {Config.VMRUN_TIMEOUT} seconds")
            logger.warning(f"vmrun command timed out after {Config.VMRUN_TIMEOUT} seconds")
            return None
        except Exception as e:
            print(f"[EXCEPTION] {str(e)}")
            logger.error(f"Error in vmrun script method: {str(e)}")
            return None
    
    def _check_via_remote_powershell(self, vm_path: str, start_time: datetime, end_time: datetime) -> Optional[bool]:
        """
        Check events via remote PowerShell (requires VM IP and credentials).
        """
        # This would require VM IP and credentials - placeholder for now
        # In a production environment, you'd need to configure WinRM and credentials
        logger.debug("Remote PowerShell method not implemented - requires credentials setup")
        return None
    
    def _check_via_simple_fallback(self, vm_path: str, start_time: datetime, end_time: datetime) -> Optional[bool]:
        """
        Simple fallback method that assumes no events if VM is unresponsive.
        This prevents the monitor from getting stuck on unresponsive VMs.
        """
        vm_name = self._get_vm_name_from_path(vm_path)
        logger.info(f"Using fallback method for VM {vm_name} - assuming no Event ID 2004")
        return False
    
    def _get_vm_name_from_path(self, vm_path: str) -> str:
        """Extract VM name from path for logging"""
        import os
        try:
            return os.path.basename(vm_path).replace('.vmx', '')
        except:
            return vm_path
    
    def _create_event_check_script(self, start_time: datetime, end_time: datetime) -> str:
        """
        Create PowerShell script to check for Event ID 2004.
        """
        # Format times for PowerShell
        start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        
        script = f"""
# PowerShell script to check for Event ID 2004
try {{
    $startTime = Get-Date "{start_str}"
    $endTime = Get-Date "{end_str}"
    
    # Check multiple event logs where Event ID 2004 might appear
    $logNames = @(
        "Microsoft-Windows-Diagnostics-Performance/Operational",
        "Microsoft-Windows-Resource-Exhaustion-Detector/Operational",
        "System",
        "Application"
    )
    
    $found = $false
    
    foreach ($logName in $logNames) {{
        try {{
            $events = Get-WinEvent -FilterHashtable @{{
                LogName = $logName
                ID = 2004
                StartTime = $startTime
                EndTime = $endTime
            }} -ErrorAction SilentlyContinue
            
            if ($events) {{
                $found = $true
                break
            }}
        }} catch {{
            # Log might not exist, continue
        }}
    }}
    
    if ($found) {{
        Write-Output "TRUE"
    }} else {{
        Write-Output "FALSE"
    }}
}} catch {{
    Write-Output "ERROR: $($_.Exception.Message)"
}}
"""
        return script
    
    def _check_local_events(self, minutes_back: int = 1) -> bool:
        """
        Check for Event ID 2004 on the local machine (for testing).
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=minutes_back)
            
            # Use PowerShell to check local events
            ps_script = self._create_event_check_script(start_time, end_time)
            
            result = subprocess.run(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout.strip().upper()
                return output == "TRUE"
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking local events: {str(e)}")
            return False
    
    def test_event_detection(self) -> bool:
        """
        Test the event detection functionality.
        """
        logger.info("Testing event detection on local machine...")
        
        # Check for any Event ID 2004 in the last 24 hours
        try:
            result = self._check_local_events(minutes_back=1440)  # 24 hours
            logger.info(f"Event detection test result: {result}")
            return True
        except Exception as e:
            logger.error(f"Event detection test failed: {str(e)}")
            return False