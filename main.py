#!/usr/bin/env python3
"""
VMware VM Monitor
Monitors VMware VMs for Event ID 2004 and restarts them if detected within the last minute.
"""

import time
import logging
from datetime import datetime
from vm_manager import VMManager
from event_checker import EventChecker
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vmware_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main monitoring loop"""
    print("="*60)
    print("VMware VM Monitor - Event ID 2004 Detection")
    print("="*60)
    logger.info("Starting VMware VM Monitor")
    
    vm_manager = VMManager()
    event_checker = EventChecker()
    
    try:
        cycle_count = 0
        while True:
            cycle_count += 1
            print(f"\n[CYCLE {cycle_count}] Starting monitoring cycle at {datetime.now().strftime('%H:%M:%S')}")
            logger.info("Starting monitoring cycle")
            
            # Step 1: Get all powered-on VMs
            print("[VM SCAN] Scanning for powered-on VMs...")
            powered_on_vms = vm_manager.get_powered_on_vms()
            print(f"[VM SCAN] Found {len(powered_on_vms)} powered-on VMs")
            logger.info(f"Found {len(powered_on_vms)} powered-on VMs")
            
            if not powered_on_vms:
                print(f"[STATUS] No powered-on VMs found - waiting for next cycle")
                logger.info("No powered-on VMs found")
                print(f"[WAIT] Sleeping for {Config.CHECK_INTERVAL} seconds...")
                time.sleep(Config.CHECK_INTERVAL)
                continue
            
            # Step 2 & 3: Check each VM for Event ID 2004 and restart if needed
            for i, vm_path in enumerate(powered_on_vms, 1):
                vm_name = vm_manager.get_vm_name(vm_path)
                print(f"\n[VM {i}/{len(powered_on_vms)}] Processing: {vm_name}")
                logger.info(f"Checking VM: {vm_name}")
                
                try:
                    # Check for Event ID 2004 in the last 60 minutes
                    if event_checker.check_event_2004(vm_path, minutes_back=60):
                        print(f"[ALERT] Event ID 2004 detected in {vm_name}!")
                        logger.warning(f"Event ID 2004 detected in VM: {vm_name}")
                        
                        # Check if restart is needed based on event timing
                        if event_checker.should_restart_vm(vm_path):
                            print(f"[ACTION] Restarting VM: {vm_name} (recent event detected)")
                            logger.info(f"Restarting VM: {vm_name}")
                            
                            if vm_manager.restart_vm(vm_path):
                                print(f"[SUCCESS] VM {vm_name} restarted successfully")
                                logger.info(f"Successfully restarted VM: {vm_name}")
                                # Mark VM as restarted to prevent duplicate restarts
                                event_checker.mark_vm_restarted(vm_path)
                            else:
                                print(f"[FAILED] Could not restart VM: {vm_name}")
                                logger.error(f"Failed to restart VM: {vm_name}")
                        else:
                            print(f"[SKIP] Event found but restart not needed (old event or already restarted)")
                    else:
                        print(f"[OK] No Event ID 2004 found in {vm_name}")
                        logger.debug(f"No Event ID 2004 found in VM: {vm_name}")
                        
                except Exception as e:
                    print(f"[ERROR] Failed to check {vm_name}: {str(e)}")
                    logger.error(f"Error checking VM {vm_name}: {str(e)}")
                    continue
            
            print(f"\n[CYCLE COMPLETE] Finished checking all VMs")
            logger.info(f"Monitoring cycle completed. Sleeping for {Config.CHECK_INTERVAL} seconds")
            print(f"[WAIT] Sleeping for {Config.CHECK_INTERVAL} seconds until next cycle...")
            time.sleep(Config.CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Received interrupt signal - stopping monitor")
        logger.info("Monitor stopped by user")
        logger.info("VMware VM Monitor stopped")
        print("[SHUTDOWN] VMware VM Monitor stopped")
    except Exception as e:
        print(f"[FATAL ERROR] {str(e)}")
        logger.error(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    main()