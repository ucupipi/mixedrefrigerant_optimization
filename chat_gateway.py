"""
TokenGateway Autonomous Dual-Agent Swarm (DeepSeek Lead + GPT-6 Sol Architect)
Integrated Architecture: /goal, /plan, /btw, /step, /unlazy, /caveman, /ponytail, /unslop, /mlflow
Engineering Engine: NeqSim | Aspen HYSYS | CoolProp | IAPWS-IF97 | AGENTS.md (13 Cardinal Rules)
"""

import os
import sys
import glob
import json
import re
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 1. Muat environment variable dari .env
load_dotenv()

# Pastikan JAVA_HOME diarahkan ke OpenJDK 64-bit yang valid jika belum disetel
if "JAVA_HOME" not in os.environ:
    default_jre = r"C:\Users\khari\AppData\Local\openLCA\jre"
    if os.path.exists(default_jre):
        os.environ["JAVA_HOME"] = default_jre

api_key = os.environ.get("TOKENGATEWAY_API_KEY")
if not api_key:
    print("Error: TOKENGATEWAY_API_KEY belum disetel di file .env!")
    sys.exit(1)

client = OpenAI(
    base_url="https://tokengateway.dev/v1",
    api_key=api_key,
)

LEAD_MODEL = "deepseek-v4.1-flash"
ARCHITECT_MODEL = "gpt-6-sol"
WORKSPACE_ROOT = Path.cwd()
CONSTRAINTS_MANIFEST_PATH = WORKSPACE_ROOT / "ikms_2026" / "ENGINEERING_CONSTRAINTS_MANIFEST.json"
CONSULTATION_LOG_PATH = WORKSPACE_ROOT / "audit" / "LAST_GPT6_ARCHITECT_CONSULTATION.md"

# State global orkestrator
STEP_BY_STEP_MODE = False
ABORT_REQUESTED = False
LAST_TASK: str | None = None
SESSION_CONTEXT_NOTES: list[str] = []

# ==============================================================================
# ASYNC INTERRUPT SUITE — /btw langsung, /interrupt, continue
# Aktif SELAMA agent bekerja, bukan hanya di prompt utama.
# ==============================================================================
import queue
import threading
import time

_INJECT_QUEUE: "queue.Queue[str]" = queue.Queue()
_LISTENER_STOP = threading.Event()
_LISTENER_THREAD: "threading.Thread | None" = None
_LISTENER_LOCK = threading.Lock()


def _kb_listener_loop() -> None:
    """Thread latar: menangkap ketikan user SELAMA agent bekerja.

    Baris yang diketik didorong ke _INJECT_QUEUE lalu dikonsumsi oleh
    _agent_loop() pada batas tool berikutnya. Windows-only (msvcrt);
    jika msvcrt tidak tersedia (mis. non-Windows) thread langsung keluar
    tanpa mengganggu alur utama.
    """
    try:
        import msvcrt
    except Exception:
        return

    buf: list[str] = []
    while not _LISTENER_STOP.is_set():
        try:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\r", "\n"):
                    line = "".join(buf).strip()
                    buf.clear()
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    if line:
                        _INJECT_QUEUE.put(line)
                elif ch in ("\x03", "\x1b"):
                    buf.clear()
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    _INJECT_QUEUE.put("/interrupt")
                elif ch in ("\x00", "\xe0"):
                    try:
                        msvcrt.getwch()
                    except Exception:
                        pass
                elif ch == "\b":
                    if buf:
                        buf.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    buf.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()
            else:
                time.sleep(0.04)
        except Exception:
            time.sleep(0.15)


def start_kb_listener() -> None:
    """Mulai thread pendengar interrupt (idempoten, sekali per proses)."""
    global _LISTENER_THREAD
    with _LISTENER_LOCK:
        if _LISTENER_THREAD is not None and _LISTENER_THREAD.is_alive():
            return
        _LISTENER_STOP.clear()
        _LISTENER_THREAD = threading.Thread(
            target=_kb_listener_loop, name="kb-interrupt-listener", daemon=True
        )
        _LISTENER_THREAD.start()


def stop_kb_listener() -> None:
    """Hentikan thread pendengar interrupt (idempoten)."""
    global _LISTENER_THREAD
    with _LISTENER_LOCK:
        _LISTENER_STOP.set()
        if _LISTENER_THREAD is not None:
            _LISTENER_THREAD.join(timeout=1.0)
            _LISTENER_THREAD = None


def drain_injections(messages: "list[dict]") -> "str | None":
    """Konsumsi seluruh input user yang masuk selama agent bekerja.

    Return 'ABORT' bila user meminta stop, selain itu None.
    Arahan biasa disuntikkan sebagai pesan user agar masuk rencana aktif
    tanpa memulai ulang tugas.
    """
    global ABORT_REQUESTED
    injected = False

    while True:
        try:
            raw = _INJECT_QUEUE.get_nowait()
        except queue.Empty:
            break

        low = raw.strip().lower()

        if low in ("/interrupt", "interrupt", "/stop", "stop", "/abort", "abort", "/halt"):
            ABORT_REQUESTED = True
            print("\n[INTERRUPT] Permintaan stop diterima. Dihentikan di batas tool ini.")
            return "ABORT"

        if low in ("/continue", "continue", "/resume", "resume", "/lanjut", "lanjut", "c"):
            print("\n[INTERRUPT] 'continue' diabaikan: agent memang sedang berjalan.")
            continue

        clean = re.sub(r"^/?\s*(btw|context|ctx|note)\s*", "", raw, flags=re.IGNORECASE).strip()
        if not clean:
            continue

        messages.append({
            "role": "user",
            "content": (
                "[USER MID-FLIGHT INJECTION /btw] "
                f"{clean}\n"
                "INTEGRASIKAN arahan ini SEKARANG ke rencana aktif. "
                "Jangan mengulang tugas dari awal. Lanjutkan dari langkah terakhir."
            ),
        })
        injected = True
        print(f"\n[INJECT] Arahan disuntikkan: '{clean[:90]}'")

    if injected:
        print("[INJECT] Konteks baru masuk. Agent melanjutkan dengan rencana yang disesuaikan.")
    return None


def render_interrupt_help() -> str:
    """Teks bantuan interrupt suite."""
    return (
        "\n" + "-" * 78 + "\n"
        "INTERRUPT SUITE (aktif KAPAN SAJA, termasuk saat agent bekerja)\n"
        "  Ketik arahan lalu Enter .......... sisipkan konteks tanpa hentikan agent\n"
        "  /interrupt | ESC | Ctrl+C ........ hentikan di batas tool berikutnya\n"
        "  continue | /resume ............... lanjutkan tugas terakhir\n"
        "  /btw <teks> ...................... pertanyaan cepat atau konteks\n"
        "  /context <teks> .................. konteks permanen sesi ini\n"
        "  /status .......................... tampilkan state sesi\n"
        "  /step ............................ toggle konfirmasi tiap tool\n"
        "  /manifest ........................ baca batas rekayasa kilang\n"
        "  /help ............................ tampilkan bantuan ini\n"
        + "-" * 78 + "\n"
    )

# ==============================================================================
# TOOL IMPLEMENTATIONS (EKSEKUTOR ALAT LOKAL)
# ==============================================================================

def tool_list_dir(path: str = ".") -> str:
    """Mendaftar isi folder di dalam workspace."""
    try:
        target = (WORKSPACE_ROOT / path).resolve()
        if not target.exists():
            return f"Error: Folder '{path}' tidak ditemukan."
        
        items = []
        for item in sorted(target.iterdir()):
            prefix = "[DIR] " if item.is_dir() else "[FILE]"
            size = f"({item.stat().st_size:,} bytes)" if item.is_file() else ""
            items.append(f"{prefix} {item.name} {size}")
        return "\n".join(items[:100]) or "(Folder kosong)"
    except Exception as e:
        return f"Error saat membaca folder: {e}"

def tool_read_file(path: str, start_line: int = 1, end_line: int = 200) -> str:
    """Membaca isi file teks dalam rentang baris tertentu."""
    try:
        target = (WORKSPACE_ROOT / path).resolve()
        if not target.is_file():
            return f"Error: File '{path}' tidak ditemukan."
        
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            
        total_lines = len(lines)
        start = max(1, start_line)
        end = min(total_lines, end_line)
        
        if start > total_lines:
            return f"Error: start_line ({start}) melebihi total baris ({total_lines})."
            
        selected = lines[start - 1 : end]
        output = [f"{i + start}: {line.rstrip()}" for i, line in enumerate(selected)]
        header = f"=== File: {path} (Baris {start}-{end} dari {total_lines}) ==="
        return header + "\n" + "\n".join(output)
    except Exception as e:
        return f"Error saat membaca file: {e}"

def tool_write_file(path: str, content: str, overwrite: bool = True) -> str:
    """Menulis atau menimpa file di dalam workspace."""
    try:
        target = (WORKSPACE_ROOT / path).resolve()
        if target.exists() and not overwrite:
            return f"Error: File '{path}' sudah ada dan overwrite=False."
            
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Sukses menulis {len(content)} karakter ke '{path}'."
    except Exception as e:
        return f"Error saat menulis file: {e}"

def tool_search_code(query: str, path: str = ".") -> str:
    """Mencari string query di dalam file skrip (.py, .md, .json, .yaml, .txt)."""
    try:
        target = (WORKSPACE_ROOT / path).resolve()
        exts = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".csv"}
        matches = []
        
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache"}]
            for file in files:
                if Path(file).suffix in exts:
                    file_path = Path(root) / file
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f):
                                if query.lower() in line.lower():
                                    rel_path = file_path.relative_to(WORKSPACE_ROOT)
                                    matches.append(f"{rel_path}:{idx + 1} | {line.strip()[:100]}")
                                    if len(matches) >= 30:
                                        break
                    except Exception:
                        pass
            if len(matches) >= 30:
                break
                
        return "\n".join(matches) if matches else f"Tidak ditemukan kemunculan '{query}'."
    except Exception as e:
        return f"Error saat mencari: {e}"

def tool_run_command(command: str) -> str:
    """Menjalankan perintah PowerShell / Shell di dalam workspace (timeout 180 detik)."""
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=180,
        )
        stdout = res.stdout.strip()
        stderr = res.stderr.strip()
        
        parts = []
        if stdout:
            parts.append(f"[STDOUT]\n{stdout}")
        if stderr:
            parts.append(f"[STDERR]\n{stderr}")
        parts.append(f"[EXIT CODE]: {res.returncode}")
        
        return "\n\n".join(parts) if parts else "[Command dieksekusi tanpa output]"
    except subprocess.TimeoutExpired:
        return "Error: Perintah melebihi batas waktu (timeout 180 detik)."
    except Exception as e:
        return f"Error saat menjalankan perintah: {e}"

def tool_read_constraints_manifest() -> str:
    """Membaca batas termodinamika resmi, komposisi gas DCS, dan aturan ML dari ENGINEERING_CONSTRAINTS_MANIFEST.json."""
    try:
        if not CONSTRAINTS_MANIFEST_PATH.exists():
            return "Error: ENGINEERING_CONSTRAINTS_MANIFEST.json tidak ditemukan."
        with open(CONSTRAINTS_MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error saat membaca manifest: {e}"

def tool_consult_gpt6(task: str, context: str = "") -> str:
    """
    Mendelegasikan analisis penalaran tingkat tinggi, audit termodinamika/PIML,
    atau perumusan matematika kompleks kepada GPT-6 Sol (Principal Architect).
    Hasil lengkap disimpan otomatis ke audit/LAST_GPT6_ARCHITECT_CONSULTATION.md.
    """
    print(f"\n" + "=" * 70)
    print(f"[MULTI-AGENT DELEGATION] -> DeepSeek mengutus GPT-6 Sol (Principal Architect)")
    print(f"Task Brief: {task[:120]}...")
    print("=" * 70)
    try:
        user_msg = f"Tugas dari Lead Engineer (DeepSeek):\n{task}\n"
        if context:
            user_msg += f"\nKonteks Teknis / Kode Pendukung:\n{context}\n"
            
        res = client.chat.completions.create(
            model=ARCHITECT_MODEL,
            messages=[
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
        )
        reply = res.choices[0].message.content or "(GPT-6 Sol tidak memberikan output)"
        
        CONSULTATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONSULTATION_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(f"# TUGAS KONSULTASI GPT-6 SOL\n\n## Brief:\n{task}\n\n---\n\n## Telaah Arsitektur Penuh:\n\n{reply}")
            
        print(f"[MULTI-AGENT DELEGATION] <- GPT-6 Sol selesai ({len(reply):,} karakter).")
        print(f"[CATATAN] Naskah lengkap tersimpan di: {CONSULTATION_LOG_PATH.name}")
        print("=" * 70 + "\n")
        
        return f"=== HASIL ANALISIS DARI GPT-6 SOL (PRINCIPAL ARCHITECT) ===\n{reply}"
    except Exception as e:
        return f"Error saat berkonsultasi dengan GPT-6 Sol: {e}"

TOOL_REGISTRY = {
    "list_dir": tool_list_dir,
    "read_file": tool_read_file,
    "write_file": tool_write_file,
    "search_code": tool_search_code,
    "run_command": tool_run_command,
    "read_constraints_manifest": tool_read_constraints_manifest,
    "consult_gpt6_architect": tool_consult_gpt6,
}

# ==============================================================================
# SCHEMA FUNCTION CALLING OPENAI
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "consult_gpt6_architect",
            "description": "WAJIB DIGUNAKAN untuk mendelegasikan tugas penalaran tingkat tinggi, audit matematis rumit, pembuktian termodinamika PR-EOS/NeqSim/HYSYS/Gouy-Stodola, desain arsitektur surrogate PIML, atau peninjauan naskah ilmiah kepada GPT-6 Sol (Principal Architect).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Instruksi spesifik dan rumit yang membutuhkan penalaran mendalam dari GPT-6 Sol"},
                    "context": {"type": "string", "description": "Potongan kode, data, atau konteks teknis yang sudah dibaca dari workspace"}
                },
                "required": ["task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_constraints_manifest",
            "description": "Membaca manifest batasan fisik kilang Badak LNG Plant-3, batas surge kompresor (480 t/h), suction TAL (-45 C), baseline gas 3C-1, rasio uap (4.193 t/MWh), dan kriteria lolos ML dari ENGINEERING_CONSTRAINTS_MANIFEST.json.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "Mendaftar isi folder di dalam workspace proyek.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relatif folder (default '.')"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Membaca baris kode dari file di dalam workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path relatif file yang akan dibaca"},
                    "start_line": {"type": "integer", "description": "Nomor baris awal (default 1)"},
                    "end_line": {"type": "integer", "description": "Nomor baris akhir (default 200)"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Membuat atau menimpa file kode di dalam workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path file yang akan ditulis"},
                    "content": {"type": "string", "description": "Isi lengkap file"},
                    "overwrite": {"type": "boolean", "description": "Apakah menimpa jika file sudah ada (default true)"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Mencari string tertentu di seluruh file kode proyek.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "String atau keyword yang dicari"},
                    "path": {"type": "string", "description": "Subdirektori pencarian (default '.')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Menjalankan perintah PowerShell di workspace (misal: python script.py, pytest, pip list, mlflow).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Perintah PowerShell yang akan dijalankan"}
                },
                "required": ["command"]
            }
        }
    }
]

# ==============================================================================
# INTEGRATED SYSTEM PROMPTS (/GOAL, /PLAN, 13 CARDINAL RULES, SIMULATION TOOLS)
# ==============================================================================

SHARED_CONSTITUTION = """
### CONSTITUTIONAL GOVERNANCE: 13 CARDINAL RULES OF INDUSTRIAL AI (AGENTS.md):
1. ZERO MAGIC NUMBERS & ARBITRARY MULTIPLIERS: All coefficients must derive from PR-EOS, CoolProp, Steam Tables (IAPWS-IF97), or verified DCS datasets (scrubcolumn.xlsx, master_minute_level.parquet). Never invent multipliers.
2. ZERO FAKE REGRESSION: Strict train/test partition (80:20 or chronological) BEFORE fitting any scaler/imputer. Data leakage = fatal error. Criteria: R²_test >= 0.60, Normalized/Relative MAE < 1.0%, power evaluated in MW.
3. ZERO INVENTED GAS COMPOSITIONS: Baseline overhead Scrub Column (3C-1) MUST strictly match DCS median: N2: 0.0536%, C1: 94.5096%, C2: 2.7181%, C3: 1.6738%, iC4: 0.3913%, nC4: 0.5426%, iC5: 0.000157%, HHV: 1076.3876 BTU/scf. Heavy slip follows exponential VLE, never linear approximations.
4. ZERO FAKE DELTA OFFSETS: Column tray temperature gradients must couple directly to heat balances and VLE curves, not static frozen offsets.
5. FIRST-PRINCIPLES GROUND TRUTH:
   - MCHE: 100-slice Riemann integral pinch analysis. Minimum MITA >= 1.50°C. Temperature crossover (ΔT <= 0) is forbidden.
   - Compressors: Centrifugal C3 (4K-1/2/3) and MCR (4K-4) must respect flow floor >= 480.0 t/h. Secondary kickback 4UV-53 modulates for anti-surge. Isentropic power: W_shaft = (m_dot * delta_h_s) / eta_p.
   - Suction Drum: TAL interlock T_suct >= -45.0°C. Suction reheat 4TV-510 modulates to prevent liquid carryover.
   - Simplex S^4 & Mahalanobis Distance: Aitchison ILR coordinates. D_M = sqrt((z - mu)^T Sigma^-1 (z - mu)) <= 3.080216 (chi^2 95%, 4 DoF).
6. ZERO FAKE MIMICS & PFD DEVIATIONS: Accurate Centum VP layouts, equipment geometry (stepped swage 3C-4, hemispherical domes 3C-6/8), single source of piping truth.
7. ZERO SCOPE CREEP: Strict boundaries. Do not alter uninstructed plant subsystems.
8. ZERO PRETENTIOUS AI JARGON (/unslop): Forbid "turndown paradox", "thermal glove", "aerodynamic bypass", "tapestry", "pivotal", "delve". Use authentic Badak LNG plant engineering language.
9. PRIMARY DECISION VECTOR: Multicomponent MR composition (N2, C1, C2, C3) and circulation rate m_MR. Valves 4UV-53 and 4TV-510 are safety boundary enablers, not solution variables.
10. POWER DECOMPOSITION MANDATE: Total C3MR savings (~28.98 MW / -27.10% at P90 turndown) must decompose transparently: direct MCR compressor (10.83 MW) + C3 precooling at 3E-14/17/18 (18.15 MW).
11. ZERO LUMPED EXERGY: MCHE exergy destruction: E_D = T_0 * sum(delta_Q_i * (1/T_cold,i - 1/T_hot,i)). Compressor Gouy-Stodola: E_D,comp = W_shaft * (1 - eta_s).
12. ZERO FAKE STATIC MCR ASSUMPTION: Plant operators dynamically adjust MCR composition (2,531 shift samples).
13. ZERO AMBIGUOUS METRICS: Power metrics must be in proportional MW with Relative MAE < 1.0%.

### OPERATIONAL SKILLS & INTERRUPT PROTOCOL (/plan, /goal, /btw):
- /plan: Always construct an explicit execution strategy, file change list, and testable acceptance gates before touching code.
- /goal: Execute autonomously across multiple iterations until every gate passes and verifiable evidence is produced.
- /btw: User can provide mid-flight guidance, side questions, or corrections. You must immediately integrate user /btw inputs into your active plan without restarting the task from scratch.
- /unlazy: Zero placeholders (never leave `// TODO`, `# nanti dilengkapi`). Write 100% complete, runnable, production code.
- /caveman: Answer first: `[thing] [action] [reason].` Max 20 words per sentence. Zero pleasantries. 100% payload preserved.
- /ponytail: Minimal working diff. Cite `file:line` for all findings. Deletion beats addition.
- /mlflow: Track parameters, holdout metrics (r2_test, nmae_relative_pct), and log models/artifacts.
- /awesome-scientific-skills: Curated index of 207+ installed scientific agent skills (InternScience catalog at `C:\\Users\\khari\\.gemini\\config\\plugins\\internscience\\skills\\`). Search via `python C:\\Users\\khari\\.gemini\\config\\skills\\awesome-scientific-skills\\scripts\\search_skills.py <query>`. Covers chemical structure, fluid mechanics, buoyancy, atmospheric physics, and thermodynamic properties.
- /ai-hysys-basic-package: Industrial standard for controlling Aspen HYSYS (V14/V15) COM automation (`win32com.client.Dispatch("HYSYS.Application")`). Takeover existing cases (`C3MR.hsc`, `MACHINELEARNINGMCR4E40ADDED_R47A3B_WORKING.hsc`), bounded parameter tuning, mandatory iterative convergence gate (`Solver.IsSolving == False` is IDLE not CONVERGED; require two consecutive passing readbacks, save-close-reopen validation, explicit tear residuals and mass/energy closure), and export machine-readable CSV/JSON/MD outputs first.
- Domain Engines:
  * NeqSim: PR-EOS/CPA VLE, phase envelope, dew point MCHE shell (-75.35°C), enthalpy departure.
  * Aspen HYSYS: C3MR Train H flowsheet, MCHE 100-slice rating, compressor curves (4K-1/2/3/4), surge floor 480 t/h.
  * CoolProp: Helmholtz high-accuracy EOS for propane precooling loop AND Peng-Robinson AbstractState('PR', '...') for zero-JVM C++ flash.
  * Steam Tables (IAPWS-IF97): Turbine 4KT-1/2/3 steam rates (4.193 t/MWh), boiler fuel gas (97.70 Nm³/t).
"""

LEAD_SYSTEM_PROMPT = f"""You are the Lead Autonomous AI & Systems Orchestrator (DeepSeek V4.1 Flash) for the Badak LNG Plant-3 OTS & AI C3MR Optimization Suite.

MISSION:
You plan, inspect, coordinate, and execute all engineering tasks. You have immediate access to `read_constraints_manifest` to pull official plant limits.
When facing complex thermodynamic proofs, PR-EOS derivations, Gouy-Stodola exergy formulations, or high-stakes paper reviews, you MUST consult GPT-6 Sol via `consult_gpt6_architect`.
For coding and tests, you inspect files, write complete code, and execute pytest / python via `run_command`.
Respond to user `/btw` interrupts and context updates attentively and adaptively.

{SHARED_CONSTITUTION}
"""

ARCHITECT_SYSTEM_PROMPT = f"""You are the Principal AI Process & Thermodynamics Architect (GPT-6 Sol) for the Badak LNG Plant-3 OTS & AI C3MR Optimization Suite (OilWeek 2026).
You are consulted by Lead Engineer (DeepSeek) on theoretical, thermodynamic, and ML architecture proofs.

MISSION:
Provide deep, mathematically rigorous, unassailable engineering analyses. Cite exact physical equations, thermodynamic derivation steps (PR-EOS, NeqSim, Aspen HYSYS, CoolProp, IAPWS-IF97), and explicit code diffs.

{SHARED_CONSTITUTION}
"""

def get_latest_antigravity_transcript() -> str | None:
    """Mencari file transcript percakapan Antigravity terbaru."""
    brain_dir = os.path.expanduser(r"~\.gemini\antigravity\brain")
    pattern = os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl")
    transcripts = glob.glob(pattern)
    if not transcripts:
        return None
    transcripts.sort(key=os.path.getmtime, reverse=True)
    return transcripts[0]

def load_antigravity_history(limit_turns: int = 8, max_chars: int = 14000) -> list[dict]:
    """Mengekstrak percakapan user dan assistant dari log Antigravity dengan proteksi context window."""
    transcript_path = get_latest_antigravity_transcript()
    if not transcript_path or not os.path.exists(transcript_path):
        return []

    history = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    if d.get("type") == "USER_INPUT" and d.get("source") == "USER_EXPLICIT":
                        raw = d.get("content", "")
                        m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", raw, re.DOTALL)
                        text = m.group(1).strip() if m else raw.strip()
                        if text:
                            if len(text) > 1200:
                                text = text[:1000] + "\n[...input dipangkas demi batas context window...]"
                            history.append({"role": "user", "content": text})
                    elif d.get("type") == "PLANNER_RESPONSE" and d.get("source") == "MODEL":
                        content = d.get("content")
                        if content and content.strip():
                            text = content.strip()
                            if len(text) > 1500:
                                text = text[:1200] + "\n[...respons dipangkas demi batas context window...]"
                            history.append({"role": "assistant", "content": text})
                except Exception:
                    continue
    except Exception as e:
        print(f"Peringatan: Gagal membaca riwayat Antigravity: {e}")

    trimmed = history[-limit_turns:] if limit_turns else history
    while trimmed and sum(len(x["content"]) for x in trimmed) > max_chars:
        trimmed.pop(0)

    return trimmed

def prune_messages_for_context(messages: list[dict], max_chars: int = 26000, aggressive: bool = False) -> None:
    """
    Menjaga ukuran messages agar tidak melebihi batas upstream route TokenGateway (400 context_length_exceeded).
    1. Truncate isi tool output lama (>2 iterasi).
    2. Jika masih melebihi budget, buang turn tertua setelah system prompt secara atomik (assistant + tools).
    """
    if not messages:
        return
        
    def calc_chars():
        total = 0
        for m in messages:
            content = m.get("content") if isinstance(m, dict) else getattr(m, "content", None)
            if isinstance(content, str):
                total += len(content)
            elif content:
                total += len(str(content))
        return total

    # Tahap 1: Pangkas tool output lama
    total = calc_chars()
    if total > max_chars or aggressive:
        for idx in range(1, max(1, len(messages) - 2)):
            msg = messages[idx]
            role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
            if role == "tool":
                content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
                if len(content) > 300:
                    new_c = content[:150] + "\n[...ringkasan tool output lama dipangkas demi batas context upstream...]\n" + content[-100:]
                    if isinstance(msg, dict):
                        msg["content"] = new_c
                    else:
                        msg.content = new_c

    # Tahap 2: Jika masih melebihi, buang turn tertua setelah system prompt
    while calc_chars() > max_chars and len(messages) > 3:
        del_idx = 1
        target = messages[del_idx]
        has_tools = False
        if isinstance(target, dict):
            has_tools = bool(target.get("tool_calls"))
        else:
            has_tools = bool(getattr(target, "tool_calls", None))
            
        messages.pop(del_idx)
        
        # Hapus tool messages pasangannya jika ada
        if has_tools:
            while del_idx < len(messages):
                next_role = messages[del_idx].get("role") if isinstance(messages[del_idx], dict) else getattr(messages[del_idx], "role", None)
                if next_role == "tool":
                    messages.pop(del_idx)
                else:
                    break

def handle_interrupt_prompt(messages: list[dict], current_step: int) -> str | None:
    """Menu jeda interaktif saat user menekan Ctrl+C atau meminta interrupt."""
    print("\n" + "!" * 75)
    print(f"[PAUSE / INTERRUPT] Eksekusi dihentikan sementara pada Langkah ke-{current_step}.")
    print("Opsi:")
    print("  - Ketik apa saja / '/btw <instruksi>' : Menambahkan koreksi/konteks baru lalu lanjut.")
    print("  - Tekan [Enter] atau ketik 'c'        : Melanjutkan eksekusi saat ini.")
    print("  - Ketik 'stop' atau 'batal'           : Menghentikan iterasi dan kembali ke menu utama.")
    print("!" * 75)
    
    try:
        user_choice = input(f"[Interrupt Step {current_step}] Anda > ").strip()
        if not user_choice or user_choice.lower() in ["c", "continue", "lanjut"]:
            print("[*] Melanjutkan eksekusi...")
            return None
        if user_choice.lower() in ["stop", "batal", "abort"]:
            print("[*] Menghentikan iterasi tugas.")
            return "USER_STOPPED"
            
        # Jika user memasukkan teks /btw
        clean_msg = user_choice
        if clean_msg.lower().startswith("/btw "):
            clean_msg = clean_msg[5:].strip()
        elif clean_msg.lower().startswith("btw "):
            clean_msg = clean_msg[4:].strip()
            
        feedback_entry = {
            "role": "user",
            "content": f"[USER INTERRUPT GUIDANCE / BTW AT STEP {current_step}]: {clean_msg}"
        }
        messages.append(feedback_entry)
        print(f"[*] Arahan /btw berhasil disuntikkan: '{clean_msg[:80]}...'")
        print("[*] Melanjutkan dengan konteks baru...")
        return None
    except KeyboardInterrupt:
        print("\n[*] Force stop diminta.")
        return "USER_STOPPED"

def execute_agent_turn(messages: list[dict], model: str = LEAD_MODEL, max_iterations: int = 35) -> str:
    """Menjalankan loop interaksi LLM dengan dukungan Interrupt (Ctrl+C), /btw, dan /step."""
    global STEP_BY_STEP_MODE, ABORT_REQUESTED
    ABORT_REQUESTED = False
    start_kb_listener()
    print('    [INTERRUPT LIVE] Ketik arahan lalu Enter kapan saja. ESC = stop.')
    try:
        return _agent_loop(messages, model, max_iterations)
    finally:
        stop_kb_listener()


def _agent_loop(messages: list[dict], model: str, max_iterations: int) -> str:
    global STEP_BY_STEP_MODE, ABORT_REQUESTED
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        if drain_injections(messages) == 'ABORT':
            return '[INTERRUPT] Eksekusi dihentikan atas permintaan pengguna.'
        
        retries = 2
        response = None
        while retries >= 0:
            try:
                prune_messages_for_context(messages, max_chars=26000 if retries == 2 else 16000)
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOLS_SCHEMA,
                    tool_choice="auto",
                )
                break
            except KeyboardInterrupt:
                action = handle_interrupt_prompt(messages, iteration)
                if action == "USER_STOPPED":
                    return "[INTERRUPT] Eksekusi dihentikan oleh pengguna."
                continue
            except Exception as e:
                err_str = str(e).lower()
                if ("context_length" in err_str or "context length" in err_str or "400" in err_str) and retries > 0:
                    print(f"\n[*] Terdeteksi batas context window upstream ({e}). Melakukan auto-pruning memori ({retries} retry tersisa)...")
                    prune_messages_for_context(messages, max_chars=16000, aggressive=True)
                    retries -= 1
                    continue
                return f"Error API saat iterasi {iteration}: {e}"

        if not response:
            return f"Error: Tidak ada respons dari model saat iterasi {iteration}."
        
        msg = response.choices[0].message
        messages.append(msg)
        
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args_raw = tool_call.function.arguments
                
                try:
                    fn_args = json.loads(fn_args_raw)
                except Exception:
                    fn_args = {}
                    
                print(f"\n[ORCHESTRATOR STEP {iteration}] Tool Target: {fn_name}({fn_args_raw[:100]}...)")
                
                # Jika mode /step aktif: minta konfirmasi sebelum menjalankan alat
                if STEP_BY_STEP_MODE:
                    print(f"  [STEP CONFIRMATION] Jalankan tool '{fn_name}'? (Tekan Enter=Ya, /btw <teks>, 'skip'=Lewati, 'stop'=Berhenti)")
                    try:
                        step_input = input(f"  [Step {iteration}] Konfirmasi > ").strip()
                        if step_input.lower() in ["stop", "batal"]:
                            return "[INTERRUPT] Dihentikan saat konfirmasi step."
                        if step_input.lower() in ["skip", "s"]:
                            print(f"  [*] Tool {fn_name} dilewati.")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": "Tool call dilewati atas instruksi pengguna (skipped).",
                            })
                            continue
                        if step_input and (step_input.lower().startswith("/btw") or step_input.lower().startswith("btw")):
                            clean_txt = re.sub(r"^/?[bB][tT][wW]\s*", "", step_input).strip()
                            messages.append({
                                "role": "user",
                                "content": f"[USER PRE-TOOL GUIDANCE]: {clean_txt}"
                            })
                            print(f"  [*] Arahan pre-tool dicatat: {clean_txt[:60]}...")
                    except KeyboardInterrupt:
                        action = handle_interrupt_prompt(messages, iteration)
                        if action == "USER_STOPPED":
                            return "[INTERRUPT] Dihentikan oleh pengguna."
                
                executor = TOOL_REGISTRY.get(fn_name)
                try:
                    if executor:
                        tool_result = executor(**fn_args)
                    else:
                        tool_result = f"Error: Tool '{fn_name}' tidak dikenal."
                except KeyboardInterrupt:
                    action = handle_interrupt_prompt(messages, iteration)
                    if action == "USER_STOPPED":
                        return "[INTERRUPT] Dihentikan saat eksekusi tool."
                    tool_result = "[Tool execution interrupted by user]"
                    
                res_str = str(tool_result).strip()
                if len(res_str) > 200:
                    snippet = res_str[:200].replace("\n", " ") + "..."
                else:
                    snippet = res_str.replace("\n", " ")
                print(f"[TOOL OUTPUT] ({len(res_str):,} chars) -> {snippet}")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": res_str,
                })
        else:
            return msg.content or ""
            
    return (
        "[ORCHESTRATOR] Batas iterasi tool (/goal budget) tercapai "
        f"({max_iterations} langkah).\n"
        "Ketik 'continue' untuk melanjutkan dari titik ini, atau "
        "'/goal 60' lalu ulangi perintah untuk menambah anggaran langkah."
    )

def main():
    global STEP_BY_STEP_MODE
    print("=" * 82)
    print("  TokenGateway Dual-Agent Swarm (DeepSeek Lead + GPT-6 Sol Architect)")
    print("  Engine: /goal + /plan + /btw + /step + /unlazy + /caveman + /ponytail + /mlflow")
    print("  Domain: NeqSim | Aspen HYSYS | CoolProp | AGENTS.md (13 Cardinal Rules)")
    print("=" * 82)
    
    ag_history = load_antigravity_history(limit_turns=8, max_chars=14000)
    messages = [{"role": "system", "content": LEAD_SYSTEM_PROMPT}]
    
    if ag_history:
        messages.extend(ag_history)
        print(f"[*] Sinkronisasi {len(ag_history)} pesan Antigravity sukses ({sum(len(x['content']) for x in ag_history):,} chars).")
        print("    Konteks percakapan & kode aktif di memori tim AI.")
    else:
        print("[-] Tidak ada riwayat Antigravity aktif. Memulai sesi baru.")
        
    print(f"[*] Lead Orchestrator  : {LEAD_MODEL} (247M tokens pool)")
    print(f"[*] Principal Architect : {ARCHITECT_MODEL} (33.8M tokens pool - auto-delegated)")
    print("    INTERRUPT LIVE : ketik arahan lalu Enter kapan saja saat agent bekerja")
    print("                     ESC / Ctrl+C = stop | 'continue' = lanjutkan tugas terakhir")
    print("    Perintah Cepat : /btw <teks> | /context <teks> | /compact | /status | /help")
    print("                     /step (toggle konfirmasi) | /manifest | reload | exit")
    print("-" * 82)
    
    while True:
        try:
            status_indicator = " [STEP-BY-STEP]" if STEP_BY_STEP_MODE else ""
            user_input = input(f"\n[Anda -> Lead DeepSeek{status_indicator}] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "keluar", "quit", "q"]:
                print("Sesi orchestrator diakhiri.")
                break
            if user_input.lower() in ["/compact", "compact"]:
                before_len = len(messages)
                prune_messages_for_context(messages, max_chars=14000, aggressive=True)
                print(f"[*] /compact selesai: Memori dipangkas dari {before_len} menjadi {len(messages)} item.")
                continue
            if user_input.lower() == "reload":
                ag_history = load_antigravity_history(limit_turns=8, max_chars=14000)
                messages = [{"role": "system", "content": LEAD_SYSTEM_PROMPT}] + ag_history
                print(f"[*] Berhasil memuat ulang {len(ag_history)} pesan dari Antigravity!")
                continue
            if user_input.lower() == "/manifest" or user_input.lower() == "manifest":
                print(tool_read_constraints_manifest())
                continue
            if user_input.lower() == "/step" or user_input.lower() == "step":
                STEP_BY_STEP_MODE = not STEP_BY_STEP_MODE
                status = "AKTIF (Setiap aksi tool akan meminta konfirmasi)" if STEP_BY_STEP_MODE else "NON-AKTIF (Eksekusi otonom penuh)"
                print(f"[*] Mode Step-by-Step sekarang: {status}")
                continue
                
            # Penanganan khusus perintah /btw atau btw di prompt utama
            if user_input.lower().startswith("/btw ") or user_input.lower().startswith("btw "):
                side_note = re.sub(r"^/?[bB][tT][wW]\s*", "", user_input).strip()
                
                # Cek apakah ini pertanyaan singkat atau penambahan konteks
                if side_note.endswith("?") or side_note.lower().startswith(("apakah", "kenapa", "apa", "bagaimana", "siapa")):
                    print(f"\n[*] Menjawab pertanyaan cepat (/btw mode)...")
                    quick_prompt = [
                        {"role": "system", "content": "You are a concise engineering assistant. Answer this quick contextual question directly in 1-2 paragraphs without calling complex tools."},
                        {"role": "user", "content": side_note}
                    ]
                    try:
                        q_res = client.chat.completions.create(model=LEAD_MODEL, messages=quick_prompt)
                        ans = q_res.choices[0].message.content or ""
                        print(f"\n[BTW JAWABAN CEPAT] >\n{ans}\n")
                        # Catat ke history agar konteks tetap terjaga
                        messages.append({"role": "user", "content": f"[Side Question]: {side_note}"})
                        messages.append({"role": "assistant", "content": ans})
                        continue
                    except Exception as e:
                        print(f"Gagal memproses pertanyaan cepat: {e}")
                else:
                    # Penambahan konteks pasif
                    messages.append({
                        "role": "system",
                        "content": f"[USER INJECTED CONTEXT VIA /BTW]: {side_note}"
                    })
                    print(f"[*] Konteks berhasil disuntikkan ke memori: '{side_note[:80]}...'")
                    continue
                
            if user_input.lower() in ("/help", "help", "/?"):
                print(render_interrupt_help())
                continue

            if user_input.lower().startswith("/context ") or user_input.lower().startswith("/ctx "):
                note = re.sub(r"^/?\s*(context|ctx)\s*", "", user_input, flags=re.IGNORECASE).strip()
                if note:
                    SESSION_CONTEXT_NOTES.append(note)
                    messages.append({
                        "role": "system",
                        "content": f"[PERMANENT SESSION CONTEXT] {note}",
                    })
                    print(f"[*] Konteks permanen tersimpan (#{len(SESSION_CONTEXT_NOTES)}): '{note[:90]}'")
                continue

            if user_input.lower() in ("/status", "status"):
                print(
                    "\n=== STATUS SESI ==="
                    f"\n  Pesan dalam konteks   : {len(messages)}"
                    f"\n  Catatan /context      : {len(SESSION_CONTEXT_NOTES)}"
                    f"\n  Mode step-by-step     : {'AKTIF' if STEP_BY_STEP_MODE else 'NON-AKTIF'}"
                    f"\n  Tugas terakhir        : {(LAST_TASK[:90] + '...') if LAST_TASK else '(belum ada)'}"
                    f"\n  Antrian injeksi       : {_INJECT_QUEUE.qsize()}\n"
                )
                continue

            if user_input.lower() in ("continue", "/continue", "resume", "/resume", "lanjut", "/lanjut"):
                if not LAST_TASK:
                    print("[*] Tidak ada tugas untuk dilanjutkan. Berikan perintah baru.")
                    continue
                messages.append({
                    "role": "user",
                    "content": (
                        "[CONTINUE] Lanjutkan tugas sebelumnya dari titik terakhir. "
                        "Jangan ulangi langkah yang sudah selesai dan terverifikasi. "
                        f"Tugas acuan: {LAST_TASK}"
                    ),
                })
                print(f"\n[*] Melanjutkan tugas: {LAST_TASK[:90]}...")
                print("    (Ketik arahan lalu Enter kapan saja, ESC = stop)\n")
                reply = execute_agent_turn(messages, LEAD_MODEL)
                print(f"\n[HASIL KOLABORASI DEEPSEEK + GPT-6 SOL] >\n{reply}")
                continue

            LAST_TASK = user_input
            messages.append({"role": "user", "content": user_input})

            print("\nLead DeepSeek menganalisis & mengoordinasikan tim...")
            print("    (Ketik arahan lalu Enter kapan saja, ESC = stop)\n")
            reply = execute_agent_turn(messages, LEAD_MODEL)
            print(f"\n[HASIL KOLABORASI DEEPSEEK + GPT-6 SOL] >\n{reply}")
            
        except KeyboardInterrupt:
            print("\n[*] Sesi chat diakhiri (atau tekan Enter untuk lanjut obrolan).")
            continue
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
