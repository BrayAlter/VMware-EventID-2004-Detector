#!/usr/bin/env python3
"""
VM Manager
Handles VMware VM operations using vmrun command-line tool.
"""

import subprocess
import logging
import os
from typing import List, Optional
from config import Config

logger = logging.getLogger(__name__)

class VMManager:
    """Manages VMware VM operations using vmrun"""
    
    def __init__(self):
        self.vmrun_path = self._find_vmrun()
        if not self.vmrun_path:
            raise RuntimeError("vmrun executable not found. Please install VMware Workstation or Player.")
        logger.info(f"Using vmrun at: {self.vmrun_path}")
    
    def _find_vmrun(self) -> Optional[str]:
        """Find vmrun executable in common VMware installation paths"""
        common_paths = [
            r"C:\Program Files (x86)\VMware\VMware Workstation\vmrun.exe",
            r"C:\Program Files\VMware\VMware Workstation\vmrun.exe",
            r"C:\Program Files (x86)\VMware\VMware Player\vmrun.exe",
            r"C:\Program Files\VMware\VMware Player\vmrun.exe"
        ]
        
        # Check if vmrun is in PATH
        try:
            result = subprocess.run(["vmrun"], capture_output=True, text=True)
            if result.returncode == 1:  # vmrun returns 1 when called without arguments
                return "vmrun"
        except FileNotFoundError:
            pass
        
        # Check common installation paths
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _run_vmrun_command(self, args: List[str]) -> tuple[bool, str]:
        """Execute vmrun command and return success status and output"""
        cmd = [self.vmrun_path] + args
        
        try:
            logger.debug(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=Config.VMRUN_TIMEOUT
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                logger.error(f"vmrun command failed: {result.stderr.strip()}")
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            logger.error(f"vmrun command timed out after {Config.VMRUN_TIMEOUT} seconds")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"Error executing vmrun command: {str(e)}")
            return False, str(e)
    
    def get_powered_on_vms(self) -> List[str]:
        """Get list of all powered-on VMs"""
        success, output = self._run_vmrun_command(["list"])
        
        if not success:
            logger.error("Failed to get VM list")
            return []
        
        lines = output.split('\n')
        if not lines:
            return []
        
        # First line contains the count, rest are VM paths
        vm_paths = []
        for line in lines[1:]:  # Skip first line (count)
            line = line.strip()
            if line and line.endswith('.vmx'):
                vm_paths.append(line)
        
        logger.info(f"Found {len(vm_paths)} powered-on VMs")
        return vm_paths
    
    def get_vm_name(self, vm_path: str) -> str:
        """Extract VM name from VM path"""
        try:
            # Extract filename without extension
            vm_name = os.path.basename(vm_path).replace('.vmx', '')
            return vm_name
        except Exception:
            return vm_path
    
    def restart_vm(self, vm_path: str) -> bool:
        """Restart a VM with lock file handling and retry logic"""
        vm_name = self.get_vm_name(vm_path)
        
        for attempt in range(1, Config.RESTART_MAX_RETRIES + 1):
            print(f"[RESTART] Attempt {attempt}/{Config.RESTART_MAX_RETRIES} for VM {vm_name}")
            logger.info(f"Restart attempt {attempt} for VM: {vm_name}")
            
            if self._restart_vm_single_attempt(vm_path, vm_name, attempt):
                return True
            
            if attempt < Config.RESTART_MAX_RETRIES:
                print(f"[RESTART] Attempt {attempt} failed, waiting {Config.RESTART_RETRY_DELAY}s before retry")
                logger.warning(f"Restart attempt {attempt} failed for {vm_name}, retrying in {Config.RESTART_RETRY_DELAY}s")
                import time
                time.sleep(Config.RESTART_RETRY_DELAY)
        
        print(f"[RESTART] All {Config.RESTART_MAX_RETRIES} attempts failed for VM {vm_name}")
        logger.error(f"Failed to restart VM {vm_name} after {Config.RESTART_MAX_RETRIES} attempts")
        return False
    
    def _restart_vm_single_attempt(self, vm_path: str, vm_name: str, attempt: int) -> bool:
        """Single restart attempt with enhanced lock file handling"""
        import time
        
        # Step 1: Stop the VM
        print(f"[RESTART] Step 1: Stopping VM {vm_name} (soft shutdown)")
        logger.info(f"Stopping VM: {vm_name}")
        success, output = self._run_vmrun_command(["stop", vm_path, "soft", "nogui"])
        
        if not success:
            if "is not powered on" in output.lower():
                print(f"[RESTART] VM {vm_name} already stopped")
                logger.info(f"VM {vm_name} was already stopped")
            elif "locked" in output.lower() or "busy" in output.lower():
                print(f"[RESTART] VM {vm_name} locked, trying hard stop")
                logger.warning(f"VM {vm_name} appears locked, attempting hard stop")
                success, output = self._run_vmrun_command(["stop", vm_path, "hard", "nogui"])
                if not success:
                    print(f"[RESTART] Hard stop failed: {output}")
                    return False
            else:
                print(f"[RESTART] Soft shutdown failed, trying hard stop")
                logger.error(f"Failed to stop VM {vm_name}: {output}")
                success, output = self._run_vmrun_command(["stop", vm_path, "hard", "nogui"])
                if not success:
                    print(f"[RESTART] Hard stop failed: {output}")
                    return False
        
        print(f"[RESTART] VM {vm_name} stopped successfully")
        logger.info(f"VM {vm_name} stopped successfully")
        
        # Step 2: Wait for lock files to clear with progressive checking
        total_wait = Config.RESTART_DELAY + Config.LOCK_FILE_CLEANUP_DELAY
        print(f"[RESTART] Step 2: Waiting {total_wait}s for lock files to clear")
        
        # Check for lock files every 5 seconds during wait period
        wait_intervals = max(1, total_wait // 5)
        interval_time = total_wait / wait_intervals
        
        for i in range(int(wait_intervals)):
            time.sleep(interval_time)
            # Try a quick status check to see if VM is ready
            if i > 0 and (i % 2 == 0):  # Check every other interval after first
                test_success, test_output = self._run_vmrun_command(["list"])
                if test_success:
                    print(f"[RESTART] Lock file check {i+1}/{int(wait_intervals)} - VMware responding")
        
        # Step 3: Start the VM with enhanced error handling
        print(f"[RESTART] Step 3: Starting VM {vm_name}")
        logger.info(f"Starting VM: {vm_name}")
        
        # First attempt with nogui for faster startup
        success, output = self._run_vmrun_command(["start", vm_path, "nogui"])
        
        if not success:
            if "locked" in output.lower() or "busy" in output.lower():
                print(f"[RESTART] VM {vm_name} still locked, waiting additional 15s")
                logger.warning(f"VM {vm_name} still locked, waiting additional time: {output}")
                time.sleep(15)
                # Retry with standard start
                success, output = self._run_vmrun_command(["start", vm_path])
                if not success:
                    print(f"[RESTART] VM {vm_name} still locked after extended wait, will retry")
                    return False
            elif "timeout" in output.lower():
                print(f"[RESTART] VM {vm_name} start timed out, will retry")
                logger.warning(f"VM {vm_name} start operation timed out: {output}")
                return False
            else:
                print(f"[RESTART] Failed to start VM {vm_name}: {output}")
                logger.error(f"Failed to start VM {vm_name}: {output}")
                return False
        
        print(f"[RESTART] VM {vm_name} restarted successfully")
        logger.info(f"VM {vm_name} started successfully")
        return True
    
    def get_vm_ip(self, vm_path: str) -> Optional[str]:
        """Get VM IP address (useful for remote event checking)"""
        success, output = self._run_vmrun_command(["getGuestIPAddress", vm_path])
        
        if success and output:
            return output.strip()
        
        return None
    
    def is_vm_running(self, vm_path: str) -> bool:
        """Check if a specific VM is running"""
        running_vms = self.get_powered_on_vms()
        return vm_path in running_vms