# AutoKubeX Session Management

## Overview

AutoKubeX now features persistent session management that eliminates the need to re-upload kubeconfig files after browser refreshes. Sessions maintain cluster connections, diagnosis history, and user preferences across browser sessions.

## Key Features

### 🔐 Persistent Sessions
- **Automatic Session Creation**: Each connection gets a unique session ID
- **Cross-Refresh Persistence**: Sessions survive browser refreshes and page reloads
- **Secure Storage**: Kubeconfig files stored in secure temporary locations
- **24-Hour Expiration**: Sessions automatically expire after 24 hours for security

### 🔄 Session Restoration
- **Auto-Recovery**: Automatically detects and restores previous sessions on page load
- **Connection Validation**: Verifies cluster connectivity before restoring
- **Graceful Fallback**: Falls back to new session creation if restoration fails

### 📱 Multi-Session Support
- **Concurrent Sessions**: Support multiple cluster connections simultaneously
- **Session Isolation**: Each session maintains separate state and history
- **Session Switching**: View and manage multiple active sessions

### 🛡️ Security Features
- **Unique Session IDs**: Cryptographically secure session identifiers
- **Automatic Cleanup**: Expired sessions and temporary files cleaned up automatically
- **Isolated Storage**: Each session stores data in separate secure locations

## Usage Guide

### Starting a New Session

1. **Launch Web UI**: 
   ```bash
   python launch_ui.py
   ```

2. **Upload Kubeconfig**: 
   - Click "Choose your kubeconfig file"
   - Select your kubeconfig file
   - Optionally provide a cluster name
   - Click "🔗 Start Session"

3. **Session Active**: 
   - Green checkmark indicates active connection
   - Session ID displayed in sidebar
   - Connection timestamp shown

### Session Management

#### Sidebar Session Controls
- **Session Status**: Shows current connection status
- **Session ID**: Displays unique session identifier (first 8 characters)
- **Connection Time**: When the session was established
- **End Session**: Cleanly terminates current session
- **Restore Session**: Attempts to restore previous session

#### Quick Actions
- **Refresh Data**: Reload cluster information
- **Problem Detection**: Quick check for problematic pods
- **Tab Navigation**: Direct links to specific functionality

### Session Persistence

#### What Persists
- ✅ Cluster connection and kubeconfig
- ✅ AI diagnosis history
- ✅ Custom query results
- ✅ Session metadata and timestamps
- ✅ Cluster name and connection details

#### What Doesn't Persist
- ❌ UI state (selected tabs, form inputs)
- ❌ Temporary operation results
- ❌ In-progress bulk operations

### Session Restoration

#### Automatic Restoration
- Occurs on page load/refresh
- Validates cluster connectivity
- Restores session data and history
- Shows restoration status

#### Manual Restoration
- Click "🔄 Restore Previous Session" button
- Attempts to find and restore valid sessions
- Displays success/failure status

### Session Termination

#### Manual End Session
- Click "🔴 End Session" in sidebar
- Immediately cleans up session data
- Removes temporary kubeconfig files
- Returns to session creation screen

#### Automatic Expiration
- Sessions expire after 24 hours
- Expired sessions automatically cleaned up
- Storage space freed automatically

## File Structure

### Session Storage
```
/tmp/autokubex_sessions/
├── session_[session_id].json    # Session metadata and history
├── kubeconfig_[session_id].yaml  # Cluster configuration
└── ... (other sessions)
```

### Session Data Format
```json
{
  "session_id": "d4b5c6db...",
  "last_updated": "2025-08-30T20:45:59",
  "data": {
    "kubeconfig_path": "/tmp/autokubex_sessions/kubeconfig_abc123.yaml",
    "cluster_name": "Production Cluster",
    "connection_time": "2025-08-30T15:30:00",
    "last_diagnosis": { ... },
    "last_custom": { ... }
  }
}
```

## Technical Implementation

### SessionManager Class
- **Location**: `interface/session_manager.py`
- **Purpose**: Handles all session lifecycle operations
- **Features**: Create, save, load, restore, cleanup sessions

### Key Methods
- `start_session()`: Initialize new session with cluster connection
- `restore_session()`: Restore previous session from storage
- `end_session()`: Clean termination and cleanup
- `save_session_data()`: Persist session data to disk
- `load_session_data()`: Retrieve session data from disk

### Integration Points
- **Dashboard**: Main UI integration in `dashboard.py`
- **State Management**: Streamlit session state integration
- **Security**: Secure file handling and cleanup

## Benefits

### User Experience
- 🚫 **No More Re-uploads**: Never lose your connection after refresh
- ⚡ **Faster Startup**: Instant connection to previously connected clusters
- 📝 **History Persistence**: Keep your diagnosis results across sessions
- 🔄 **Seamless Continuity**: Pick up exactly where you left off

### Operational Benefits
- 🛡️ **Enhanced Security**: Proper session isolation and cleanup
- 🧹 **Resource Management**: Automatic cleanup prevents storage bloat
- 📊 **Multi-Cluster**: Work with multiple clusters simultaneously
- 🔧 **Reliability**: Robust error handling and graceful degradation

## Troubleshooting

### Common Issues

#### Session Not Restoring
- **Cause**: Session expired or kubeconfig moved
- **Solution**: Start new session with fresh kubeconfig

#### Connection Lost After Restore
- **Cause**: Cluster credentials changed or cluster unreachable
- **Solution**: End session and create new one with updated kubeconfig

#### Multiple Sessions Showing
- **Cause**: Normal behavior for multi-cluster usage
- **Solution**: Use "End Session" to clean up unused sessions

### Error Messages
- `No valid session found to restore`: No previous sessions available
- `Session expired`: Session older than 24 hours, cleanup occurred
- `Failed to restore cluster connection`: Cluster unreachable or kubeconfig invalid
- `Failed to save session`: File system permissions or storage issues

### Best Practices
1. **Regular Cleanup**: End sessions when switching clusters frequently
2. **Security**: Don't share session IDs or leave sessions running on shared machines
3. **Storage**: Monitor `/tmp/autokubex_sessions/` size if using extensively
4. **Backup**: Keep original kubeconfig files separate from session storage

## Migration Guide

### From Legacy Version
1. Existing temporary files will be ignored
2. First session will require kubeconfig upload
3. Previous diagnoses won't be restored (stored in old format)
4. New persistent behavior starts immediately

### Configuration
- No configuration required
- Default 24-hour expiration (hardcoded)
- Default storage in system temp directory
- Automatic cleanup on startup
