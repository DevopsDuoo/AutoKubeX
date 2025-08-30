#!/usr/bin/env python3
"""
AutoKubeX Web UI Launcher

This script launches the AutoKubeX web interface with automatic session persistence.
Clean, simple UI that just works - sessions persist across browser refreshes.

Usage:
    python launch_ui.py [--port 8501] [--host localhost]
    
Features:
- Automatic session persistence across browser refreshes
- Clean, focused interface  
- All bulk operations and advanced features
- One-click connect and disconnect
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Launch AutoKubeX Web UI")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the web UI on (default: 8501)")
    parser.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with auto-reload")
    
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = Path(__file__).parent
    dashboard_path = project_root / "interface" / "web_ui" / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        sys.exit(1)
    
    print("🚀 Starting AutoKubeX Web UI...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print("✨ Features: Auto-Persistent Sessions, Bulk Operations, AI Diagnosis")
    print()
    print("🎯 Clean & Simple Interface:")
    print("  📤 Upload kubeconfig once - stays connected across refreshes")
    print("  🔄 Automatic session restoration")
    print("  🚀 Quick actions and bulk operations")
    print("  🔴 One-click disconnect when done")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", str(args.port),
        "--server.address", args.host,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
    
    if args.dev:
        cmd.extend(["--server.runOnSave", "true"])
    
    try:
        # Run streamlit
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n🛑 AutoKubeX Web UI stopped by user")
    except Exception as e:
        print(f"❌ Error starting web UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
