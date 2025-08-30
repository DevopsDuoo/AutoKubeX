# 🤖 Autonomous AI Cluster Management

AutoKubeX now includes **Autonomous AI** capabilities that can automatically detect and fix Kubernetes cluster issues without human intervention.

## 🎯 What It Does

The Autonomous AI Agent can:
- **Analyze** your cluster for critical issues
- **Plan** specific fixes using available actions  
- **Execute** fixes automatically (with safety controls)
- **Monitor** continuously and respond to problems
- **Learn** from feedback to improve decisions

## 🛡️ Safety Features

### Built-in Protections:
- **Rate Limiting**: Max 20 actions/hour, 5 deletions/hour
- **Protected Resources**: Won't touch system pods (coredns, etcd, etc.)
- **Protected Namespaces**: kube-system, kube-public, istio-system
- **Scaling Limits**: Max 20 replicas, 300% scaling percentage
- **Bulk Limits**: Max 10 resources per bulk operation
- **Action Logging**: All actions tracked with timestamps

### Dry Run Mode:
- **Default behavior** - shows what would be done
- **Zero risk** - no actual changes made
- **Perfect for testing** and understanding AI decisions

## 🚀 Quick Start

### 1. Web Interface (Recommended)
```bash
python launch_ui.py
```
- Navigate to **"🤖 Autonomous AI"** tab
- Upload your kubeconfig
- Click **"🤖 Analyze & Fix Issues"**
- Review what AI found and would fix
- Switch to **"🚀 Execute Actions"** when ready

### 2. Command Line Interface
```bash
# Dry run analysis (safe)
python -m interface.cli autonomous-fix --kubeconfig path/to/config --dry-run

# Execute fixes (careful!)
python -m interface.cli autonomous-fix --kubeconfig path/to/config --execute

# Continuous monitoring
python -m interface.cli autonomous-monitor --kubeconfig path/to/config --interval 5 --cycles 12
```

### 3. Standalone Autonomous Script
```bash
# Single analysis
python autonomous.py --kubeconfig path/to/config --mode single --dry-run

# Continuous monitoring (1 hour)
python autonomous.py --kubeconfig path/to/config --mode monitor --interval 5 --cycles 12

# Show safety constraints
python autonomous.py --kubeconfig path/to/config --show-safety
```

## 🧠 AI Capabilities

### Issues It Detects:
1. **High Restart Pods** (>5 restarts) → Restart or delete pod
2. **Failed Pods** (CrashLoopBackOff) → Delete pod to force recreation  
3. **Zero Replica Deployments** → Scale up to restore service
4. **Resource Starved Pods** → Update resource limits
5. **Stuck Pending Pods** → Fix scheduling issues

### Actions It Can Take:
- `restart_pod` - Restart individual pods
- `delete_pod` - Delete failed pods for recreation
- `restart_deployment` - Restart entire deployments
- `scale_deployment` - Scale replicas up/down
- `scale_deployment_by_percentage` - Percentage-based scaling
- `bulk_restart_pods` - Restart multiple pods
- `bulk_scale_deployments` - Scale multiple deployments
- `update_pod_resources` - Adjust CPU/memory limits
- `apply_hpa` - Set up auto-scaling

## 🔧 Configuration

### Custom Prompts:
Guide the AI to focus on specific areas:
```bash
--prompt "Focus on performance and scaling issues"
--prompt "Check for security and resource problems"  
--prompt "Look for networking and connectivity issues"
```

### Safety Configuration:
Edit `config/autonomous.yaml` to adjust:
- Rate limits
- Protected resources
- Monitoring intervals
- AI behavior settings

## 📊 Usage Examples

### Example 1: Daily Health Check
```bash
# Safe daily check - see what needs fixing
python autonomous.py --kubeconfig ~/.kube/config --mode single --dry-run
```

### Example 2: Active Problem Resolution
```bash
# Let AI fix issues automatically
python autonomous.py --kubeconfig ~/.kube/config --mode single --execute
```

### Example 3: 24/7 Monitoring
```bash
# Run continuous monitoring (check every 10 minutes)
python autonomous.py --kubeconfig ~/.kube/config --mode monitor --interval 10 --cycles 144 --execute
```

### Example 4: Custom Focus
```bash
# Focus on specific problems
python autonomous.py --kubeconfig ~/.kube/config --prompt "Focus on pods with high CPU usage and memory leaks" --execute
```

## 🔍 How It Works

1. **Cluster Analysis**: AI gets comprehensive cluster state
2. **Issue Detection**: Uses advanced prompts to identify problems
3. **Action Planning**: AI creates specific fix commands
4. **Safety Validation**: Each action checked against safety rules
5. **Execution**: Actions executed in safe order with error handling
6. **Logging**: All actions logged for audit and learning

## ⚠️ Important Notes

- **Start with dry-run** to understand what AI would do
- **Monitor the logs** in `/tmp/autokubex_safety_log.json`
- **Protected namespaces** are never modified for safety
- **Rate limits** prevent excessive actions
- **Always test** in dev environment first

## 🎛️ Advanced Usage

### Integration with CI/CD:
```bash
# In your pipeline
python autonomous.py --kubeconfig $KUBECONFIG --mode single --execute --prompt "Post-deployment health check"
```

### Scheduled Monitoring:
```bash
# Add to crontab for regular checks
0 */6 * * * cd /path/to/autokubex && python autonomous.py --kubeconfig ~/.kube/config --mode single --execute
```

### Custom Analysis:
```python
from ai_engine.autonomous_agent import AutonomousAgent

agent = AutonomousAgent(dry_run=False)
result = agent.analyze_and_fix("Check for memory leaks in production namespace")
print(result)
```

## 🆘 Troubleshooting

- **Permission denied**: Ensure kubeconfig has required RBAC permissions
- **Rate limited**: Wait or check safety logs in `/tmp/autokubex_safety_log.json`
- **AI timeout**: Check network connection and Gemini API key
- **Action failed**: Check individual action logs in execution results

## 🔮 Future Enhancements

- Machine learning from action outcomes
- Custom action plugins
- Integration with monitoring systems
- Slack/Teams notifications
- Advanced scheduling and orchestration

---

**🚨 REMEMBER: Always start with `--dry-run` to see what the AI would do before executing!**
