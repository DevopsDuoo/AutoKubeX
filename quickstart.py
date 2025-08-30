#!/usr/bin/env python3
"""
AutoKubeX Quick Start Script

This script helps you get started with AutoKubeX quickly and cleanly.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 AutoKubeX Quick Start")
    print("=" * 50)
    print()
    print("Choose your preferred interface:")
    print("1. 🎯 Web UI (Recommended) - Clean interface with automatic sessions")
    print("2.  CLI Only - Command line interface")
    print("3. 🧹 Clear Sessions - Reset all session data")
    print()
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🎯 Starting Web UI...")
            print("✨ Features: Auto-persistent sessions, bulk operations, AI diagnosis")
            print("📍 Opening at: http://localhost:8501")
            print()
            subprocess.run([sys.executable, "launch_ui.py"])
            break
            
        elif choice == "2":
            print("\n💻 CLI Mode Selected")
            print()
            print("Available commands:")
            print("  python main.py diagnose --kubeconfig /path/to/kubeconfig")
            print("  python main.py list-pods --kubeconfig /path/to/kubeconfig")
            print("  python main.py bulk-restart-pods-cmd --kubeconfig /path/to/kubeconfig --namespace default --pods 'pod1,pod2'")
            print()
            print("📖 See ACTIONS_GUIDE.md for complete CLI documentation")
            break
            
        elif choice == "3":
            print("\n🧹 Clearing all sessions...")
            try:
                subprocess.run([sys.executable, "clear_sessions.py"])
                print("\n✅ Sessions cleared! You can now start fresh.")
            except Exception as e:
                print(f"\n❌ Error clearing sessions: {e}")
            
            # Ask if they want to start UI after clearing
            print("\nStart UI after clearing?")
            start_ui = input("Start Web UI? (y/n): ").strip().lower()
            if start_ui in ['y', 'yes']:
                print("\n🎯 Starting Web UI...")
                subprocess.run([sys.executable, "launch_ui.py"])
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("launch_ui.py"):
        print("❌ Error: Please run this script from the AutoKubeX root directory")
        sys.exit(1)
    
    main()
