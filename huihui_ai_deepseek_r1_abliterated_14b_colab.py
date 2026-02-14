#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║       DeepSeek-R1 Abliterated                              ║
║              Made with ❤️  by Uzair Mughal                         ║
║  Runtime: Google Colab GPU + Ollama                             ║
╚══════════════════════════════════════════════════════════════════╝
"""

import subprocess, sys, os, time, json, signal, re, threading, shutil, datetime

MODEL_NAME = "huihui_ai/deepseek-r1-abliterated:14b"
MODEL_TITLE = "DeepSeek-R1 Abliterated"
MADE_BY = "Uzair Mughal"

SYSTEM_PROMPT = ""

START_TIME = time.time()

# ━━━ SECTION 1 — DEPENDENCY INSTALLATION ━━━

def install_dependencies():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "rich"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.panel import Panel; from rich.text import Text
    console = Console()
    banner = Text()
    banner.append("╔══════════════════════════════════════════╗\n", style="bold cyan")
    banner.append("║  " + MODEL_TITLE[:38].ljust(38) + " ║\n", style="bold cyan")
    banner.append("║           Made by " + MADE_BY[:22].ljust(22) + "  ║\n", style="bold cyan")
    banner.append("╚══════════════════════════════════════════╝", style="bold cyan")
    console.print(Panel(banner, title="[bold magenta]🚀 Setup[/]", border_style="bright_blue"))
    packages = [("flask","Flask"),("requests","HTTP"),("psutil","System Monitor"),("gputil","GPU Monitor"),("markdown","Markdown")]
    with Progress(SpinnerColumn("dots"),TextColumn("[bold blue]{task.description}"),BarColumn(bar_width=30,style="cyan",complete_style="green"),TextColumn("[green]{task.percentage:>3.0f}%"),TimeElapsedColumn(),console=console) as prog:
        t = prog.add_task("Installing…", total=len(packages))
        for pkg, label in packages:
            prog.update(t, description=f"📦 Installing {label}…")
            try: subprocess.check_call([sys.executable,"-m","pip","install","-q",pkg],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            except: pass
            prog.advance(t)
        prog.update(t, description="[bold green]✔ All dependencies installed!")
    console.print("[bold green]✔ Dependencies ready!\n")

# ━━━ SECTION 2 — OLLAMA ━━━

def install_ollama(console):
    console.print("\n[bold cyan]⏳ Installing Ollama…[/]")
    try:
        subprocess.run(["which", "zstd"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        console.print("[dim]Installing zstd…[/dim]")
        subprocess.run("apt-get update -qq && apt-get install -y -qq zstd > /dev/null 2>&1", shell=True)
    OLLAMA_VERSION = "0.16.1"
    TAR_URL = f"https://github.com/ollama/ollama/releases/download/v{OLLAMA_VERSION}/ollama-linux-amd64.tar.zst"
    try:
        console.print(f"[dim]Downloading Ollama v{OLLAMA_VERSION}…[/dim]")
        subprocess.run(f'curl --fail --show-error --location "{TAR_URL}" | zstd -d | tar -xf - -C /usr/local', shell=True, check=True)
        ollama_bin = "/usr/local/bin/ollama"
        if os.path.exists(ollama_bin):
            os.chmod(ollama_bin, 0o755)
            console.print("[bold green]✔ Ollama installed![/]")
            return
        result = subprocess.run("find /usr/local -name 'ollama' -type f 2>/dev/null", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            found = result.stdout.strip().split('\n')[0]
            os.chmod(found, 0o755)
            if found != "/usr/local/bin/ollama":
                os.makedirs("/usr/local/bin", exist_ok=True)
                subprocess.run(f"ln -sf {found} /usr/local/bin/ollama", shell=True)
            console.print("[bold green]✔ Ollama installed![/]")
            return
    except: pass
    try:
        subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print("[bold green]✔ Ollama installed![/]")
    except:
        console.print("[bold red]✗ Ollama installation failed[/]")

def start_ollama_server(console):
    console.print("[bold cyan]⏳ Starting Ollama server…[/]")
    env = os.environ.copy(); env["OLLAMA_HOST"] = "0.0.0.0:11434"
    proc = subprocess.Popen(["ollama","serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, preexec_fn=os.setsid)
    import requests as req
    for i in range(60):
        try:
            if req.get("http://localhost:11434/api/tags", timeout=2).status_code == 200:
                console.print("[bold green]✔ Ollama server running![/]"); return proc
        except: pass
        time.sleep(1)
    console.print("[bold red]✗ Ollama server failed to start[/]"); return proc

# ━━━ SECTION 3 — MODEL PULL ━━━

def pull_model(console):
    import requests as req
    from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
    console.print(f"\n[bold cyan]⏳ Pulling model [magenta]{MODEL_NAME}[/magenta]…[/]")
    console.print("[dim]This may take a while depending on model size…[/dim]\n")
    resp = req.post("http://localhost:11434/api/pull", json={"name": MODEL_NAME, "stream": True}, stream=True, timeout=None)
    with Progress(TextColumn("[bold blue]{task.description}"),BarColumn(bar_width=40,style="cyan",complete_style="bright_green"),DownloadColumn(),TransferSpeedColumn(),TimeRemainingColumn(),console=console) as prog:
        tasks = {}
        for line in resp.iter_lines():
            if not line: continue
            try: data = json.loads(line)
            except: continue
            status=data.get("status",""); digest=data.get("digest","default"); total=data.get("total",0); done=data.get("completed",0)
            if total and total > 0:
                short = digest[:12] if digest != "default" else ""
                if digest not in tasks: tasks[digest] = prog.add_task(f"📥 {status} {short}", total=total)
                prog.update(tasks[digest], completed=done, description=f"📥 {status} {short}")
            elif "success" in status.lower(): console.print(f"\n[bold green]✔ Model pulled successfully![/]")
            else:
                if not total: console.print(f"  [dim]{status}[/dim]", end="\r")
    console.print(f"[bold green]✔ {MODEL_NAME} is ready!\n")

# ━━━ SECTION 4 — SYSTEM MONITOR ━━━

def get_system_info():
    import psutil
    info = {"cpu_percent":psutil.cpu_percent(),"ram_total_gb":round(psutil.virtual_memory().total/1e9,1),"ram_used_gb":round(psutil.virtual_memory().used/1e9,1),"ram_percent":psutil.virtual_memory().percent,"disk_total_gb":round(psutil.disk_usage('/').total/1e9,1),"disk_used_gb":round(psutil.disk_usage('/').used/1e9,1),"disk_percent":psutil.disk_usage('/').percent}
    try:
        import GPUtil; gpus = GPUtil.getGPUs()
        if gpus:
            g=gpus[0]; info["gpu_name"]=g.name; info["gpu_vram_total"]=round(g.memoryTotal/1024,1); info["gpu_vram_used"]=round(g.memoryUsed/1024,1); info["gpu_vram_percent"]=round(g.memoryUtil*100,1); info["gpu_temp"]=g.temperature
    except: info["gpu_name"]="N/A"
    info["model"]=MODEL_NAME; info["uptime"]=str(datetime.timedelta(seconds=int(time.time()-START_TIME))); return info

def print_system_dashboard(console):
    from rich.table import Table; from rich.panel import Panel
    info = get_system_info()
    table = Table(show_header=True, header_style="bold magenta", border_style="bright_blue")
    table.add_column("Metric", style="cyan", width=20); table.add_column("Value", style="green", width=30)
    table.add_row("🤖 Model", info["model"]); table.add_row("🖥️  GPU", info.get("gpu_name","N/A"))
    table.add_row("🎮 VRAM", f"{info.get('gpu_vram_used','?')} / {info.get('gpu_vram_total','?')} GB ({info.get('gpu_vram_percent','?')}%)")
    table.add_row("🌡️  Temp", f"{info.get('gpu_temp','N/A')}°C"); table.add_row("💾 RAM", f"{info['ram_used_gb']} / {info['ram_total_gb']} GB ({info['ram_percent']}%)")
    table.add_row("💿 Disk", f"{info['disk_used_gb']} / {info['disk_total_gb']} GB ({info['disk_percent']}%)"); table.add_row("⏱️  Uptime", info["uptime"])
    console.print(Panel(table, title=f"[bold magenta]📊 System Dashboard — by {MADE_BY}[/]", border_style="bright_blue"))

# ━━━ SECTION 5 — CLOUDFLARE TUNNEL ━━━

def start_cloudflare_tunnel(console, port=7860):
    console.print("\n[bold cyan]⏳ Setting up Cloudflare Tunnel…[/]")
    cf_path = "/usr/local/bin/cloudflared"
    if not os.path.exists(cf_path):
        subprocess.run(["wget","-q","https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64","-O",cf_path], check=True)
        os.chmod(cf_path, 0o755)
    log_file = "/tmp/cloudflared.log"
    log_fh = open(log_file, "w")
    proc = subprocess.Popen([cf_path,"tunnel","--url",f"http://localhost:{port}","--no-autoupdate"], stdout=log_fh, stderr=log_fh, preexec_fn=os.setsid)
    url_pattern = re.compile(r'(https://[a-zA-Z0-9_\-]+\.trycloudflare\.com)')
    public_url = None
    for attempt in range(45):
        time.sleep(2)
        try:
            with open(log_file,"r") as f: content=f.read()
            match = url_pattern.search(content)
            if match: public_url=match.group(1); break
            if not match and attempt > 10:
                fallback=re.search(r'(https://[^\s]+\.trycloudflare\.com[^\s]*)', content)
                if fallback: public_url=fallback.group(1).rstrip('/'); break
        except: pass
    if public_url:
        from rich.panel import Panel
        console.print(Panel(f"[bold green]🌐 Public URL: [link={public_url}]{public_url}[/link]\n\n[dim]Share this link with anyone![/dim]\n[bold magenta]Made by {MADE_BY}[/bold magenta]", title="[bold cyan]☁️  Cloudflare Tunnel Active[/]", border_style="bright_green"))
    else:
        console.print("[bold yellow]⚠ Cloudflare tunnel URL not detected yet.[/]")
        try:
            with open(log_file,"r") as f: console.print(f"[dim]{f.read()[-500:]}[/dim]")
        except: pass
        console.print(f"[dim]Web UI at http://localhost:{port}[/dim]")
    return proc, public_url

# ━━━ SECTION 6 — WEB CHAT UI ━━━

WEB_CHAT_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="purple"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTIiIGZpbGw9IiMxYTE3MjYiLz4KPGcgZmlsbD0iIzZlZTdhMCIgdHJhbnNmb3JtPSJzY2FsZSgwLjc1KSB0cmFuc2xhdGUoNCw0KSI+CjxwYXRoIGQ9Ik0xMyw4LjU3Yy0wLjc5LDAtMS40MywwLjY0LTEuNDMsMS40M3MwLjY0LDEuNDMsMS40MywxLjQzczEuNDMtMC42NCwxLjQzLTEuNDNTMTMuNzksOC41NywxMyw4LjU3eiIvPgo8cGF0aCBkPSJNMTMsM0M5LjI1LDMsNi4yLDUuOTQsNi4wMiw5LjY0TDQuMSwxMi4yQzMuODUsMTIuNTMsNC4wOSwxMyw0LjUsMTNINnYzYzAsMS4xLDAuOSwyLDIsMmgxdjNoN3YtNC42OCBjMi4zNi0xLjEyLDQtMy41Myw0LTYuMzJDMjAsNi4xMywxNi44NywzLDEzLDN6IE0xNiwxMGMwLDAuMTMtMC4wMSwwLjI2LTAuMDIsMC4zOWwwLjgzLDAuNjZjMC4wOCwwLjA2LDAuMSwwLjE2LDAuMDUsMC4yNSBsLTAuOCwxLjM5Yy0wLjA1LDAuMDktMC4xNiwwLjEyLTAuMjQsMC4wOWwtMC45OS0wLjRjLTAuMjEsMC4xNi0wLjQzLDAuMjktMC42NywwLjM5TDE0LDEzLjgzYy0wLjAxLDAuMS0wLjEsMC4xNy0wLjIsMC4xN2gtMS42IGMtMC4xLDAtMC4xOC0wLjA3LTAuMi0wLjE3bC0wLjE1LTEuMDZjLTAuMjUtMC4xLTAuNDctMC4yMy0wLjY4LTAuMzlsLTAuOTksMC40Yy0wLjA5LDAuMDMtMC4yLDAtMC4yNS0wLjA5bC0wLjgtMS4zOSBjLTAuMDUtMC4wOC0wLjAzLTAuMTksMC4wNS0wLjI1bDAuODQtMC42NkMxMC4wMSwxMC4yNiwxMCwxMC4xMywxMCwxMGMwLTAuMTMsMC4wMi0wLjI3LDAuMDQtMC4zOUw5LjE5LDguOTUgYy0wLjA4LTAuMDYtMC4xLTAuMTYtMC4wNS0wLjI2bDAuOC0xLjM4YzAuMDUtMC4wOSwwLjE1LTAuMTIsMC4yNC0wLjA5bDEsMC40YzAuMi0wLjE1LDAuNDMtMC4yOSwwLjY3LTAuMzlsMC4xNS0xLjA2IEMxMi4wMiw2LjA3LDEyLjEsNiwxMi4yLDZoMS42YzAuMSwwLDAuMTgsMC4wNywwLjIsMC4xN2wwLjE1LDEuMDZjMC4yNCwwLjEsMC40NiwwLjIzLDAuNjcsMC4zOWwxLTAuNGMwLjA5LTAuMDMsMC4yLDAsMC4yNCwwLjA5IGwwLjgsMS4zOGMwLjA1LDAuMDksMC4wMywwLjItMC4wNSwwLjI2bC0wLjg1LDAuNjZDMTUuOTksOS43MywxNiw5Ljg2LDE2LDEweiIvPgo8L2c+Cjwvc3ZnPg==" />
<title>DeepSeek-R1 Abliterated Chat — by Uzair Mughal</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
.material-symbols-rounded{font-variation-settings:'FILL' 1,'wght' 500,'GRAD' 0,'opsz' 24;vertical-align:middle}
[data-theme="dark"][data-accent="purple"]{--bg:#0f0d1a;--surface:#1a1726;--surface2:#241f33;--surface3:#2e2841;--surface4:#3a3350;--primary:#c9b3ff;--primary-container:#4a3d6e;--on-primary:#1a0e3a;--on-primary-container:#e8deff;--accent:#c9b3ff;--accent2:#a78bfa;--accent-glow:rgba(167,139,250,.2);--text:#e8e4f0;--text2:#9e97ad;--text3:#6b6578;--danger:#f28b82;--outline:#4a4458;--outline-var:#352f40;--gradient:linear-gradient(135deg,#a78bfa 0%,#818cf8 50%,#6366f1 100%)}
[data-theme="dark"][data-accent="green"]{--bg:#0d1a14;--surface:#17261e;--surface2:#1f332a;--surface3:#284136;--surface4:#335043;--primary:#a8d5ba;--primary-container:#2d6e4a;--on-primary:#0e3a24;--on-primary-container:#c4f0d6;--accent:#a8d5ba;--accent2:#6ee7a0;--accent-glow:rgba(110,231,160,.2);--text:#e4f0ea;--text2:#97ad9e;--text3:#657b6e;--danger:#f28b82;--outline:#445a4e;--outline-var:#2f4039;--gradient:linear-gradient(135deg,#6ee7a0 0%,#34d399 50%,#10b981 100%)}
[data-theme="light"][data-accent="purple"]{--bg:#faf7ff;--surface:#f2edf9;--surface2:#ece6f3;--surface3:#e3dceb;--surface4:#d9d1e4;--primary:#6750a4;--primary-container:#e8deff;--on-primary:#fff;--on-primary-container:#1d0160;--accent:#6750a4;--accent2:#7c5cbf;--accent-glow:rgba(103,80,164,.15);--text:#1c1b1f;--text2:#49454f;--text3:#79747e;--danger:#b3261e;--outline:#cac4d0;--outline-var:#e1dce7;--gradient:linear-gradient(135deg,#7c5cbf 0%,#6750a4 50%,#553c8b 100%)}
[data-theme="light"][data-accent="green"]{--bg:#f7fff9;--surface:#edf9f0;--surface2:#e6f3ea;--surface3:#dcebe1;--surface4:#d1e4d7;--primary:#386a4f;--primary-container:#c4f0d6;--on-primary:#fff;--on-primary-container:#02210e;--accent:#386a4f;--accent2:#2d8d56;--accent-glow:rgba(56,106,79,.15);--text:#1a1c1b;--text2:#414942;--text3:#727970;--danger:#b3261e;--outline:#c4d0c8;--outline-var:#dce7df;--gradient:linear-gradient(135deg,#2d8d56 0%,#386a4f 50%,#1e5238 100%)}
html,body{height:100%;font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);overflow:hidden;transition:background .3s,color .3s}
.app{display:flex;height:100vh;position:relative}
.sidebar{width:300px;background:var(--surface);border-right:1px solid var(--outline-var);display:flex;flex-direction:column;transition:transform .3s,background .3s}
.sidebar-header{padding:20px;border-bottom:1px solid var(--outline-var)}
.sidebar-header h2{font-size:13px;font-weight:600;color:var(--accent);text-transform:uppercase;letter-spacing:1.5px;display:flex;align-items:center;gap:8px}
.new-chat-btn{width:100%;margin-top:14px;padding:14px;background:var(--gradient);border:none;border-radius:28px;color:#fff;font-weight:600;cursor:pointer;font-size:14px;transition:all .3s;display:flex;align-items:center;justify-content:center;gap:8px}
.new-chat-btn:hover{transform:translateY(-1px);box-shadow:0 6px 24px var(--accent-glow)}
.chat-list{flex:1;overflow-y:auto;padding:8px}
.chat-item{padding:12px 16px;border-radius:28px;cursor:pointer;margin-bottom:2px;color:var(--text2);font-size:13px;transition:all .2s;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:flex;align-items:center;gap:10px}
.chat-item:hover{background:var(--surface2);color:var(--text)}
.chat-item.active{background:var(--primary-container);color:var(--on-primary-container);font-weight:500}
.chat-item .chat-title{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chat-item .del-btn{display:none;background:none;border:none;color:var(--danger);cursor:pointer;padding:2px;border-radius:50%;flex-shrink:0;line-height:1}
.chat-item .del-btn:hover{background:rgba(242,139,130,.15)}
.chat-item:hover .del-btn{display:flex}
.sidebar-footer{padding:16px 20px;border-top:1px solid var(--outline-var);text-align:center}
.sidebar-footer span{font-size:11px;color:var(--text3)}.sidebar-footer .brand{color:var(--accent);font-weight:600}
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.topbar{padding:12px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--outline-var);background:var(--surface);transition:background .3s}
.topbar .title{font-size:16px;font-weight:600;color:var(--accent);display:flex;align-items:center;gap:8px}
.topbar-actions{display:flex;gap:6px;align-items:center}
.icon-btn{width:40px;height:40px;border-radius:50%;border:none;background:transparent;color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;position:relative}
.icon-btn:hover{background:var(--surface2);color:var(--accent)}
.theme-menu{position:absolute;top:48px;right:0;background:var(--surface2);border:1px solid var(--outline);border-radius:16px;padding:8px;min-width:180px;z-index:200;display:none;box-shadow:0 8px 32px rgba(0,0,0,.3)}
.theme-menu.open{display:block}
.theme-menu-item{padding:10px 14px;border-radius:12px;cursor:pointer;font-size:13px;color:var(--text);display:flex;align-items:center;gap:10px;transition:background .15s}
.theme-menu-item:hover{background:var(--surface3)}
.theme-menu-item.active{background:var(--primary-container);color:var(--on-primary-container);font-weight:500}
.color-dot{width:16px;height:16px;border-radius:50%;flex-shrink:0}
.color-dot.purple{background:linear-gradient(135deg,#a78bfa,#6366f1)}
.color-dot.green{background:linear-gradient(135deg,#6ee7a0,#10b981)}
.theme-divider{height:1px;background:var(--outline-var);margin:6px 0}
.messages{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px;scroll-behavior:smooth}
.msg{display:flex;gap:12px;max-width:80%;animation:msgIn .35s cubic-bezier(.4,0,.2,1)}
.msg.user{align-self:flex-end;flex-direction:row-reverse}
.msg-avatar{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;transition:background .3s}
.msg.user .msg-avatar{background:var(--gradient);color:#fff}
.msg.assistant .msg-avatar{background:var(--surface3);color:var(--accent)}
.msg-bubble{padding:14px 18px;border-radius:20px;font-size:14px;line-height:1.7;word-break:break-word;transition:background .3s,border-color .3s}
.msg.user .msg-bubble{background:var(--primary);color:var(--on-primary);border-bottom-right-radius:6px}
.msg.assistant .msg-bubble{background:var(--surface2);border:1px solid var(--outline-var);border-bottom-left-radius:6px}
.msg-bubble pre{background:var(--bg);padding:14px;border-radius:12px;overflow-x:auto;margin:10px 0;font-family:'JetBrains Mono',monospace;font-size:13px;border:1px solid var(--outline-var)}
.msg-bubble code{font-family:'JetBrains Mono',monospace;font-size:13px}
.msg-bubble p{margin-bottom:8px}.msg-bubble p:last-child{margin-bottom:0}

.think-block{margin:8px 0;border-left:3px solid var(--accent2);background:var(--surface3);border-radius:0 12px 12px 0;overflow:hidden}
.think-header{padding:10px 14px;cursor:pointer;display:flex;align-items:center;gap:8px;font-size:12px;color:var(--accent2);font-weight:500}
.think-header .arrow{transition:transform .2s;font-size:10px}
.think-header.open .arrow{transform:rotate(90deg)}
.think-body{padding:0 14px 10px;font-size:13px;color:var(--text2);display:none;line-height:1.6}
.think-body.open{display:block}
.typing{display:flex;gap:12px;align-items:center;max-width:85%}
.typing .dots{display:flex;gap:5px}
.typing .dots span{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:bounce .6s infinite alternate}
.typing .dots span:nth-child(2){animation-delay:.15s}
.typing .dots span:nth-child(3){animation-delay:.3s}
@keyframes bounce{to{opacity:.3;transform:translateY(-4px)}}
@keyframes msgIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.input-area{padding:14px 20px 18px;border-top:1px solid var(--outline-var);background:var(--surface);transition:background .3s}
.input-wrap{display:flex;gap:10px;align-items:flex-end;max-width:800px;margin:0 auto}
.input-wrap textarea{flex:1;resize:none;border:1px solid var(--outline);border-radius:28px;background:var(--surface2);color:var(--text);padding:14px 20px;font-size:14px;font-family:'Inter',sans-serif;outline:none;max-height:150px;transition:border-color .2s,background .3s;line-height:1.5}
.input-wrap textarea:focus{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-glow)}
.input-wrap textarea::placeholder{color:var(--text3)}
.send-btn{width:48px;height:48px;border-radius:50%;background:var(--gradient);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0;color:#fff}
.send-btn:hover{transform:scale(1.05);box-shadow:0 6px 24px var(--accent-glow)}
.send-btn:disabled{opacity:.35;cursor:not-allowed;transform:none;box-shadow:none}
.footer-text{text-align:center;margin-top:8px;font-size:11px;color:var(--text3)}.footer-text .brand{color:var(--accent);font-weight:600}
.sys-panel{position:fixed;top:0;right:-400px;width:380px;height:100vh;background:var(--surface);border-left:1px solid var(--outline-var);padding:24px;overflow-y:auto;transition:right .3s,background .3s;z-index:100}
.sys-panel.open{right:0}
.sys-panel h3{font-size:14px;color:var(--accent);text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.sys-stat{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--outline-var);font-size:13px}
.sys-stat .label{color:var(--text2);display:flex;align-items:center;gap:6px}.sys-stat .value{color:var(--text);font-weight:500}
.sys-bar{height:6px;background:var(--surface3);border-radius:3px;margin:6px 0 4px;overflow:hidden}
.sys-bar-fill{height:100%;background:var(--gradient);border-radius:3px;transition:width .5s}
.close-panel{position:absolute;top:16px;right:16px;background:none;border:none;color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:50%;transition:background .2s}
.close-panel:hover{background:var(--surface2)}
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;text-align:center;padding:40px}
.welcome h1{font-size:34px;font-weight:700;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.welcome p{color:var(--text2);font-size:15px;max-width:480px;line-height:1.7}
.welcome .features{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:12px}
.welcome .feat{padding:10px 18px;background:var(--surface2);border:1px solid var(--outline-var);border-radius:28px;font-size:12px;color:var(--text2);display:flex;align-items:center;gap:6px;transition:background .3s}
.menu-btn{display:none;background:none;border:none;color:var(--text);cursor:pointer;width:40px;height:40px;border-radius:50%;display:none;align-items:center;justify-content:center;transition:background .2s}
.menu-btn:hover{background:var(--surface2)}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:49}
@media(max-width:768px){.sidebar{position:fixed;left:0;top:0;height:100vh;z-index:50;transform:translateX(-100%)}.sidebar.show{transform:translateX(0)}.overlay.show{display:block}.menu-btn{display:flex}.msg{max-width:95%}.theme-menu{right:-60px}.chat-item .del-btn{display:flex}}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--surface4);border-radius:3px}
</style></head><body>
<div class="app">
<div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
<aside class="sidebar" id="sidebar">
<div class="sidebar-header"><h2><span class="material-symbols-rounded" style="font-size:20px">forum</span> Chat History</h2><button class="new-chat-btn" onclick="newChat()"><span class="material-symbols-rounded">add</span> New Chat</button></div>
<div class="chat-list" id="chatList"></div>
<div class="sidebar-footer"><span>DeepSeek-R1 Abliterated<br><span class="brand">Made by Uzair Mughal</span></span></div>
</aside>
<div class="main">
<header class="topbar">
<div style="display:flex;align-items:center;gap:8px"><button class="menu-btn" onclick="toggleSidebar()"><span class="material-symbols-rounded">menu</span></button><span class="title"><span class="material-symbols-rounded" style="font-size:22px">psychology</span> DeepSeek-R1 Abliterated</span></div>
<div class="topbar-actions">
<button class="icon-btn" onclick="clearChat()" title="Clear Chat"><span class="material-symbols-rounded">delete</span></button>
<button class="icon-btn" onclick="toggleSysPanel()" title="System Monitor"><span class="material-symbols-rounded">monitoring</span></button>
<div style="position:relative"><button class="icon-btn" id="themeBtn" onclick="toggleThemeMenu()" title="Theme"><span class="material-symbols-rounded">palette</span></button>
<div class="theme-menu" id="themeMenu">
<div class="theme-menu-item" onclick="setTheme('dark')"><span class="material-symbols-rounded" style="font-size:20px">dark_mode</span> Dark Mode</div>
<div class="theme-menu-item" onclick="setTheme('light')"><span class="material-symbols-rounded" style="font-size:20px">light_mode</span> Light Mode</div>
<div class="theme-divider"></div>
<div class="theme-menu-item" onclick="setAccent('purple')"><span class="color-dot purple"></span> Purple</div>
<div class="theme-menu-item" onclick="setAccent('green')"><span class="color-dot green"></span> Green</div>
</div></div>
</div>
</header>
<div class="messages" id="messages">
<div class="welcome" id="welcome">
<h1><span class="material-symbols-rounded" style="font-size:36px;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent">psychology</span> DeepSeek-R1 Abliterated</h1>
<p>Running locally via Ollama on a Colab GPU. Ask anything.</p>
<div class="features"><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">lightbulb</span> Reasoning</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">code</span> Coding</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">science</span> Analysis</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">brush</span> Creative</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">translate</span> Multilingual</div></div>
<p style="margin-top:16px;font-size:12px;color:var(--text2)">Made with ❤️ by <span style="color:var(--accent);font-weight:600">Uzair Mughal</span></p>
</div></div>
<div class="input-area"><div class="input-wrap">
<textarea id="userInput" rows="1" placeholder="Type your message…" onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
<button class="send-btn" id="sendBtn" onclick="sendMessage()"><span class="material-symbols-rounded">send</span></button>
</div><div class="footer-text">huihui_ai/deepseek-r1-abliterated:14b • <span class="brand">Made by Uzair Mughal</span></div></div>
</div>
<div class="sys-panel" id="sysPanel"><button class="close-panel" onclick="toggleSysPanel()"><span class="material-symbols-rounded">close</span></button><h3><span class="material-symbols-rounded" style="font-size:20px">monitoring</span> System Monitor</h3><div id="sysStats"></div></div>
</div>
<script>
const MODEL="huihui_ai/deepseek-r1-abliterated:14b";
const MODEL_TITLE="DeepSeek-R1 Abliterated";
const MADE_BY="Uzair Mughal";
let chats=JSON.parse(localStorage.getItem('mc_chats')||'{}');let currentChatId=null;let isGenerating=false;
function uid(){return Date.now().toString(36)+Math.random().toString(36).substr(2,5)}
function save(){localStorage.setItem('mc_chats',JSON.stringify(chats))}
function toggleSidebar(){document.getElementById('sidebar').classList.toggle('show');document.getElementById('overlay').classList.toggle('show')}
function toggleSysPanel(){const p=document.getElementById('sysPanel');p.classList.toggle('open');if(p.classList.contains('open'))loadSysInfo()}
function setTheme(t){document.documentElement.setAttribute('data-theme',t);localStorage.setItem('mc_theme',t);updateThemeMenu()}
function setAccent(a){document.documentElement.setAttribute('data-accent',a);localStorage.setItem('mc_accent',a);updateThemeMenu()}
function toggleThemeMenu(){document.getElementById('themeMenu').classList.toggle('open');updateThemeMenu()}
function updateThemeMenu(){const t=document.documentElement.getAttribute('data-theme');const a=document.documentElement.getAttribute('data-accent');document.querySelectorAll('.theme-menu-item').forEach(el=>{el.classList.remove('active');if(el.textContent.trim()==='Dark Mode'&&t==='dark')el.classList.add('active');if(el.textContent.trim()==='Light Mode'&&t==='light')el.classList.add('active');if(el.textContent.trim()==='Purple'&&a==='purple')el.classList.add('active');if(el.textContent.trim()==='Green'&&a==='green')el.classList.add('active')})}
(function(){const t=localStorage.getItem('mc_theme');const a=localStorage.getItem('mc_accent');if(t)document.documentElement.setAttribute('data-theme',t);if(a)document.documentElement.setAttribute('data-accent',a)})();
document.addEventListener('click',e=>{const m=document.getElementById('themeMenu');const b=document.getElementById('themeBtn');if(m&&m.classList.contains('open')&&!m.contains(e.target)&&e.target!==b&&!b.contains(e.target))m.classList.remove('open')});
function deleteChat(id,e){e.stopPropagation();delete chats[id];save();if(currentChatId===id){const keys=Object.keys(chats);if(keys.length){loadChat(keys.sort((a,b)=>chats[b].ts-chats[a].ts)[0])}else{newChat()}}renderChatList()}
function renderChatList(){const el=document.getElementById('chatList');el.innerHTML='';Object.keys(chats).sort((a,b)=>chats[b].ts-chats[a].ts).forEach(id=>{const c=chats[id];const d=document.createElement('div');d.className='chat-item'+(id===currentChatId?' active':'');d.innerHTML='<span class="material-symbols-rounded" style="font-size:18px">chat_bubble</span><span class="chat-title">'+(c.title||'New Chat')+'</span><button class="del-btn" title="Delete chat"><span class="material-symbols-rounded" style="font-size:18px">delete</span></button>';d.querySelector('.del-btn').addEventListener('click',function(e){deleteChat(id,e)});d.onclick=()=>loadChat(id);el.appendChild(d)})}
function getWelcomeHTML(){return '<div class="welcome" id="welcome"><h1><span class="material-symbols-rounded" style="font-size:36px;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent">psychology</span> '+MODEL_TITLE+'</h1><p>Running locally via Ollama on a Colab GPU. Ask anything.</p><div class="features"><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">lightbulb</span> Reasoning</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">code</span> Coding</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">science</span> Analysis</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">brush</span> Creative</div><div class="feat"><span class="material-symbols-rounded" style="font-size:16px">translate</span> Multilingual</div></div><p style="margin-top:16px;font-size:12px;color:var(--text2)">Made with ❤️ by <span style="color:var(--accent);font-weight:600">'+MADE_BY+'</span></p></div>';}
function newChat(){const id=uid();chats[id]={title:'New Chat',messages:[],ts:Date.now()};currentChatId=id;save();renderChatList();renderMessages();toggleSidebar()}
function loadChat(id){currentChatId=id;renderChatList();renderMessages();if(window.innerWidth<768)toggleSidebar()}
function clearChat(){if(!currentChatId)return;chats[currentChatId].messages=[];save();renderMessages()}

function processThinking(text){
  return text.replace(/<think>([\s\S]*?)<\/think>/g,(m,body)=>{
    return '<div class="think-block"><div class="think-header" onclick="let b=this.nextElementSibling;b.classList.toggle(\'open\');this.classList.toggle(\'open\')"><span class="arrow">▶</span> Thinking Process</div><div class="think-body">'+marked.parse(body.trim())+'</div></div>';
  });
}
function escapeHtml(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function renderMessages(){const el=document.getElementById('messages');el.innerHTML='';if(!currentChatId||!chats[currentChatId]||!chats[currentChatId].messages.length){el.innerHTML=getWelcomeHTML();return}const msgs=chats[currentChatId].messages;msgs.forEach(m=>{const d=document.createElement('div');d.className='msg '+m.role;const icon=m.role==='user'?'person':'psychology';let content=m.role==='assistant'?processThinking(marked.parse(m.content)):escapeHtml(m.content).replace(/\n/g,'<br>');d.innerHTML='<div class="msg-avatar"><span class="material-symbols-rounded" style="font-size:20px">'+icon+'</span></div><div class="msg-bubble">'+content+'</div>';el.appendChild(d)});el.scrollTop=el.scrollHeight}
function autoResize(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,150)+'px'}
function handleKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage()}}
function addTyping(){const el=document.getElementById('messages');const d=document.createElement('div');d.className='typing';d.id='typing';d.innerHTML='<div class="msg-avatar" style="background:var(--surface3)"><span class="material-symbols-rounded" style="font-size:20px;color:var(--accent)">psychology</span></div><div class="dots"><span></span><span></span><span></span></div>';el.appendChild(d);el.scrollTop=el.scrollHeight}
function removeTyping(){const t=document.getElementById('typing');if(t)t.remove()}
async function sendMessage(){const input=document.getElementById('userInput');const text=input.value.trim();if(!text||isGenerating)return;if(!currentChatId)newChat();isGenerating=true;document.getElementById('sendBtn').disabled=true;chats[currentChatId].messages.push({role:'user',content:text});if(chats[currentChatId].messages.length===1)chats[currentChatId].title=text.slice(0,40);chats[currentChatId].ts=Date.now();save();renderMessages();renderChatList();input.value='';autoResize(input);addTyping();try{const ollamaMsgs=chats[currentChatId].messages.map(m=>({role:m.role,content:m.content}));const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:ollamaMsgs,model:MODEL})});removeTyping();const reader=res.body.getReader();const dec=new TextDecoder();let full='';chats[currentChatId].messages.push({role:'assistant',content:''});const aidx=chats[currentChatId].messages.length-1;const msgEl=document.createElement('div');msgEl.className='msg assistant';msgEl.innerHTML='<div class="msg-avatar"><span class="material-symbols-rounded" style="font-size:20px">psychology</span></div><div class="msg-bubble"></div>';document.getElementById('messages').appendChild(msgEl);const bubble=msgEl.querySelector('.msg-bubble');while(true){const{done,value}=await reader.read();if(done)break;const chunk=dec.decode(value,{stream:true});for(const line of chunk.split(String.fromCharCode(10))){if(!line.trim())continue;try{const j=JSON.parse(line);if(j.error){full+='\n**Error:** '+j.error}else if(j.content){full+=j.content}}catch(e){}}chats[currentChatId].messages[aidx].content=full;bubble.innerHTML=processThinking(marked.parse(full));document.getElementById('messages').scrollTop=document.getElementById('messages').scrollHeight}save();renderChatList()}catch(e){removeTyping();console.error('Chat error:',e)}finally{isGenerating=false;document.getElementById('sendBtn').disabled=false}}
async function loadSysInfo(){try{const r=await fetch('/api/system');const d=await r.json();document.getElementById('sysStats').innerHTML='<div class="sys-stat"><span class="label"><span class="material-symbols-rounded" style="font-size:18px">smart_toy</span> Model</span><span class="value">'+(d.model||'N/A')+'</span></div><div class="sys-stat"><span class="label"><span class="material-symbols-rounded" style="font-size:18px">memory</span> GPU</span><span class="value">'+(d.gpu_name||'N/A')+'</span></div><div class="sys-stat"><span class="label"><span class="material-symbols-rounded" style="font-size:18px">developer_board</span> VRAM</span><span class="value">'+(d.gpu_vram_used||'?')+'/'+(d.gpu_vram_total||'?')+' GB</span></div><div class="sys-bar"><div class="sys-bar-fill" style="width:'+(d.gpu_vram_percent||0)+'%"></div></div><div class="sys-stat"><span class="label"><span class="material-symbols-rounded" style="font-size:18px">storage</span> RAM</span><span class="value">'+d.ram_used_gb+'/'+d.ram_total_gb+' GB</span></div><div class="sys-bar"><div class="sys-bar-fill" style="width:'+d.ram_percent+'%"></div></div><div class="sys-stat"><span class="label"><span class="material-symbols-rounded" style="font-size:18px">schedule</span> Uptime</span><span class="value">'+(d.uptime||'N/A')+'</span></div>'}catch(e){document.getElementById('sysStats').innerHTML='<p style="color:var(--danger)">Failed to load</p>'}}
if(!Object.keys(chats).length)newChat();else{const latest=Object.keys(chats).sort((a,b)=>chats[b].ts-chats[a].ts)[0];loadChat(latest)}
renderChatList();setInterval(()=>{if(document.getElementById('sysPanel').classList.contains('open'))loadSysInfo()},5000);
</script></body></html>"""

# ━━━ SECTION 7 — FLASK SERVER ━━━

def create_flask_app():
    from flask import Flask, request, Response, jsonify
    app = Flask(__name__)

    @app.route("/")
    def index(): return WEB_CHAT_HTML

    @app.route("/api/chat", methods=["POST"])
    def api_chat():
        import requests as req
        data = request.get_json(); messages = data.get("messages", []); model = data.get("model", MODEL_NAME)
        def generate():
            try:
                resp = req.post("http://localhost:11434/api/chat", json={"model":model,"messages":messages,"stream":True}, stream=True, timeout=None)
                if resp.status_code != 200:
                    try: err=resp.json().get("error",resp.text)
                    except: err=resp.text
                    yield json.dumps({"error":f"Ollama error ({resp.status_code}): {err}"})+chr(10); return
                for line in resp.iter_lines():
                    if not line: continue
                    try:
                        chunk=json.loads(line)
                        if chunk.get("error"): yield json.dumps({"error":chunk["error"]})+chr(10); return
                        msg=chunk.get("message",{}); content=msg.get("content","")
                        if content: yield json.dumps({"content":content})+chr(10)
                        if chunk.get("done"): break
                    except json.JSONDecodeError: continue
            except Exception as e: yield json.dumps({"error":str(e)})+chr(10)
        return Response(generate(), mimetype="text/plain", headers={"X-Accel-Buffering":"no","Cache-Control":"no-cache"})

    @app.route("/api/system")
    def api_system(): return jsonify(get_system_info())

    @app.route("/health")
    def health(): return jsonify({"status":"ok","model":MODEL_NAME,"made_by":MADE_BY})

    return app

def run_flask_server(port=7860):
    app = create_flask_app()
    t = threading.Thread(target=lambda: app.run(host="0.0.0.0",port=port,debug=False,use_reloader=False), daemon=True)
    t.start(); time.sleep(1); return t

# ━━━ SECTION 8 — CLI CHAT ━━━

def cli_chat(console):
    import requests as req
    from rich.markdown import Markdown; from rich.panel import Panel
    console.print(f"\n[bold cyan]╔══════════════════════════════════════╗[/]")
    console.print(f"[bold cyan]║  {MODEL_TITLE[:34].ljust(34)}  ║[/]")
    console.print(f"[bold cyan]║         Made by {MADE_BY[:20].ljust(20)}  ║[/]")
    console.print(f"[bold cyan]╚══════════════════════════════════════╝[/]\n")
    console.print("[dim]Commands: 'exit' to quit | 'clear' to reset | 'sys' for dashboard[/dim]\n")
    history = []
    while True:
        try: user_input = console.input("[bold green]You ▸ [/]")
        except (KeyboardInterrupt, EOFError): console.print(f"\n[bold cyan]👋 Goodbye! — Made by {MADE_BY}[/]"); break
        text = user_input.strip()
        if not text: continue
        if text.lower() in ("exit","quit","q"): console.print(f"[bold cyan]👋 Goodbye! — Made by {MADE_BY}[/]"); break
        if text.lower() == "clear": history.clear(); console.print("[bold yellow]🗑️  Chat history cleared.[/]\n"); continue
        if text.lower() == "sys": print_system_dashboard(console); continue
        history.append({"role":"user","content":text})
        try:
            resp = req.post("http://localhost:11434/api/chat", json={"model":MODEL_NAME,"messages":history,"stream":True}, stream=True, timeout=None)
            if resp.status_code != 200:
                try: err=resp.json().get("error",resp.text)
                except: err=resp.text
                console.print(f"[bold red]Ollama error ({resp.status_code}): {err}[/]\n"); continue
            full_response = ""; console.print()
            for line in resp.iter_lines():
                if not line: continue
                try:
                    chunk=json.loads(line)
                    if chunk.get("error"): console.print(f"[bold red]Ollama: {chunk['error']}[/]"); break
                    content=chunk.get("message",{}).get("content","")
                    if content: full_response+=content; print(content,end="",flush=True)
                    if chunk.get("done"): break
                except: continue
            print()
            clean = full_response
            think_match = re.search(r'<think>([\s\S]*?)</think>', clean)
            if think_match:
                think_text = think_match.group(1).strip()
                clean = re.sub(r'<think>[\s\S]*?</think>', '', clean).strip()
                console.print(Panel(
                    Markdown(think_text),
                    title="[bold cyan]💭 Thinking Process[/]",
                    border_style="dim cyan",
                    padding=(1, 2),
                ))
            console.print(Panel(
                Markdown(clean),
                title="[bold magenta]🧠 DeepSeek-R1 Abliterated[/]",
                border_style="bright_blue",
                padding=(1, 2),
            ))
            history.append({"role":"assistant","content":full_response}); console.print()
        except Exception as e: console.print(f"[bold red]Error: {e}[/]\n")

# ━━━ SECTION 9 — MAIN ━━━

def main():
    global START_TIME; START_TIME = time.time()
    install_dependencies()
    from rich.console import Console; from rich.panel import Panel
    console = Console()
    install_ollama(console); ollama_proc = start_ollama_server(console)
    pull_model(console); print_system_dashboard(console)
    WEB_PORT = 7860
    console.print(f"\n[bold cyan]⏳ Starting web server on port {WEB_PORT}…[/]")
    run_flask_server(port=WEB_PORT)
    console.print(f"[bold green]✔ Web server running at http://localhost:{WEB_PORT}[/]")
    cf_proc, public_url = start_cloudflare_tunnel(console, port=WEB_PORT)
    console.print(Panel(
        f"[bold green]✔ Everything is ready![/]\n\n"
        f"  🌐 [bold]Public URL:[/] [link={public_url or '#'}]{public_url or 'N/A'}[/link]\n"
        f"  🏠 [bold]Local URL:[/]  http://localhost:{WEB_PORT}\n"
        f"  🤖 [bold]Model:[/]      {MODEL_NAME}\n"
        f"  📊 [bold]Health:[/]     http://localhost:{WEB_PORT}/health\n\n"
        f"  [bold magenta]Made with ❤️  by {MADE_BY}[/bold magenta]",
        title=f"[bold cyan]🚀 {MODEL_TITLE} — Ready![/]", border_style="bright_green", padding=(1, 3)))
    console.print("\n[bold yellow]💬 Starting CLI Chat Mode…[/]")
    console.print("[dim]You can also use the Web UI via the public URL above.[/dim]\n")
    try: cli_chat(console)
    except KeyboardInterrupt: console.print(f"\n[bold cyan]👋 Shutting down… — Made by {MADE_BY}[/]")
    finally:
        try: os.killpg(os.getpgid(ollama_proc.pid), signal.SIGTERM)
        except: pass
        try:
            if cf_proc: os.killpg(os.getpgid(cf_proc.pid), signal.SIGTERM)
        except: pass

if __name__ == "__main__":
    main()
