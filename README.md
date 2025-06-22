# 🤖 AutoKubeX - AI-Powered Kubernetes Cluster Manager

AutoKubeX is an intelligent assistant that connects to any Kubernetes cluster and diagnoses issues using AI (Gemini or OpenAI). It supports both CLI and web-based interfaces to simplify troubleshooting and will evolve into a full-featured autonomous Kubernetes manager.

---

## 🚀 Features

- 🔍 AI-based diagnosis for cluster health
- 💻 Streamlit Web UI for interactive analysis
- 💬 CLI for automation workflows
- ⚙️ Gemini & OpenAI support
- 📦 Modular architecture for future autoscaling, anomaly detection, and observability
- 📄 Future: Export reports as images/PDF

---

## 📁 Project Structure

```
autokubex/
├── ai_engine/               # AI planner, LLM interface, prompt templates
├── actions/                 # Restart, scale, patch K8s components
├── config/                  # Cluster-specific configuration files
├── interface/
│   ├── cli.py               # Typer CLI interface
│   └── web_ui/dashboard.py  # Streamlit-based dashboard
├── k8s_connector/           # K8s API wrapper, cluster connector, observability
├── models/                  # Trained anomaly models and history tracking
├── tests/                   # Placeholder for unit tests
├── main.py                  # CLI entrypoint
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🧑‍💻 Local Development Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/autokubex.git
cd autokubex
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
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

## 🧪 CLI Usage

To run cluster diagnosis from terminal:

```bash
python main.py diagnose --kubeconfig /path/to/your/kubeconfig
```

Example:

```bash
python main.py diagnose --kubeconfig ~/.kube/dev.yaml
```

---

## 🌐 Web UI (Streamlit)

Launch the Streamlit dashboard:

```bash
streamlit run interface/web_ui/dashboard.py
```

Then open in your browser:  
[http://localhost:8501](http://localhost:8501)

### ✅ Usage Steps:

1. Upload your kubeconfig file (ensure it ends with `.yaml`, `.yml`, or `.conf`).
2. Click **"🔍 Diagnose Cluster"**.
3. View the AI-generated health report in your browser.

---

## 📌 Output

After diagnosis:

- ✅ AI-generated summary of cluster health
- 🚨 Recommendations for components like:
  - Flux CD
  - Karpenter
  - AWS Load Balancer Controller
  - CoreDNS
  - StatefulSets, EBS CSI, and more
- 📊 Displayed as rich markdown
- 🔜 [Coming Soon] Export to PDF/image

---

## 🧭 Roadmap (Coming Soon)

- [ ] Export cluster reports as PDF/image
- [ ] Save diagnosis logs to SQLite
- [ ] Public deployment with GitHub OAuth
- [ ] Slack/MS Teams alert integration
- [ ] AI-planned automated fixes (restart, scale, patch)

---

## 🛡️ License

MIT License – Use freely with credit.
