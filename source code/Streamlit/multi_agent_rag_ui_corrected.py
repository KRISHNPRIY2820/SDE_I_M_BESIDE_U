# multi_agent_rag_ui_corrected.py
"""
Extended Streamlit app implementing:
- Multi-agent collaboration (Planner + Executor)
- Real-ish RAG integration using sentence-transformers + FAISS (with graceful fallback)
- UI for adding/editing/deleting tasks and schedule monitoring
- Batch / parallel execution support
- Hooks for external tools (MCP / custom tools) via a simple plugin interface

Dependencies:
    pip install streamlit sentence-transformers faiss-cpu numpy PyPDF2
"""

import streamlit as st
import datetime
import time
import threading
import uuid
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Optional RAG deps
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
    EMBEDDINGS_AVAILABLE = True
except Exception:
    EMBEDDINGS_AVAILABLE = False

# PDF handling
try:
    import PyPDF2
    PDF_SUPPORTED = True
except ImportError:
    PDF_SUPPORTED = False

# -------------------------
# Config
# -------------------------
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800  # characters

# -------------------------
# Simple VectorStore wrapper (FAISS) with fallback
# -------------------------
class SimpleVectorStore:
    def __init__(self):
        self.meta = []  # metadata dicts
        self.vectors = None
        self.index = None
        self.dim = None
        if EMBEDDINGS_AVAILABLE:
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        else:
            self.model = None

    def _embed(self, texts: List[str]):
        if self.model is None:
            # fallback: zero vector
            return np.zeros((len(texts), 1), dtype="float32") if 'np' in globals() else [[0] for _ in texts]
        return np.array(self.model.encode(texts, convert_to_numpy=True), dtype="float32")

    def add_documents(self, docs: List[Dict[str, Any]]):
        texts = [d["text"] for d in docs]
        embeddings = self._embed(texts)
        if self.vectors is None:
            self.vectors = embeddings
            self.meta = docs.copy()
            self.dim = embeddings.shape[1] if hasattr(embeddings, 'shape') else None
        else:
            self.vectors = np.vstack([self.vectors, embeddings])
            self.meta.extend(docs)

        if EMBEDDINGS_AVAILABLE and self.dim is not None:
            try:
                self.index = faiss.IndexFlatL2(self.dim)
                self.index.add(self.vectors)
            except Exception:
                self.index = None

    def similarity_search(self, query: str, k: int = 3):
        if EMBEDDINGS_AVAILABLE and self.index is not None:
            q_emb = self._embed([query])
            D, I = self.index.search(q_emb, k)
            results = []
            for idx in I[0]:
                if idx < len(self.meta):
                    results.append(self.meta[idx])
            return results
        # fallback: substring match
        results = []
        q = query.lower()
        for m in self.meta:
            if q in m["text"].lower() or q in m.get("source", "").lower():
                results.append(m)
                if len(results) >= k:
                    break
        return results

# -------------------------
# Document ingestion helpers
# -------------------------
def chunk_text(text: str, size: int = CHUNK_SIZE):
    return [text[i:i+size] for i in range(0, len(text), size)]

def extract_text_from_pdf(file) -> str:
    if not PDF_SUPPORTED:
        return ""
    reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

# -------------------------
# Tool interface
# -------------------------
class ToolInterface:
    def __init__(self):
        self.tools = {}

    def register(self, name, fn):
        self.tools[name] = fn

    def call(self, name, payload: Dict[str, Any]):
        if name not in self.tools:
            raise ValueError(f"Tool {name} not registered")
        return self.tools[name](payload)

TOOLS = ToolInterface()

def web_search_tool(payload):
    query = payload.get("query", "")
    return {"results": [f"Simulated search result for '{query}' (1)", f"(2)"]}

TOOLS.register("web_search", web_search_tool)

# -------------------------
# Agents
# -------------------------
@dataclass
class Task:
    id: str
    name: str
    duration: int
    importance: int
    deadline: Optional[datetime.date] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class PlannerAgent:
    def __init__(self, available_hours=8, start_hour=9):
        self.available_hours = available_hours
        self.start_hour = start_hour

    def plan(self, tasks: List[Task]):
        available_minutes = self.available_hours * 60
        today = datetime.date.today()
        tasks_sorted = sorted(tasks, key=lambda t: (-t.importance, t.deadline or datetime.date.max))
        current_time = datetime.datetime.now().replace(hour=self.start_hour, minute=0, second=0, microsecond=0)

        schedule = []
        for task in tasks_sorted:
            if task.duration <= available_minutes:
                start = current_time
                end = start + datetime.timedelta(minutes=task.duration)
                schedule.append({"task": task, "start": start, "end": end})
                current_time = end
                available_minutes -= task.duration
            else:
                schedule.append({"task": task, "start": None, "end": None})
        return schedule

class ExecutorAgent:
    def __init__(self, rag_store: SimpleVectorStore = None, tools: ToolInterface = None):
        self.rag_store = rag_store
        self.tools = tools

    def _get_notes(self, query: str):
        if self.rag_store is None:
            return "(No RAG store configured)"
        hits = self.rag_store.similarity_search(query, k=2)
        if not hits:
            return "No relevant notes found."
        return "\n---\n".join([f"Source: {h.get('source')}\n{h.get('text')[:600]}" for h in hits])

    def execute_task(self, scheduled_item, log_fn):
        task = scheduled_item["task"]
        start = scheduled_item["start"]
        if start is None:
            log_fn(f"⏭ Skipping backlog task: {task.name}")
            return {"task_id": task.id, "status": "backlog"}

        log_fn(f"▶ Starting: {task.name} ({task.duration} min)")
        if self.tools:
            try:
                tool_out = self.tools.call("web_search", {"query": task.name})
                log_fn(f"🔧 Tool web_search result: {tool_out.get('results')[0]}")
            except Exception as e:
                log_fn(f"Tool error: {e}")

        notes = self._get_notes(task.name)
        log_fn(f"📖 Notes:\n{notes}")

        simulated_seconds = max(1, int(task.duration * 0.05))
        for i in range(simulated_seconds):
            log_fn(f"   working... ({i+1}/{simulated_seconds})")
            time.sleep(0.2)

        log_fn(f"✅ Finished: {task.name}")
        return {"task_id": task.id, "status": "done"}

    def run_schedule_sequential(self, schedule, log_fn):
        results = []
        for item in schedule:
            results.append(self.execute_task(item, log_fn))
        return results

    def run_schedule_parallel(self, schedule, log_fn, max_workers=3):
        threads = []
        results = []
        results_lock = threading.Lock()

        def worker(item):
            res = self.execute_task(item, log_fn)
            with results_lock:
                results.append(res)

        for item in schedule:
            t = threading.Thread(target=worker, args=(item,))
            threads.append(t)

        active = []
        while threads:
            while threads and len(active) < max_workers:
                t = threads.pop(0)
                t.start()
                active.append(t)
            for at in active[:]:
                if not at.is_alive():
                    at.join()
                    active.remove(at)
            time.sleep(0.1)

        for at in active:
            at.join()
        return results

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Study Planner with RAG (Extended)", layout="wide")
st.title("🤖 Multi-Agent Planner + RAG (Extended)")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "schedule" not in st.session_state:
    st.session_state.schedule = []
if "rag_store" not in st.session_state:
    st.session_state.rag_store = SimpleVectorStore()

left, right = st.columns([2,3])

with left:
    st.header("Add / Manage Tasks")
    with st.form("task_form", clear_on_submit=True):
        name = st.text_input("Task name")
        duration = st.number_input("Duration (minutes)", min_value=5, step=5, value=30)
        importance = st.slider("Importance (1 = low, 5 = high)", 1, 5, 3)
        deadline = st.date_input("Deadline (optional)", value=None)
        submitted = st.form_submit_button("Add Task")
        if submitted and name:
            t = Task(id=str(uuid.uuid4()), name=name, duration=int(duration), importance=int(importance), deadline=deadline)
            st.session_state.tasks.append(t)
            st.success(f"Added task: {name}")

    st.markdown("---")
    st.subheader("Current Tasks")
    for i, task in enumerate(list(st.session_state.tasks)):
        exp = st.expander(f"{i+1}. {task.name} — {task.duration}min — imp {task.importance} — dl {task.deadline}")
        with exp:
            new_name = st.text_input(f"Name_{task.id}", value=task.name)
            new_duration = st.number_input(f"Duration_{task.id}", min_value=1, value=task.duration)
            new_importance = st.slider(f"Importance_{task.id}", 1, 5, task.importance)
            if st.button(f"Save_{task.id}"):
                task.name = new_name
                task.duration = int(new_duration)
                task.importance = int(new_importance)
                st.success("Saved")
            if st.button(f"Delete_{task.id}"):
                st.session_state.tasks = [t for t in st.session_state.tasks if t.id != task.id]
                st.warning("Deleted")
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("RAG / Documents")
    uploaded = st.file_uploader("Upload TXT / PDF (TXT preferred for this demo)", accept_multiple_files=True)
    if uploaded:
        docs_to_add = []
        for up in uploaded:
            text = ""
            if up.name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(up)
            else:
                try:
                    text = up.getvalue().decode(errors="ignore")
                except Exception:
                    text = ""
            chunks = chunk_text(text)
            for idx, c in enumerate(chunks):
                docs_to_add.append({"text": c, "source": up.name, "id": f"{up.name}_{idx}"})
        st.session_state.rag_store.add_documents(docs_to_add)
        st.success(f"Ingested {len(docs_to_add)} chunks from {len(uploaded)} files")

    st.markdown("---")
    st.subheader("Tools")
    st.write("Registered tools: ", list(TOOLS.tools.keys()))

with right:
    st.header("Planner & Execution")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Schedule"):
            planner = PlannerAgent()
            st.session_state.schedule = planner.plan(st.session_state.tasks)
            st.success("Schedule generated")
    with col2:
        if st.button("Clear Schedule"):
            st.session_state.schedule = []

    st.subheader("Planned Schedule")
    if st.session_state.schedule:
        for item in st.session_state.schedule:
            t = item["task"]
            if item["start"] is not None:
                st.write(f"{item['start'].strftime('%H:%M')} - {item['end'].strftime('%H:%M')} : {t.name} (imp {t.importance})")
            else:
                st.write(f"BACKLOG: {t.name} (imp {t.importance})")
    else:
        st.write("No schedule. Generate one after adding tasks.")

    st.markdown("---")
    st.subheader("Executor")
    mode = st.radio("Execution mode", ["sequential", "parallel"], index=0)
    max_workers = st.number_input("Max parallel workers (if parallel)", min_value=1, max_value=10, value=3)
    log_area = st.empty()
    log_container = log_area.container()

    if st.button("Run Executor"):
        if not st.session_state.schedule:
            st.warning("Please generate a schedule first")
        else:
            executor = ExecutorAgent(rag_store=st.session_state.rag_store, tools=TOOLS)
            def make_logger(c):
                def logger(msg):
                    c.write(msg)
                return logger

            with log_container:
                if mode == "sequential":
                    executor.run_schedule_sequential(st.session_state.schedule, make_logger(st))
                    st.success("Execution finished")
                else:
                    executor.run_schedule_parallel(st.session_state.schedule, make_logger(st), max_workers=max_workers)
                    st.success("Parallel execution finished")

with st.expander("App diagnostics"):
    st.write({
        "embeddings_available": EMBEDDINGS_AVAILABLE,
        "pdf_supported": PDF_SUPPORTED,
        "num_docs_in_rag": len(st.session_state.rag_store.meta) if hasattr(st.session_state.rag_store, 'meta') else 0,
        "tasks_count": len(st.session_state.tasks),
    })
