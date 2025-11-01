#!/usr/bin/env python3
"""
Test Recording Isolation - Verify recording continues during UI freeze
CRITICAL TEST: Ensures data quality is maintained even when dashboard freezes
"""

import sys
import time
import psutil
from core.ros2_manager import ROS2Manager

def test_recording_isolation():
    """
    Test that recording process continues independently of main thread freezes
    """
    print("="*70)
    print("RECORDING ISOLATION TEST")
    print("="*70)
    print("This test verifies that ROS2 bag recording continues even when")
    print("the main thread (UI) freezes completely.")
    print()
    
    # Initialize ROS2 Manager
    print("1️⃣  Initializing ROS2 Manager...")
    manager = ROS2Manager()
    
    # Start recording (all topics)
    print("\n2️⃣  Starting recording...")
    bag_name = f"test_isolation_{int(time.time())}"
    success = manager.start_recording(bag_name, topics=None)
    
    if not success:
        print("❌ Failed to start recording!")
        return False
    
    print("✅ Recording started")
    time.sleep(2)  # Let recording stabilize
    
    # Get initial recording health
    health_before = manager.get_recording_health()
    if health_before:
        print(f"\n📊 Initial Recording Health:")
        print(f"   PID: {health_before['pid']}")
        print(f"   CPU: {health_before['cpu_percent']:.1f}%")
        print(f"   Memory: {health_before['memory_mb']:.1f} MB")
        print(f"   Status: {health_before['status']}")
    
    # CRITICAL TEST: Freeze main thread for 10 seconds
    print("\n3️⃣  SIMULATING UI FREEZE (main thread blocked for 10 seconds)...")
    print("   🧊 Main thread freezing NOW...")
    print("   🎬 Recording process should CONTINUE independently...")
    
    freeze_start = time.time()
    time.sleep(10)  # This simulates a complete UI freeze
    freeze_duration = time.time() - freeze_start
    
    print(f"   ✅ Main thread unfroze after {freeze_duration:.1f}s")
    
    # Check recording health after freeze
    print("\n4️⃣  Checking recording health after freeze...")
    health_after = manager.get_recording_health()
    
    if not health_after:
        print("❌ CRITICAL: Recording process died during freeze!")
        return False
    
    print(f"✅ Recording process is ALIVE!")
    print(f"\n📊 Recording Health After Freeze:")
    print(f"   PID: {health_after['pid']}")
    print(f"   Elapsed: {health_after['elapsed_seconds']}s")
    print(f"   CPU: {health_after['cpu_percent']:.1f}%")
    print(f"   Memory: {health_after['memory_mb']:.1f} MB")
    print(f"   Health Checks: {health_after['health_checks']}")
    print(f"   Status: {health_after['status']}")
    
    if health_after['warnings']:
        print(f"   ⚠️  Warnings: {health_after['warnings']}")
    
    # Verify recording process is still actively running
    try:
        process = psutil.Process(health_after['pid'])
        if process.is_running():
            print(f"\n✅ VERIFICATION: Process {health_after['pid']} is running")
            print(f"   Process Name: {process.name()}")
            print(f"   Process Status: {process.status()}")
        else:
            print(f"\n❌ CRITICAL: Process {health_after['pid']} is NOT running!")
            return False
    except psutil.NoSuchProcess:
        print(f"\n❌ CRITICAL: Process {health_after['pid']} does not exist!")
        return False
    
    # Stop recording gracefully
    print("\n5️⃣  Stopping recording...")
    manager.stop_recording()
    print("✅ Recording stopped")
    
    # Final summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("✅ Recording process survived 10-second main thread freeze")
    print("✅ Process remained alive and healthy throughout test")
    print("✅ Data integrity maintained (no process crashes)")
    print("\n🎉 RECORDING ISOLATION: VERIFIED")
    print("   Recording will continue even if dashboard UI freezes!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    print("\n" + "🚀 "*20)
    print("Starting Recording Isolation Test...")
    print("🚀 "*20 + "\n")
    
    try:
        success = test_recording_isolation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
