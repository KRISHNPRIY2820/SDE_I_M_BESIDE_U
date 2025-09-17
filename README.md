# SDE_I_M_BESIDE_U


---


# AI Study Planner Agent  
**README and User Guide**

---

## 🌐 Live Demo

You can try the deployed **Streamlit Apps** here:  

-👉 [Multi-Agent RAG (Full Version)](https://multi-agent-rag-ui-sde-imbesideyou-priyanshi-agrawal.streamlit.app/)  
-👉 [Multi-Agent RAG (Simple Version)](https://multi-agent-rag-ui-simple-sde-imbesideyou-priyanshi-agrawal.streamlit.app/)  
-👉 [Single-Agent Version](https://single-agent-ui-sde-imbesideu-priyanshi-agrawal.streamlit.app/)  


---


## 📌 Introduction
The **AI Study Planner Agent** is a lightweight prototype that automates scheduling and execution of study tasks. It demonstrates:

- Multi-agent collaboration (Planner + Executor).
- Integration with knowledge retrieval (RAG).
- Dual interfaces: CLI and Streamlit.
- Support for batch execution and monitoring.

---

## 📂 Project Structure



ai-agent-study-planner/
├── ai\_agent.py
├── multi\_agent.py
├── multi\_agent\_rag.py
├── ai\_agent\_ui.py
├── multi\_agent\_ui.py
├── multi\_agent\_rag\_ui.py
├── multi\_agent\_rag\_ui\_corrected.py
├── System\_Design\_Document.tex
├── Originality\_Impact.tex
├── Interaction\_Logs/
├── screenshots/
└── README.tex



---

## ⚙️ Requirements and Installation

### Minimal (no installs)  
The CLI scripts (`ai_agent.py`, `multi_agent.py`, `multi_agent_rag.py`) work with **Python 3.8+** and require no external libraries.

### Recommended (Streamlit UI)  
To run Streamlit apps:

```bash
pip install streamlit
````

### Optional (Extended RAG features)

The extended UI (`multi_agent_rag_ui_corrected.py`) can optionally use embeddings and PDF ingestion:

```bash
pip install numpy PyPDF2
pip install sentence-transformers
pip install faiss-cpu   # optional, platform-specific
```

If FAISS is unavailable, the system falls back to substring-based retrieval.

---

## ▶️ How to Run

### CLI

```bash
python ai_agent.py
python multi_agent.py
python multi_agent_rag.py
```

### Streamlit

```bash
streamlit run ai_agent_ui.py
streamlit run multi_agent_ui.py
streamlit run multi_agent_rag_ui.py
streamlit run multi_agent_rag_ui_corrected.py
```

Or use the **hosted versions**:  

-👉 [Multi-Agent RAG (Full Version)](https://multi-agent-rag-ui-sde-imbesideyou-priyanshi-agrawal.streamlit.app/)  
-👉 [Multi-Agent RAG (Simple Version)](https://multi-agent-rag-ui-simple-sde-imbesideyou-priyanshi-agrawal.streamlit.app/)  
-👉 [Single-Agent Version](https://single-agent-ui-sde-imbesideu-priyanshi-agrawal.streamlit.app/)  

---

## 📖 Usage Examples

### CLI Example


📅 AI Study Planner Agent
Enter your tasks (type 'done' when finished):
Task name: Computer network lab exam
Duration (in minutes): 30
Importance (1-5): 5
Deadline (YYYY-MM-DD, or leave blank):
Task name: done

✅ Today's Plan:
09:00 - 09:30: Computer network lab exam


### Multi-Agent RAG Example


📅 Planned Schedule
09:00 - 10:00: Study Machine Learning
10:00 - 10:45: Review Compiler Design

⚡ Running Executor Agent...
▶ Starting: Study Machine Learning at 09:00
📖 Study Note: Machine learning is the study of algorithms
that improve from experience.
✅ Finished: Study Machine Learning at 10:00


### Streamlit

* Enter tasks in the sidebar form.
* Click **Generate Schedule** to display the plan.
* Monitor execution logs in real-time.
* Upload documents in the extended RAG UI for note retrieval.

---

## 🚀 Future Work

* Calendar and notification integration.
* Adaptive scheduling with AI reasoning.
* Collaboration features for study groups.
* Richer retrieval methods beyond simple RAG.

---

## ✅ Submission Checklist

Include the following in your submission:

* Source code files (`.py`).
* System Design Document.
* Originality and Social Impact Document.
* Interaction Logs.
* Screenshots or demo video.
* README (this document).

---

## 📜 License

This project is provided for academic and demonstration purposes.
Free to use with attribution.

---

## 👩‍💻 About Me

Hi! I'm Priyanshi Agrawal, a dual-degree student pursuing:

- **BS in Data Science And Applications** from **IIT Madras** --- **INDIAN INSTITUTE OF TECHNOLOGY MADRAS** --- **DATA SCIENCE AND APPLICATIONS DEPARTMENT , BS DEGREE**
- **B.Tech in Computer Science and Engineering** from **IIT Patna**  --- **Department of Computer Science and Engineering** --- **INDIAN INSTITUTE OF TECHNOLOGY PATNA**


I'm passionate about building reproducible automation pipelines, agentic AI systems, and solving real-world problems through strategic planning and modular design. This repository reflects my commitment to clarity, transparency, and scalable innovation.

Feel free to explore, contribute, or reach out!

---



