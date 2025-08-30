# 🤖 AutoKubeX - AI-Powered Kubernetes Cluster Manager

AutoKubeX is an intelligent assistant that connects to any Kubernetes cluster and diagnoses issues using AI (Gemini or OpenAI). It features automatic session persistence, bulk operations, and advanced scaling capabilities through both CLI and web interfaces.

---

## 🚀 Key Features

### 🔍 AI-Powered Diagnosis
- **Intelligent Analysis**: AI-based diagnosis for cluster health using Gemini/OpenAI
- **Custom Queries**: Ask specific questions about your cluster
- **Persistent Results**: Keep diagnosis history across sessions

### 🔐 Automatic Sessions
- **Persistent Connection**: Sessions survive browser refreshes automatically
- **No Complex UI**: Simple connect/disconnect - no session management needed
- **Reliable Restoration**: Automatic restoration that actually works
- **Clean Interface**: Focus on cluster management, not session complexity

### ⚡ Advanced Operations
- **Bulk Actions**: Restart, scale, or delete multiple resources simultaneously
- **Smart Scaling**: Percentage-based scaling, namespace-wide operations
- **Label Selectors**: Target specific resources using Kubernetes labels
- **Safety Features**: Error isolation, minimum replica enforcement

### 🖥️ Dual Interface
- **Web UI**: Clean Streamlit dashboard with automatic persistence
- **CLI**: Comprehensive command-line interface for automation
- **Unified Experience**: Consistent functionality across both interfaces

---

## 📁 Project Structure

```
autokubex/
├── ai_engine/               # AI planner, LLM interface, prompt templates
├── actions/                 # Restart, scale, patch K8s components
├── config/                  # Cluster-specific configuration files
├── interface/
│   ├── cli.py               # Typer CLI interface
│   ├── simple_session.py    # Simple session management
│   └── web_ui/dashboard.py  # Main Streamlit dashboard
├── k8s_connector/           # K8s API wrapper, cluster connector, observability
├── models/                  # Trained anomaly models and history tracking
├── tests/                   # Placeholder for unit tests
├── main.py                  # CLI entrypoint
├── launch_ui.py             # Web UI launcher
├── quickstart.py            # Interactive startup script
├── clear_sessions.py        # Session cleanup utility
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### Web UI (Recommended)

Launch the web interface with automatic session persistence:

```bash
# Launch web UI - clean and persistent
python launch_ui.py

# Custom port/host
python launch_ui.py --port 8080 --host 0.0.0.0

# Development mode with auto-reload  
python launch_ui.py --dev

# Or use the interactive quickstart
python quickstart.py

# Clear sessions if needed
python clear_sessions.py
```

**Simple & Persistent:**
- 📤 Upload kubeconfig once - automatically persists across browser refreshes
- 🔄 No complex session UI - just works automatically  
- 🚀 Clean interface focused on cluster management
- 🔴 One-click disconnect when switching clusters

### CLI Usage

For command-line automation and scripting:

```bash
# AI diagnosis
python main.py diagnose --kubeconfig /path/to/kubeconfig

# Individual actions
python main.py restart-pod-cmd --kubeconfig /path/to/kubeconfig --namespace default --pod my-pod
python main.py scale-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployment my-app --replicas 5

# Bulk operations  
python main.py bulk-restart-pods-cmd --kubeconfig /path/to/kubeconfig --namespace default --pods "pod1,pod2,pod3"
python main.py bulk-scale-cmd --kubeconfig /path/to/kubeconfig --namespace default --config "app1:3,app2:5,cache:1"

# Advanced scaling
python main.py scale-all-cmd --kubeconfig /path/to/kubeconfig --namespace staging --replicas 1
python main.py scale-by-percentage-cmd --kubeconfig /path/to/kubeconfig --namespace default --deployment api --percentage 1.5
```

> **💡 Tip**: See `ACTIONS_GUIDE.md` for comprehensive CLI documentation

---

## 🧑‍💻 Local Development Setup

### 1. Clone the Repo

```bash
git clone https://github.com/DevopsDuoo/autokubex.git
cd autokubex
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Add Your AI Key (Gemini or OpenAI)

Create or edit the config file:

```yaml
# config/default.yaml
api_provider: gemini
api_key: "YOUR_GEMINI_API_KEY"
```

> You can also switch to `openai` by changing the `api_provider` field.

---

## 📚 Comprehensive Documentation

### Quick References
- **[Actions Guide](ACTIONS_GUIDE.md)**: Full CLI command reference and web UI features
- **[Simple UI Guide](SIMPLE_UI_GUIDE.md)**: Clean interface usage and benefits
- **[Bulk Operations](ACTIONS_GUIDE.md#bulk-operations)**: Multi-resource management examples
- **[Advanced Scaling](ACTIONS_GUIDE.md#advanced-scaling-operations)**: Percentage and namespace-wide scaling

### Key Features
- **🔐 Automatic Sessions**: No session management UI needed - just works
- **⚡ Bulk Operations**: Manage dozens of resources with single commands
- **🎯 Smart Targeting**: Use label selectors for precise resource management
- **🔄 Auto-Recovery**: Automatic session restoration and error handling
- **📊 Real-time Monitoring**: Live cluster data with health indicators

---

## 🌐 Web Interface Features

The clean, simple web interface provides:

```bash
# Launch the UI
python launch_ui.py
# or
python quickstart.py
```

### Main Features
- **Upload Once**: Upload kubeconfig, automatically persists across browser refreshes
- **AI Diagnosis**: Full cluster analysis and custom queries with persistent results
- **Quick Actions**: Individual resource operations with real-time feedback
- **Bulk Operations**: Multi-select resources for batch processing
- **Problem Detection**: Automatic identification and one-click fixes

### Interface Tabs
1. **🔍 AI Diagnosis**: Full cluster analysis and custom AI queries
2. **🚀 Quick Actions**: Individual pod and deployment operations
3. **📊 Bulk Operations**: Multi-resource management with advanced options
4. **⚠️ Problems**: Automatic problem detection with quick fixes

---

## 📌 Enhanced Output & Capabilities

### AI Diagnosis
- ✅ **Intelligent Analysis**: AI-generated cluster health assessment
- 🚨 **Targeted Recommendations**: Specific suggestions for your cluster components
- 📊 **Rich Reporting**: Interactive results with persistent history
- 🔍 **Custom Queries**: Ask specific questions about your cluster

### Cluster Operations
- ⚡ **Bulk Restart**: Restart multiple pods/deployments simultaneously  
- 📈 **Smart Scaling**: Scale by percentage, target by labels, namespace-wide operations
- 🎯 **Precise Control**: Individual resource management with immediate feedback
- 🛡️ **Safety Features**: Error isolation, minimum replica enforcement

### Monitoring & Observability
- 📊 **Real-time Status**: Live pod and deployment health monitoring
- ⚠️ **Problem Detection**: Automatic identification of problematic resources
- 🔄 **Health Tracking**: Continuous cluster state monitoring
- 📈 **Resource Metrics**: Replica counts, restart counts, node information

---

## 🧪 Legacy CLI Usage (Optional)

For backward compatibility, you can still use the original CLI commands:

```bash
python main.py diagnose --kubeconfig /path/to/your/kubeconfig
```

Example:

```bash
python main.py diagnose --kubeconfig ~/.kube/dev.yaml
```

---

## 🧭 Roadmap & Future Features

### Near Term (Q4 2025)
- [ ] **PDF/Image Export**: Export cluster reports and session history
- [ ] **Advanced RBAC**: Role-based access control for multi-user environments
- [ ] **Webhook Integration**: Slack/Teams notifications for cluster events
- [ ] **Scheduled Diagnoses**: Automated health checks with alerting

### Long Term (2026)
- [ ] **AI-Automated Fixes**: Autonomous issue resolution with approval workflows
- [ ] **Predictive Analytics**: ML-based anomaly detection and capacity planning  
- [ ] **Multi-Cloud Support**: Azure AKS, Google GKE integration
- [ ] **Enterprise Features**: SSO, audit logs, compliance reporting

---

## 🛡️ License

MIT License – Use freely with credit.
