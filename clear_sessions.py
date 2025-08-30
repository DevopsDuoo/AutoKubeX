#!/usr/bin/env python3
"""
Clear all AutoKubeX sessions and temporary files
"""

import os
import tempfile
import glob
import shutil

def clear_all_sessions():
    """Clear all session files and temporary data"""
    
    temp_dir = tempfile.gettempdir()
    
    # Clear complex session manager files
    complex_session_dir = os.path.join(temp_dir, "autokubex_sessions")
    if os.path.exists(complex_session_dir):
        try:
            shutil.rmtree(complex_session_dir)
            print(f"✅ Cleared complex sessions directory: {complex_session_dir}")
        except Exception as e:
            print(f"❌ Failed to clear complex sessions: {e}")
    
    # Clear simple session files
    simple_files = [
        os.path.join(temp_dir, "autokubex_session.json"),
        os.path.join(temp_dir, "autokubex_kubeconfig.yaml")
    ]
    
    for file_path in simple_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Cleared: {file_path}")
            except Exception as e:
                print(f"❌ Failed to clear {file_path}: {e}")
    
    # Clear any temporary kubeconfig files
    temp_kubeconfig_pattern = os.path.join(temp_dir, "tmp*kubeconfig*")
    temp_files = glob.glob(temp_kubeconfig_pattern)
    
    for temp_file in temp_files:
        try:
            os.remove(temp_file)
            print(f"✅ Cleared temp file: {temp_file}")
        except Exception as e:
            print(f"❌ Failed to clear {temp_file}: {e}")
    
    print("\n🎉 All AutoKubeX sessions and temporary files cleared!")
    print("💡 You can now start fresh with the simple UI")

if __name__ == "__main__":
    clear_all_sessions()
