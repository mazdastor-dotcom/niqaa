# -*- coding: utf-8 -*-
import ctypes
import csv
import hashlib
import html
import json
import random
import re
import math
import os
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
import winreg
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

try:
    import win32api
    import win32con
    import win32gui
except ImportError:
    win32api = None
    win32con = None
    win32gui = None


APP_NAME = "نقاء"
APP_SUBTITLE = "تنظيف واضح وذكي: إزالة البرامج، تنظيف المخلفات، مراقبة التشغيل، وفحص الأمان المحلي."
APP_REPORT_NAME = "نقاء"
CONTACT_HANDLE = "@iML7x"
CONTACT_URL = "https://x.com/iML7x"
DEVELOPER_NAME = "ماجد السعدي"
COPYRIGHT_TEXT = "جميع الحقوق محفوظة"
QUARANTINE_DIR = Path.home() / "Desktop" / "Niqaa_Backups"
LOG_DIR = Path.home() / "Desktop" / "Niqaa_Reports"
DATA_DIR = Path.home() / "Desktop" / "Niqaa_Data"
HASH_DB_PATH = DATA_DIR / "hash_database.json"
SETTINGS_PATH = DATA_DIR / "settings.json"
SNAPSHOT_PATH = DATA_DIR / "system_snapshot.json"
DISABLED_STARTUP_PATH = DATA_DIR / "disabled_startup.json"
DISABLED_STARTUP_DIR = DATA_DIR / "DisabledStartupItems"
CACHE_MAX_AGE_SECONDS = 24 * 60 * 60
MANIFEST_NAME = "restore_manifest.json"
DHIKR_NOTIFIER_ARG = "--dhikr-notifier"
DHIKR_NOTIFIER_STOP_PATH = DATA_DIR / "dhikr_notifier.stop"
DEFAULT_DHIKR_INTERVAL_MINUTES = 5
ADHKAR = [
    "سبحان الله وبحمده، سبحان الله العظيم",
    "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد",
    "اللهم صل وسلم على نبينا محمد",
    "أستغفر الله العظيم وأتوب إليه",
    "لا حول ولا قوة إلا بالله",
    "حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم",
    "سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر",
]
DHIKR_NOTIFICATIONS = [
    "سبحان الله وبحمده، سبحان الله العظيم",
    "أستغفر الله العظيم وأتوب إليه",
    "اللهم صل وسلم على نبينا محمد",
    "لا حول ولا قوة إلا بالله",
    "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير",
    "حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم",
    "اللهم آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار",
    "اللهم إنك عفو تحب العفو فاعف عني",
    "رب اغفر لي وتب علي إنك أنت التواب الرحيم",
    "اللهم إني أسألك الهدى والتقى والعفاف والغنى",
    "اللهم أعني على ذكرك وشكرك وحسن عبادتك",
    "اللهم إني أعوذ بك من الهم والحزن، والعجز والكسل",
    "ربنا لا تزغ قلوبنا بعد إذ هديتنا وهب لنا من لدنك رحمة",
    "اللهم اجعل القرآن ربيع قلبي ونور صدري وجلاء حزني",
    "يا حي يا قيوم برحمتك أستغيث، أصلح لي شأني كله",
    "اللهم بارك لي في وقتي وعملي ورزقي",
    "اللهم ارزقني قلبًا سليمًا ولسانًا ذاكرًا",
    "رب اشرح لي صدري ويسر لي أمري",
    "اللهم إني أسألك علماً نافعاً ورزقاً طيباً وعملاً متقبلاً",
    "اللهم اكفني بحلالك عن حرامك وأغنني بفضلك عمن سواك",
    "سبحان الله، والحمد لله، ولا إله إلا الله، والله أكبر",
    "اللهم اجعل هذا اليوم خيرًا وبركة وتوفيقًا",
    "اللهم إني أسألك من الخير كله عاجله وآجله",
    "ربنا ظلمنا أنفسنا وإن لم تغفر لنا وترحمنا لنكونن من الخاسرين",
    "اللهم ثبت قلبي على دينك",
    "اللهم إني أعوذ بك من شر ما عملت ومن شر ما لم أعمل",
    "اللهم اغفر للمؤمنين والمؤمنات والمسلمين والمسلمات",
    "اللهم اجعلني من الذاكرين الشاكرين",
    "اللهم إني أسألك حسن الخاتمة",
    "اللهم ارزقني طمأنينة القلب وصفاء النية",
]
EXECUTABLE_EXTENSIONS = {".exe", ".dll", ".sys", ".scr", ".com", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".msi"}
SUSPICIOUS_IMPORTS = [
    b"CreateRemoteThread",
    b"VirtualAllocEx",
    b"WriteProcessMemory",
    b"URLDownloadToFile",
    b"WinHttpOpen",
    b"InternetOpen",
    b"RegSetValue",
    b"ShellExecute",
    b"PowerShell",
]
SUSPICIOUS_SCRIPT_PATTERNS = [
    r"frombase64string",
    r"encodedcommand",
    r"downloadstring",
    r"invoke-webrequest",
    r"start-process",
    r"hidden",
    r"bypass",
    r"reg\s+add",
    r"schtasks\s+/create",
]
TEXT = {
    "ar": {
        "remove": "إزالة كاملة",
        "leftovers": "فحص البقايا",
        "security": "فحص أمان",
        "cache": "تنظيف الكاش",
        "device_cache": "تنظيف كاش الجهاز",
        "install_watch": "مراقبة تثبيت",
        "connections": "الاتصالات",
        "startup": "قناص بدء التشغيل",
        "folder_scan": "فحص مجلد",
        "health": "تقرير صحة",
        "behavior": "مراقبة سلوك",
        "hash": "بصمات Hash",
        "quarantine": "العزل",
        "forensics": "Forensics",
        "smart_scan": "الفحص الذكي",
        "updates": "تحديث التطبيقات",
        "dns": "DNS Watch",
        "guardian": "الحارس",
        "snapshot": "Snapshot",
        "allow_block": "السماح/الحظر",
        "settings_io": "استيراد/تصدير",
        "advanced_clean": "تنظيف متقدم",
        "dhikr_alerts": "تنبيهات الأذكار",
        "dhikr_interval": "فاصل الأذكار",
        "dhikr_background": "أذكار بالخلفية",
        "stop_dhikr_background": "إيقاف الخلفية",
        "disable_startup": "تعطيل بدء مشبوه",
        "restore_startup": "استرجاع بدء التشغيل",
        "refresh": "تحديث",
        "restore": "استرجاع آخر عزل",
        "search": "بحث في البرامج",
        "sort": "ترتيب حسب",
        "programs": "البرامج المثبتة",
        "details": "تفاصيل البرنامج المحدد",
        "leftovers_title": "المخلفات المقترحة",
        "language": "English",
    },
    "en": {
        "remove": "Full Remove",
        "leftovers": "Scan Leftovers",
        "security": "Security Scan",
        "cache": "Clean Cache",
        "device_cache": "Device Cache",
        "install_watch": "Install Watch",
        "connections": "Connections",
        "startup": "Startup Hunter",
        "folder_scan": "Folder Scan",
        "health": "Health Report",
        "behavior": "Behavior Monitor",
        "hash": "Hash Baseline",
        "quarantine": "Quarantine",
        "forensics": "Forensics",
        "smart_scan": "Smart Scan",
        "updates": "App Updates",
        "dns": "DNS Watch",
        "guardian": "Guardian",
        "snapshot": "Snapshot",
        "allow_block": "Allow/Block",
        "settings_io": "Import/Export",
        "advanced_clean": "Advanced Clean",
        "dhikr_alerts": "Dhikr Alerts",
        "dhikr_interval": "Dhikr Interval",
        "dhikr_background": "Background Dhikr",
        "stop_dhikr_background": "Stop Background",
        "disable_startup": "Disable Risky Startup",
        "restore_startup": "Restore Startup",
        "refresh": "Refresh",
        "restore": "Restore Last Quarantine",
        "search": "Search programs",
        "sort": "Sort by",
        "programs": "Installed Programs",
        "details": "Selected Program Details",
        "leftovers_title": "Suggested Leftovers",
        "language": "العربية",
    },
}


@dataclass(frozen=True)
class Program:
    name: str
    publisher: str
    version: str
    estimated_size_kb: int
    install_date: str
    install_location: str
    uninstall_string: str
    quiet_uninstall_string: str
    registry_key: str


@dataclass(frozen=True)
class LeftoverItem:
    path: Path
    size: int
    confidence: str
    reason: str


@dataclass(frozen=True)
class CacheItem:
    path: Path
    size: int
    category: str


@dataclass(frozen=True)
class SecurityFinding:
    path: Path
    score: int
    level: str
    reasons: list[str]


@dataclass(frozen=True)
class ConnectionItem:
    protocol: str
    local: str
    remote: str
    state: str
    pid: str
    process: str


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    returncode: int

    def text(self) -> str:
        parts = []
        if self.stdout.strip():
            parts.append(self.stdout.strip())
        if self.stderr.strip():
            parts.append("STDERR:\n" + self.stderr.strip())
        parts.append(f"Exit code: {self.returncode}")
        return "\n\n".join(parts)


@dataclass(frozen=True)
class OperationReport:
    program_name: str
    uninstall_code: int
    leftovers_found: int
    leftovers_quarantined: int
    cache_deleted: int
    cache_bytes: int
    log_path: Path
    quarantine_paths: list[str]


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False


def relaunch_as_admin() -> None:
    params = " ".join(f'"{arg}"' for arg in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)


def normalize_token(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\u0600-\u06FF]+", " ", value.lower())
    stop_words = {
        "inc",
        "llc",
        "ltd",
        "limited",
        "corporation",
        "corp",
        "company",
        "co",
        "microsoft",
    }
    return " ".join(part for part in cleaned.split() if len(part) >= 3 and part not in stop_words)


def safe_filename(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]+', "_", value).strip()
    return cleaned[:90] or "program"


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.tmp")
    temp_path.write_text(text, encoding=encoding)
    os.replace(temp_path, path)


def atomic_write_json(path: Path, data: object) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_app_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)


def show_dhikr_toast(parent: tk.Misc, message: str) -> tk.Toplevel:
    toast = tk.Toplevel(parent)
    toast.overrideredirect(True)
    toast.configure(bg="#172033")
    toast.attributes("-topmost", True)
    try:
        toast.attributes("-alpha", 0.0)
    except tk.TclError:
        pass

    width = 390
    frame = tk.Frame(toast, bg="#172033", highlightbackground="#818CF8", highlightthickness=1)
    frame.pack(fill=tk.BOTH, expand=True)

    header = tk.Frame(frame, bg="#312E81")
    header.pack(fill=tk.X)
    tk.Label(
        header,
        text="نقاء | تذكير",
        bg="#312E81",
        fg="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        anchor="e",
        padx=10,
        pady=6,
    ).pack(side=tk.RIGHT, fill=tk.X, expand=True)
    tk.Button(
        header,
        text="×",
        command=toast.destroy,
        bg="#312E81",
        fg="#FFFFFF",
        activebackground="#4338CA",
        activeforeground="#FFFFFF",
        relief=tk.FLAT,
        cursor="hand2",
        width=3,
    ).pack(side=tk.LEFT)

    tk.Label(
        frame,
        text=message,
        bg="#172033",
        fg="#F9FAFB",
        font=("Segoe UI", 11, "bold"),
        justify=tk.RIGHT,
        wraplength=width - 34,
        padx=14,
        pady=14,
    ).pack(fill=tk.BOTH, expand=True)

    toast.update_idletasks()
    height = max(124, toast.winfo_reqheight())
    x = max(16, toast.winfo_screenwidth() - width - 24)
    y = max(16, toast.winfo_screenheight() - height - 74)
    toast.geometry(f"{width}x{height}+{x}+{y}")

    def fade(alpha: float, step: float) -> None:
        if not toast.winfo_exists():
            return
        next_alpha = alpha + step
        if step > 0 and next_alpha >= 0.96:
            try:
                toast.attributes("-alpha", 0.96)
            except tk.TclError:
                pass
            toast.after(10500, lambda: fade(0.96, -0.08))
            return
        if step < 0 and next_alpha <= 0:
            toast.destroy()
            return
        try:
            toast.attributes("-alpha", next_alpha)
        except tk.TclError:
            pass
        toast.after(18, lambda: fade(next_alpha, step))

    fade(0.0, 0.08)
    return toast


def path_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def path_has_reparse_point(path: Path) -> bool:
    try:
        return path.is_symlink()
    except OSError:
        return True


def read_reg_value(key: winreg.HKEYType, name: str) -> str:
    try:
        value, _ = winreg.QueryValueEx(key, name)
        return str(value).strip()
    except OSError:
        return ""


def read_reg_int(key: winreg.HKEYType, name: str) -> int:
    try:
        value, _ = winreg.QueryValueEx(key, name)
        return int(value)
    except (OSError, TypeError, ValueError):
        return 0


def registry_uninstall_roots() -> list[tuple[int, str]]:
    return [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]


def load_programs() -> list[Program]:
    programs: list[Program] = []
    seen: set[tuple[str, str]] = set()

    for root, path in registry_uninstall_roots():
        try:
            with winreg.OpenKey(root, path) as parent:
                count, _, _ = winreg.QueryInfoKey(parent)
                for index in range(count):
                    try:
                        subkey_name = winreg.EnumKey(parent, index)
                        full_key = f"{path}\\{subkey_name}"
                        with winreg.OpenKey(parent, subkey_name) as child:
                            name = read_reg_value(child, "DisplayName")
                            uninstall = read_reg_value(child, "UninstallString")
                            system_component = read_reg_value(child, "SystemComponent")
                            release_type = read_reg_value(child, "ReleaseType")
                            parent_name = read_reg_value(child, "ParentDisplayName")

                            if not name or not uninstall:
                                continue
                            if system_component == "1" or release_type or parent_name:
                                continue

                            program = Program(
                                name=name,
                                publisher=read_reg_value(child, "Publisher"),
                                version=read_reg_value(child, "DisplayVersion"),
                                estimated_size_kb=read_reg_int(child, "EstimatedSize"),
                                install_date=read_reg_value(child, "InstallDate"),
                                install_location=read_reg_value(child, "InstallLocation"),
                                uninstall_string=uninstall,
                                quiet_uninstall_string=read_reg_value(child, "QuietUninstallString"),
                                registry_key=full_key,
                            )
                            signature = (program.name.lower(), program.uninstall_string.lower())
                            if signature not in seen:
                                seen.add(signature)
                                programs.append(program)
                    except OSError:
                        continue
        except OSError:
            continue

    return sorted(programs, key=lambda item: item.name.lower())


def command_for_display(command: str) -> str:
    return command.replace("MsiExec.exe", "msiexec.exe").replace("MsiExec", "msiexec")


def uninstall_command(program: Program) -> str:
    command = program.quiet_uninstall_string or program.uninstall_string
    lowered = command.lower()
    if "msiexec" in lowered and " /i" in lowered:
        command = re.sub(r"\s/I\s", " /X ", command, flags=re.IGNORECASE)
    return command_for_display(command)


def run_uninstall(program: Program) -> int:
    command = uninstall_command(program)
    completed = subprocess.run(["cmd.exe", "/c", command], check=False)
    return int(completed.returncode)


def launch_and_wait(path: str) -> CommandResult:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".msi":
            completed = subprocess.run(["msiexec.exe", "/i", str(file_path)], capture_output=True, text=True, encoding="utf-8", errors="ignore", check=False)
        elif suffix in {".bat", ".cmd"}:
            completed = subprocess.run(["cmd.exe", "/c", str(file_path)], capture_output=True, text=True, encoding="utf-8", errors="ignore", check=False)
        else:
            completed = subprocess.run([str(file_path)], capture_output=True, text=True, encoding="utf-8", errors="ignore", check=False)
        return CommandResult(completed.stdout, completed.stderr, int(completed.returncode))
    except OSError as exc:
        return CommandResult("", str(exc), 1)


def candidate_roots() -> list[Path]:
    env_names = [
        "ProgramFiles",
        "ProgramFiles(x86)",
        "ProgramData",
        "LOCALAPPDATA",
        "APPDATA",
    ]
    roots: list[Path] = []
    for env_name in env_names:
        value = os.environ.get(env_name)
        if value:
            path = Path(value)
            if path.exists() and path not in roots:
                roots.append(path)
    return roots


def cache_roots() -> list[Path]:
    roots: list[Path] = []
    for env_name in ["TEMP", "TMP"]:
        value = os.environ.get(env_name)
        if value:
            path = Path(value)
            if path.exists() and path not in roots:
                roots.append(path)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        temp_path = Path(local_app_data) / "Temp"
        if temp_path.exists() and temp_path not in roots:
            roots.append(temp_path)

    windows_temp = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp"
    if is_admin() and windows_temp.exists() and windows_temp not in roots:
        roots.append(windows_temp)

    return roots


def device_cache_targets() -> list[tuple[Path, str]]:
    targets: list[tuple[Path, str]] = []
    known: list[tuple[Path, str]] = []

    for env_name in ["TEMP", "TMP"]:
        env_value = os.environ.get(env_name)
        if env_value:
            known.append((Path(env_value), "Temp المستخدم"))

    local_app_data_value = os.environ.get("LOCALAPPDATA")
    if local_app_data_value:
        local_app_data = Path(local_app_data_value)
        known.extend(
            [
                (local_app_data / "Temp", "Temp المحلي"),
                (local_app_data / "Microsoft" / "Windows" / "INetCache", "كاش Windows/Internet"),
                (local_app_data / "Microsoft" / "Windows" / "Explorer", "كاش Explorer"),
                (local_app_data / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache", "كاش Edge"),
                (local_app_data / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache", "كاش Edge"),
                (local_app_data / "Microsoft" / "Edge" / "User Data" / "Default" / "GPUCache", "كاش Edge"),
                (local_app_data / "Microsoft" / "Edge" / "User Data" / "Default" / "Service Worker" / "CacheStorage", "كاش Edge"),
                (local_app_data / "Google" / "Chrome" / "User Data" / "Default" / "Cache", "كاش Chrome"),
                (local_app_data / "Google" / "Chrome" / "User Data" / "Default" / "Code Cache", "كاش Chrome"),
                (local_app_data / "Google" / "Chrome" / "User Data" / "Default" / "GPUCache", "كاش Chrome"),
                (local_app_data / "Google" / "Chrome" / "User Data" / "Default" / "Service Worker" / "CacheStorage", "كاش Chrome"),
                (local_app_data / "Packages", "كاش تطبيقات Microsoft Store"),
            ]
        )

    app_data_value = os.environ.get("APPDATA")
    if app_data_value:
        known.append((Path(app_data_value) / "Mozilla" / "Firefox" / "Profiles", "كاش Firefox"))

    if is_admin():
        known.append((Path(os.environ.get("SystemRoot", r"C:\Windows")) / "Temp", "Temp النظام"))

    seen: set[str] = set()
    for path, category in known:
        if not str(path) or not path.exists():
            continue
        key = str(path.resolve()).lower()
        if key not in seen:
            seen.add(key)
            targets.append((path, category))
    return targets


def privacy_targets() -> list[tuple[Path, str]]:
    app_data = Path(os.environ.get("APPDATA", ""))
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    targets = [
        (app_data / "Microsoft" / "Windows" / "Recent", "Recent Files"),
        (app_data / "Microsoft" / "Windows" / "Recent" / "AutomaticDestinations", "Jump Lists"),
        (app_data / "Microsoft" / "Windows" / "Recent" / "CustomDestinations", "Jump Lists"),
        (local_app_data / "Microsoft" / "Windows" / "Explorer", "Thumbnail Cache"),
    ]
    return [(path, category) for path, category in targets if path.exists()]


def scan_privacy_items() -> list[CacheItem]:
    items: list[CacheItem] = []
    for root, category in privacy_targets():
        try:
            for child in root.iterdir():
                if child.is_file() or child.is_dir():
                    size = folder_size(child)
                    if size > 0:
                        items.append(CacheItem(child, size, category))
        except OSError:
            continue
    return sorted(items, key=lambda item: item.size, reverse=True)


def clean_privacy_items(items: list[CacheItem]) -> tuple[int, int]:
    deleted_count = 0
    deleted_bytes = 0
    allowed_roots = [root.resolve() for root, _ in privacy_targets()]
    for item in items:
        try:
            resolved = item.path.resolve()
        except OSError:
            continue
        if not any(path_within(resolved, root) for root in allowed_roots):
            continue
        if delete_path(item.path):
            deleted_count += 1
            deleted_bytes += item.size
    return deleted_count, deleted_bytes


def empty_recycle_bin() -> bool:
    try:
        flags = 0x00000001 | 0x00000002 | 0x00000004
        return ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags) == 0
    except OSError:
        return False


def device_cache_path_is_safe(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    if path_has_reparse_point(path):
        return False
    return any(path_within(resolved, root) for root, _ in device_cache_targets())


def device_or_cache_path_is_safe(path: Path) -> bool:
    return device_cache_path_is_safe(path) or cache_path_is_safe(path)


def scan_device_cache() -> list[CacheItem]:
    items: list[CacheItem] = []
    for root, category in device_cache_targets():
        if root.name.lower() == "profiles":
            try:
                for profile in root.iterdir():
                    for child_name in ["cache2", "startupCache"]:
                        cache_path = profile / child_name
                        if cache_path.exists() and device_cache_path_is_safe(cache_path):
                            items.append(CacheItem(cache_path, folder_size(cache_path), "كاش Firefox"))
            except OSError:
                continue
            continue

        if root.name.lower() == "packages":
            try:
                for package in root.iterdir():
                    for child_name in ["AC\\Temp", "LocalCache", "TempState"]:
                        cache_path = package / child_name
                        if cache_path.exists() and device_cache_path_is_safe(cache_path):
                            size = folder_size(cache_path)
                            if size > 0:
                                items.append(CacheItem(cache_path, size, category))
            except OSError:
                continue
            continue

        try:
            children = list(root.iterdir())
        except OSError:
            continue
        for child in children:
            if device_cache_path_is_safe(child):
                size = folder_size(child)
                if size > 0:
                    items.append(CacheItem(child, size, category))

    return sorted(items, key=lambda item: item.size, reverse=True)


def clean_device_cache(items: list[CacheItem]) -> tuple[int, int]:
    deleted_count = 0
    deleted_bytes = 0
    for item in items:
        if not device_cache_path_is_safe(item.path):
            continue
        if delete_path(item.path):
            deleted_count += 1
            deleted_bytes += item.size
    return deleted_count, deleted_bytes


def path_is_safe(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    if path_has_reparse_point(path):
        return False

    protected_names = {
        "windows",
        "program files",
        "program files (x86)",
        "programdata",
        "users",
        "appdata",
        "local",
        "roaming",
    }
    if resolved.name.lower() in protected_names:
        return False
    return any(path_within(resolved, root) for root in candidate_roots())


def cache_path_is_safe(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    if path_has_reparse_point(path):
        return False
    return any(path_within(resolved, root) for root in cache_roots())


def classify_leftover(path: Path, program: Program) -> tuple[str, str]:
    install_location = Path(program.install_location) if program.install_location else None
    if install_location and path == install_location:
        return "عالية", "مسار التثبيت الرسمي"
    app_data = os.environ.get("APPDATA")
    local_app_data = os.environ.get("LOCALAPPDATA")
    if app_data and str(path).lower().startswith(str(Path(app_data)).lower()):
        return "متوسطة", "مجلد بيانات مستخدم"
    if local_app_data and str(path).lower().startswith(str(Path(local_app_data)).lower()):
        return "متوسطة", "مجلد بيانات محلية"
    return "متوسطة", "اسم المجلد مطابق لاسم البرنامج أو الناشر"


def find_leftover_paths(program: Program) -> list[Path]:
    tokens = [normalize_token(program.name)]
    if program.publisher:
        tokens.append(normalize_token(program.publisher))
    token_parts = {part for token in tokens for part in token.split() if len(part) >= 3}

    results: set[Path] = set()
    if program.install_location:
        install_path = Path(program.install_location)
        if install_path.exists() and path_is_safe(install_path):
            results.add(install_path)

    if not token_parts:
        return sorted(results, key=lambda item: str(item).lower())

    for root in candidate_roots():
        try:
            for child in root.iterdir():
                haystack = normalize_token(child.name)
                if any(token in haystack for token in token_parts) and path_is_safe(child):
                    results.add(child)
        except OSError:
            continue

    return sorted(results, key=lambda item: str(item).lower())


def find_leftovers(program: Program) -> list[LeftoverItem]:
    items: list[LeftoverItem] = []
    for path in find_leftover_paths(program):
        confidence, reason = classify_leftover(path, program)
        items.append(LeftoverItem(path=path, size=folder_size(path), confidence=confidence, reason=reason))
    return items


def find_program_cache(program: Program) -> list[Path]:
    token_parts = {
        part
        for token in [normalize_token(program.name), normalize_token(program.publisher)]
        for part in token.split()
        if len(part) >= 3
    }
    if not token_parts:
        return []

    results: set[Path] = set()
    for root in cache_roots():
        try:
            for child in root.iterdir():
                haystack = normalize_token(child.name)
                if any(token in haystack for token in token_parts) and cache_path_is_safe(child):
                    results.add(child)
        except OSError:
            continue
    return sorted(results, key=lambda item: str(item).lower())


def delete_path(path: Path) -> bool:
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return True
    except OSError:
        return False


def clean_temp_cache(max_age_seconds: int = CACHE_MAX_AGE_SECONDS) -> tuple[int, int]:
    now = time.time()
    deleted_count = 0
    deleted_bytes = 0

    for root in cache_roots():
        try:
            children = list(root.iterdir())
        except OSError:
            continue

        for child in children:
            if not cache_path_is_safe(child):
                continue
            try:
                modified_at = child.stat().st_mtime
            except OSError:
                continue
            if now - modified_at < max_age_seconds:
                continue

            size = folder_size(child)
            if delete_path(child):
                deleted_count += 1
                deleted_bytes += size

    return deleted_count, deleted_bytes


def clean_program_cache(program: Program) -> tuple[int, int]:
    deleted_count = 0
    deleted_bytes = 0
    for path in find_program_cache(program):
        if not cache_path_is_safe(path):
            continue
        size = folder_size(path)
        if delete_path(path):
            deleted_count += 1
            deleted_bytes += size
    return deleted_count, deleted_bytes


def folder_size(path: Path) -> int:
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0

    total = 0
    for root, _, files in os.walk(path):
        for file_name in files:
            try:
                total += (Path(root) / file_name).stat().st_size
            except OSError:
                continue
    return total


def format_size(bytes_count: int) -> str:
    size = float(bytes_count)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{bytes_count} B"


def program_size_bytes(program: Program) -> int:
    if program.estimated_size_kb > 0:
        return program.estimated_size_kb * 1024
    return 0


def format_program_size(program: Program) -> str:
    size = program_size_bytes(program)
    return format_size(size) if size > 0 else "غير معروف"


def install_date_key(program: Program) -> str:
    value = program.install_date.strip()
    if re.fullmatch(r"\d{8}", value):
        return value
    return ""


def format_install_date(program: Program) -> str:
    value = install_date_key(program)
    if not value:
        return "غير معروف"
    return f"{value[6:8]}-{value[4:6]}-{value[0:4]}"


def file_entropy(path: Path, sample_limit: int = 1024 * 1024) -> float:
    try:
        data = path.read_bytes()[:sample_limit]
    except OSError:
        return 0.0
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    entropy = 0.0
    length = len(data)
    for count in counts:
        if count:
            probability = count / length
            entropy -= probability * math.log2(probability)
    return entropy


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return ""
    return digest.hexdigest()


def load_hash_db() -> dict[str, dict[str, str]]:
    if not HASH_DB_PATH.exists():
        return {}
    try:
        data = json.loads(HASH_DB_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return {str(key): dict(value) for key, value in data.items() if isinstance(value, dict)}
    except (OSError, json.JSONDecodeError):
        return {}
    return {}


def save_hash_db(data: dict[str, dict[str, str]]) -> None:
    atomic_write_json(HASH_DB_PATH, data)


def default_settings() -> dict[str, list[str]]:
    return {"allow_publishers": [], "allow_paths": [], "block_hashes": [], "block_paths": [], "block_domains": []}


def load_settings() -> dict[str, list[str]]:
    if not SETTINGS_PATH.exists():
        return default_settings()
    try:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_settings()
    settings = default_settings()
    for key in settings:
        value = data.get(key, [])
        if isinstance(value, list):
            settings[key] = [str(item) for item in value]
    return settings


def save_settings(settings: dict[str, list[str]]) -> None:
    atomic_write_json(SETTINGS_PATH, settings)


def write_html_report(title: str, content: str) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = LOG_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}_{safe_filename(title)}.html"
    body = html.escape(content)
    document = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>
body{{margin:0;background:#0f172a;color:#e5e7eb;font-family:Segoe UI,Tahoma,Arial,sans-serif;line-height:1.65}}
main{{max-width:1180px;margin:24px auto;padding:24px;background:#111827;border:1px solid #334155;border-radius:10px}}
h1{{margin:0 0 16px;color:#fff;font-size:24px}}
pre{{white-space:pre-wrap;background:#020617;border:1px solid #334155;border-radius:8px;padding:18px;direction:rtl;text-align:right}}
.brand{{color:#a5b4fc;font-weight:700;margin-bottom:8px}}
</style>
</head>
<body><main><div class="brand">{html.escape(APP_REPORT_NAME)} | X {html.escape(CONTACT_HANDLE)} | المطور: {html.escape(DEVELOPER_NAME)} | {html.escape(COPYRIGHT_TEXT)}</div><h1>{html.escape(title)}</h1><pre>{body}</pre></main></body></html>"""
    atomic_write_text(path, document, encoding="utf-8")
    return path


def program_hashes(program: Program) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in iter_program_files(program, limit=260):
        digest = sha256_file(path)
        if digest:
            hashes[str(path)] = digest
    return hashes


def compare_program_hashes(program: Program) -> tuple[dict[str, str], list[str]]:
    key = f"{program.name}|{program.publisher}|{program.install_location}"
    db = load_hash_db()
    current = program_hashes(program)
    previous = db.get(key, {})
    changes: list[str] = []
    for path, digest in current.items():
        if path not in previous:
            changes.append(f"جديد: {path}")
        elif previous[path] != digest:
            changes.append(f"تغيرت البصمة: {path}")
    for path in previous:
        if path not in current:
            changes.append(f"اختفى: {path}")
    db[key] = current
    save_hash_db(db)
    return current, changes


def iter_program_files(program: Program, limit: int = 180) -> list[Path]:
    roots: list[Path] = []
    if program.install_location:
        root = Path(program.install_location)
        if root.exists() and root.is_dir():
            roots.append(root)
    files: list[Path] = []
    for root in roots:
        for current_root, _, file_names in os.walk(root):
            for file_name in file_names:
                path = Path(current_root) / file_name
                if path.suffix.lower() in EXECUTABLE_EXTENSIONS:
                    files.append(path)
                    if len(files) >= limit:
                        return files
    return files


def script_risk_reasons(path: Path) -> list[str]:
    if path.suffix.lower() not in {".bat", ".cmd", ".ps1", ".vbs", ".js"}:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return []
    reasons: list[str] = []
    for pattern in SUSPICIOUS_SCRIPT_PATTERNS:
        if re.search(pattern, text):
            reasons.append(f"نمط سكربت مشبوه: {pattern}")
    if len(re.findall(r"[A-Za-z0-9+/]{80,}={0,2}", text)) >= 2:
        reasons.append("وجود سلاسل طويلة قد تكون Base64 أو Obfuscation")
    return reasons


def binary_risk_reasons(path: Path) -> list[str]:
    reasons: list[str] = []
    suffix = path.suffix.lower()
    if suffix not in {".exe", ".dll", ".sys", ".scr", ".com"}:
        return reasons
    entropy = file_entropy(path)
    if entropy >= 7.25:
        reasons.append(f"Entropy عالي ({entropy:.2f}) قد يدل على ضغط/تشفير")
    try:
        sample = path.read_bytes()[:2 * 1024 * 1024]
    except OSError:
        return reasons
    matched = [token.decode("ascii", "ignore") for token in SUSPICIOUS_IMPORTS if token.lower() in sample.lower()]
    if matched:
        reasons.append("Imports/Strings حساسة: " + ", ".join(sorted(set(matched))[:6]))
    if suffix == ".scr":
        reasons.append("ملف شاشة توقف قابل للتنفيذ")
    return reasons


def path_risk_reasons(path: Path) -> list[str]:
    lowered = str(path).lower()
    reasons: list[str] = []
    suspicious_dirs = ["\\temp\\", "\\appdata\\local\\temp\\", "\\public\\", "\\downloads\\"]
    if any(item in lowered for item in suspicious_dirs):
        reasons.append("مسار تشغيل قابل للاستغلال أو مؤقت")
    suspicious_names = ["update", "service", "host", "svchost", "runtime", "helper"]
    if any(name in path.stem.lower() for name in suspicious_names):
        reasons.append("اسم عام قد يستخدم للتمويه")
    return reasons


def level_for_score(score: int) -> str:
    if score >= 75:
        return "خطر"
    if score >= 45:
        return "مشبوه"
    if score >= 20:
        return "مراجعة"
    return "منخفض"


def scan_program_security(program: Program) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for path in iter_program_files(program):
        reasons = path_risk_reasons(path)
        reasons.extend(binary_risk_reasons(path))
        reasons.extend(script_risk_reasons(path))
        score = min(100, 8 + len(reasons) * 18)
        if reasons:
            findings.append(SecurityFinding(path=path, score=score, level=level_for_score(score), reasons=reasons))
    return sorted(findings, key=lambda item: item.score, reverse=True)


def startup_registry_locations() -> list[tuple[int, str]]:
    return [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]


def scan_persistence(program: Program) -> list[SecurityFinding]:
    token_parts = set(normalize_token(f"{program.name} {program.publisher}").split())
    install_path = program.install_location.lower()
    findings: list[SecurityFinding] = []
    for root, path in startup_registry_locations():
        try:
            with winreg.OpenKey(root, path) as key:
                count, _, _ = winreg.QueryInfoKey(key)
                for index in range(count):
                    name, value, _ = winreg.EnumValue(key, index)
                    text = f"{name} {value}".lower()
                    if install_path and install_path in text:
                        findings.append(SecurityFinding(Path(path), 55, "مشبوه", [f"تشغيل تلقائي مرتبط بالبرنامج: {name}"]))
                    elif token_parts and any(token in normalize_token(text).split() for token in token_parts):
                        findings.append(SecurityFinding(Path(path), 35, "مراجعة", [f"تشغيل تلقائي قد يكون مرتبطًا: {name}"]))
        except OSError:
            continue
    return findings


def run_text_command(command: list[str]) -> str:
    result = run_command(command)
    return result.stdout if result.stdout.strip() else result.stderr


def run_command(command: list[str]) -> CommandResult:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore", check=False)
        return CommandResult(completed.stdout, completed.stderr, int(completed.returncode))
    except OSError:
        return CommandResult("", f"تعذر تشغيل الأمر: {' '.join(command)}", 1)


def powershell_text(script: str) -> str:
    return run_text_command(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script])


def authenticode_signature(path: Path) -> str:
    escaped = str(path).replace("'", "''")
    script = (
        "$s=Get-AuthenticodeSignature -LiteralPath '" + escaped + "';"
        "Write-Output ($s.Status.ToString() + ' | ' + $s.SignerCertificate.Subject)"
    )
    output = powershell_text(script).strip()
    return output or "غير معروف"


def scan_hosts_file() -> list[str]:
    hosts = Path(os.environ.get("SystemRoot", r"C:\Windows")) / r"System32\drivers\etc\hosts"
    lines: list[str] = []
    try:
        for raw in hosts.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    except OSError:
        pass
    return lines


def scan_firewall_rules() -> list[str]:
    script = (
        "Get-NetFirewallRule | Where-Object {$_.Enabled -eq 'True'} | "
        "Select-Object -First 180 DisplayName,Direction,Action,Profile | "
        "ForEach-Object { \"$($_.DisplayName) | $($_.Direction) | $($_.Action) | $($_.Profile)\" }"
    )
    return [line for line in powershell_text(script).splitlines() if line.strip()]


def scan_wmi_persistence() -> list[str]:
    script = (
        "Get-CimInstance -Namespace root/subscription -ClassName __EventConsumer -ErrorAction SilentlyContinue | "
        "ForEach-Object { $_.__CLASS + ' | ' + $_.Name }"
    )
    return [line for line in powershell_text(script).splitlines() if line.strip()]


def browser_extension_dirs() -> list[Path]:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    app_data = Path(os.environ.get("APPDATA", ""))
    return [
        local_app_data / "Google" / "Chrome" / "User Data" / "Default" / "Extensions",
        local_app_data / "Microsoft" / "Edge" / "User Data" / "Default" / "Extensions",
        app_data / "Mozilla" / "Firefox" / "Profiles",
    ]


def scan_browser_extensions() -> list[str]:
    results: list[str] = []
    for root in browser_extension_dirs():
        if not root.exists():
            continue
        if root.name == "Profiles":
            for profile in root.iterdir():
                ext_dir = profile / "extensions"
                if ext_dir.exists():
                    for item in ext_dir.iterdir():
                        results.append(f"Firefox | {item}")
            continue
        browser = "Chrome" if "Chrome" in str(root) else "Edge"
        for extension in root.iterdir():
            if extension.is_dir():
                versions = [item.name for item in extension.iterdir() if item.is_dir()]
                results.append(f"{browser} | {extension.name} | versions: {', '.join(versions[:4])}")
    return results


def winget_available() -> bool:
    return bool(shutil.which("winget"))


def winget_upgrade_report() -> str:
    if not winget_available():
        return "winget غير متوفر على هذا الجهاز."
    result = run_command(["winget", "upgrade", "--source", "winget", "--accept-source-agreements"])
    return result.text() or "لا توجد تحديثات متاحة أو تعذر قراءة نتائج winget."


def run_winget_upgrade_all() -> str:
    if not winget_available():
        return "winget غير متوفر على هذا الجهاز."
    return run_command(["winget", "upgrade", "--all", "--source", "winget", "--accept-source-agreements", "--accept-package-agreements"]).text()


def dns_cache_lines() -> list[str]:
    output = run_text_command(["ipconfig", "/displaydns"])
    interesting: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("record name") or stripped.lower().startswith("a (host) record"):
            interesting.append(stripped)
    return interesting[:500]


def save_system_snapshot() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = install_snapshot()
    serializable = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "programs": sorted(snapshot["programs"]),
        "startup": snapshot["startup"],
        "services": sorted(snapshot["services"]),
        "tasks": sorted(snapshot["tasks"]),
        "files": {path: {"size": value[0], "mtime": value[1]} for path, value in dict(snapshot["files"]).items()},
    }
    atomic_write_json(SNAPSHOT_PATH, serializable)
    return SNAPSHOT_PATH


def compare_saved_snapshot() -> list[str]:
    if not SNAPSHOT_PATH.exists():
        return ["لا توجد Snapshot محفوظة. احفظ Snapshot أولًا."]
    try:
        previous = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["تعذر قراءة Snapshot السابقة."]
    current = install_snapshot()
    before = {
        "programs": set(previous.get("programs", [])),
        "startup": previous.get("startup", {}),
        "services": set(previous.get("services", [])),
        "tasks": set(previous.get("tasks", [])),
        "files": {path: (meta.get("size", 0), meta.get("mtime", 0)) for path, meta in previous.get("files", {}).items()},
    }
    return [f"Snapshot السابقة: {previous.get('created_at', 'غير معروف')}", *diff_install_snapshots(before, current)]


def service_risk_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    base = r"SYSTEM\CurrentControlSet\Services"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as parent:
            count, _, _ = winreg.QueryInfoKey(parent)
            for index in range(count):
                name = winreg.EnumKey(parent, index)
                try:
                    with winreg.OpenKey(parent, name) as key:
                        image = read_reg_value(key, "ImagePath")
                        account = read_reg_value(key, "ObjectName")
                except OSError:
                    continue
                score, level, reasons = startup_risk(name, image)
                if account.lower() == "localsystem":
                    score = min(100, score + 8)
                    reasons.append("الخدمة تعمل بصلاحية LocalSystem")
                rows.append({"name": name, "image": image, "account": account, "score": score, "level": level_for_score(score), "reasons": reasons})
    except OSError:
        pass
    return sorted(rows, key=lambda row: int(row["score"]), reverse=True)


def scheduled_task_detail_rows() -> list[dict[str, object]]:
    output = run_text_command(["schtasks", "/query", "/fo", "csv", "/v"])
    rows: list[dict[str, object]] = []
    if not output:
        return rows
    for row in csv.DictReader(output.splitlines()):
        name = row.get("TaskName", "")
        command = row.get("Task To Run", "") or row.get("تشغيل المهمة", "")
        score, level, reasons = startup_risk(name, command)
        rows.append({"name": name, "command": command, "score": score, "level": level, "reasons": reasons})
    return sorted(rows, key=lambda row: int(row["score"]), reverse=True)


def parse_startup_registry_key(key: str) -> tuple[int, str, str] | None:
    if key.startswith("HKCU\\"):
        hive = winreg.HKEY_CURRENT_USER
        remainder = key[5:]
    elif key.startswith("HKLM\\"):
        hive = winreg.HKEY_LOCAL_MACHINE
        remainder = key[5:]
    else:
        return None
    if "\\" not in remainder:
        return None
    path, value_name = remainder.rsplit("\\", 1)
    return hive, path, value_name


def load_disabled_startup() -> list[dict[str, str]]:
    if not DISABLED_STARTUP_PATH.exists():
        return []
    try:
        data = json.loads(DISABLED_STARTUP_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [dict(item) for item in data if isinstance(item, dict)]
    except (OSError, json.JSONDecodeError):
        return []
    return []


def save_disabled_startup(items: list[dict[str, str]]) -> None:
    atomic_write_json(DISABLED_STARTUP_PATH, items)


def disable_risky_startup(min_score: int = 45) -> tuple[int, list[str]]:
    disabled = load_disabled_startup()
    messages: list[str] = []
    count = 0
    for row in startup_hunter_rows():
        if int(row["score"]) < min_score:
            continue
        row_type = str(row["type"])
        if row_type == "Startup":
            parsed = parse_startup_registry_key(str(row["key"]))
            if parsed is not None:
                hive, path, value_name = parsed
                try:
                    with winreg.OpenKey(hive, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
                        value, value_type = winreg.QueryValueEx(key, value_name)
                        winreg.DeleteValue(key, value_name)
                    disabled.append({"kind": "registry", "key": str(row["key"]), "command": str(value), "value_type": str(value_type), "disabled_at": time.strftime("%Y-%m-%d %H:%M:%S")})
                    messages.append(f"تم تعطيل Registry Startup: {row['key']}")
                    count += 1
                except OSError as exc:
                    messages.append(f"فشل تعطيل {row['key']}: {exc}")
                continue
            if str(row["key"]).startswith("StartupFolder\\"):
                original = Path(str(row["command"]))
                try:
                    DISABLED_STARTUP_DIR.mkdir(parents=True, exist_ok=True)
                    target = DISABLED_STARTUP_DIR / safe_filename(original.name)
                    shutil.move(str(original), str(target))
                    disabled.append({"kind": "startup_folder", "key": str(row["key"]), "original": str(original), "quarantined": str(target), "disabled_at": time.strftime("%Y-%m-%d %H:%M:%S")})
                    messages.append(f"تم تعطيل Startup Folder: {original}")
                    count += 1
                except OSError as exc:
                    messages.append(f"فشل تعطيل {original}: {exc}")
                continue
        if row_type == "Scheduled Task":
            task_name = str(row["key"])
            result = run_command(["schtasks", "/Change", "/TN", task_name, "/Disable"])
            if result.returncode == 0:
                disabled.append({"kind": "scheduled_task", "key": task_name, "disabled_at": time.strftime("%Y-%m-%d %H:%M:%S")})
                messages.append(f"تم تعطيل Scheduled Task: {task_name}")
                count += 1
            else:
                messages.append(f"فشل تعطيل Scheduled Task {task_name}: {result.text()}")
    save_disabled_startup(disabled)
    return count, messages


def restore_disabled_startup() -> tuple[int, list[str]]:
    items = load_disabled_startup()
    remaining: list[dict[str, str]] = []
    messages: list[str] = []
    restored = 0
    for item in items:
        kind = item.get("kind", "registry")
        if kind == "registry":
            parsed = parse_startup_registry_key(item.get("key", ""))
            if parsed is None:
                remaining.append(item)
                continue
            hive, path, value_name = parsed
            try:
                with winreg.CreateKeyEx(hive, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, value_name, 0, int(item.get("value_type", item.get("type", str(winreg.REG_SZ)))), item.get("command", ""))
                messages.append(f"تم استرجاع Registry Startup: {item.get('key', '')}")
                restored += 1
            except OSError as exc:
                messages.append(f"فشل استرجاع {item.get('key', '')}: {exc}")
                remaining.append(item)
        elif kind == "startup_folder":
            original = Path(item.get("original", ""))
            quarantined = Path(item.get("quarantined", ""))
            try:
                original.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(quarantined), str(original))
                messages.append(f"تم استرجاع Startup Folder: {original}")
                restored += 1
            except OSError as exc:
                messages.append(f"فشل استرجاع {original}: {exc}")
                remaining.append(item)
        elif kind == "scheduled_task":
            task_name = item.get("key", "")
            result = run_command(["schtasks", "/Change", "/TN", task_name, "/Enable"])
            if result.returncode == 0:
                messages.append(f"تم تفعيل Scheduled Task: {task_name}")
                restored += 1
            else:
                messages.append(f"فشل تفعيل {task_name}: {result.text()}")
                remaining.append(item)
    save_disabled_startup(remaining)
    return restored, messages


def list_startup_items() -> dict[str, str]:
    items: dict[str, str] = {}
    for root, path in startup_registry_locations():
        try:
            with winreg.OpenKey(root, path) as key:
                count, _, _ = winreg.QueryInfoKey(key)
                for index in range(count):
                    name, value, _ = winreg.EnumValue(key, index)
                    hive = "HKCU" if root == winreg.HKEY_CURRENT_USER else "HKLM"
                    items[f"{hive}\\{path}\\{name}"] = str(value)
        except OSError:
            continue
    for folder in [
        Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup",
        Path(os.environ.get("ProgramData", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup",
    ]:
        if folder.exists():
            for item in folder.iterdir():
                items[f"StartupFolder\\{item.name}"] = str(item)
    return items


def extract_executable_from_command(command: str) -> Path | None:
    command = command.strip()
    if not command:
        return None
    quoted = re.match(r'^"([^"]+)"', command)
    if quoted:
        return Path(quoted.group(1))
    match = re.match(r"^([A-Za-z]:\\[^\s]+)", command)
    if match:
        return Path(match.group(1))
    return None


def startup_risk(key: str, command: str) -> tuple[int, str, list[str]]:
    reasons: list[str] = []
    score = 5
    lowered = command.lower()
    path = extract_executable_from_command(command)
    settings = load_settings()
    if any(token in lowered for token in ["powershell", "wscript", "cscript", "cmd.exe", "mshta", "rundll32"]):
        score += 25
        reasons.append("يستخدم مفسر أو أداة تشغيل حساسة")
    if any(token in lowered for token in ["encodedcommand", "bypass", "-hidden", "frombase64string", "downloadstring"]):
        score += 35
        reasons.append("يحتوي على مؤشرات Obfuscation أو تحميل مخفي")
    if any(token in lowered for token in ["\\temp\\", "\\downloads\\", "\\public\\"]):
        score += 25
        reasons.append("يعمل من مسار مؤقت أو عام")
    if "\\appdata\\" in lowered:
        score += 12
        reasons.append("يعمل من AppData")
    if path and path.exists():
        path_text = str(path).lower()
        if any(path_text.startswith(item.lower()) for item in settings["allow_paths"]):
            score -= 15
            reasons.append("المسار ضمن قائمة السماح الشخصية")
        if any(path_text.startswith(item.lower()) for item in settings["block_paths"]):
            score += 35
            reasons.append("المسار ضمن قائمة الحظر الشخصية")
        suffix = path.suffix.lower()
        if suffix in {".ps1", ".vbs", ".js", ".bat", ".cmd"}:
            score += 22
            reasons.append("عنصر Startup يشغل سكربت")
        entropy = file_entropy(path)
        if entropy >= 7.25:
            score += 18
            reasons.append(f"Entropy عالي للملف ({entropy:.2f})")
        signature = authenticode_signature(path)
        if signature.startswith("NotSigned"):
            score += 18
            reasons.append("الملف غير موقّع رقميًا")
        elif signature.startswith("Valid"):
            score -= 8
            reasons.append("توقيع رقمي صالح")
        digest = sha256_file(path)
        if digest and digest in settings["block_hashes"]:
            score += 45
            reasons.append("Hash ضمن قائمة الحظر الشخصية")
    else:
        score += 10
        reasons.append("تعذر تحديد أو العثور على الملف التنفيذي")
    if not reasons:
        reasons.append("لا توجد مؤشرات خطر واضحة")
    score = max(0, min(100, score))
    return score, level_for_score(score), reasons


def startup_hunter_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, command in list_startup_items().items():
        score, level, reasons = startup_risk(key, command)
        rows.append({"type": "Startup", "key": key, "command": command, "score": score, "level": level, "reasons": reasons})
    for task in scheduled_task_detail_rows():
        rows.append({"type": "Scheduled Task", "key": task["name"], "command": task["command"], "score": task["score"], "level": task["level"], "reasons": task["reasons"]})
    return sorted(rows, key=lambda item: int(item["score"]), reverse=True)


def list_services() -> set[str]:
    services: set[str] = set()
    path = r"SYSTEM\CurrentControlSet\Services"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
            count, _, _ = winreg.QueryInfoKey(key)
            for index in range(count):
                name = winreg.EnumKey(key, index)
                services.add(name)
    except OSError:
        pass
    return services


def list_scheduled_tasks() -> set[str]:
    output = run_text_command(["schtasks", "/query", "/fo", "csv", "/nh"])
    tasks: set[str] = set()
    if not output:
        return tasks
    for row in csv.reader(output.splitlines()):
        if row:
            tasks.add(row[0])
    return tasks


def executable_snapshot(limit: int = 4500) -> dict[str, tuple[int, float]]:
    roots = [root for root in candidate_roots() if root.exists()]
    data: dict[str, tuple[int, float]] = {}
    for root in roots:
        for current_root, _, file_names in os.walk(root):
            for file_name in file_names:
                if Path(file_name).suffix.lower() not in EXECUTABLE_EXTENSIONS:
                    continue
                path = Path(current_root) / file_name
                try:
                    stat = path.stat()
                except OSError:
                    continue
                data[str(path)] = (stat.st_size, stat.st_mtime)
                if len(data) >= limit:
                    return data
    return data


def install_snapshot() -> dict[str, object]:
    return {
        "programs": {f"{program.name}|{program.publisher}|{program.version}" for program in load_programs()},
        "startup": list_startup_items(),
        "services": list_services(),
        "tasks": list_scheduled_tasks(),
        "files": executable_snapshot(),
    }


def diff_install_snapshots(before: dict[str, object], after: dict[str, object]) -> list[str]:
    lines: list[str] = []
    before_programs = set(before["programs"])
    after_programs = set(after["programs"])
    before_startup = dict(before["startup"])
    after_startup = dict(after["startup"])
    before_services = set(before["services"])
    after_services = set(after["services"])
    before_tasks = set(before["tasks"])
    after_tasks = set(after["tasks"])
    before_files = dict(before["files"])
    after_files = dict(after["files"])

    sections = [
        ("برامج جديدة", sorted(after_programs - before_programs)),
        ("Startup جديد", [f"{key} -> {after_startup[key]}" for key in sorted(set(after_startup) - set(before_startup))]),
        ("Services جديدة", sorted(after_services - before_services)),
        ("Scheduled Tasks جديدة", sorted(after_tasks - before_tasks)),
        ("ملفات تنفيذية جديدة", sorted(set(after_files) - set(before_files))[:300]),
    ]
    for title, values in sections:
        lines.append("")
        lines.append(title)
        lines.append("-" * len(title))
        if not values:
            lines.append("لا يوجد")
        else:
            lines.extend(str(value) for value in values)
    return lines


def process_map() -> dict[str, str]:
    output = run_text_command(["tasklist", "/fo", "csv", "/nh"])
    mapping: dict[str, str] = {}
    for row in csv.reader(output.splitlines()):
        if len(row) >= 2:
            mapping[row[1]] = row[0]
    return mapping


def scan_connections() -> list[ConnectionItem]:
    output = run_text_command(["netstat", "-ano"])
    names = process_map()
    items: list[ConnectionItem] = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] not in {"TCP", "UDP"}:
            continue
        if parts[0] == "TCP" and len(parts) >= 5:
            protocol, local, remote, state, pid = parts[0], parts[1], parts[2], parts[3], parts[4]
        elif parts[0] == "UDP" and len(parts) >= 4:
            protocol, local, remote, state, pid = parts[0], parts[1], parts[2], "UDP", parts[3]
        else:
            continue
        if remote.startswith("127.") or remote.startswith("0.0.0.0") or remote.startswith("[::"):
            continue
        items.append(ConnectionItem(protocol, local, remote, state, pid, names.get(pid, "غير معروف")))
    return sorted(items, key=lambda item: (item.process.lower(), item.remote))


def scan_folder_security(folder: Path, limit: int = 500) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    scanned = 0
    for current_root, _, file_names in os.walk(folder):
        for file_name in file_names:
            path = Path(current_root) / file_name
            if path.suffix.lower() not in EXECUTABLE_EXTENSIONS:
                continue
            reasons = path_risk_reasons(path)
            reasons.extend(binary_risk_reasons(path))
            reasons.extend(script_risk_reasons(path))
            if reasons:
                score = min(100, 8 + len(reasons) * 18)
                findings.append(SecurityFinding(path, score, level_for_score(score), reasons))
            scanned += 1
            if scanned >= limit:
                return sorted(findings, key=lambda item: item.score, reverse=True)
    return sorted(findings, key=lambda item: item.score, reverse=True)


def behavior_snapshot() -> dict[str, object]:
    return {
        "connections": {f"{item.process}|{item.pid}|{item.remote}|{item.state}" for item in scan_connections()},
        "startup": list_startup_items(),
        "tasks": list_scheduled_tasks(),
        "services": list_services(),
        "processes": set(process_map().items()),
    }


def diff_behavior_snapshots(before: dict[str, object], after: dict[str, object]) -> list[str]:
    lines: list[str] = []
    sections = [
        ("عمليات جديدة", sorted(set(after["processes"]) - set(before["processes"]))),
        ("اتصالات جديدة", sorted(set(after["connections"]) - set(before["connections"]))),
        ("Startup جديد", [f"{key} -> {dict(after['startup'])[key]}" for key in sorted(set(dict(after["startup"])) - set(dict(before["startup"])))]),
        ("Scheduled Tasks جديدة", sorted(set(after["tasks"]) - set(before["tasks"]))),
        ("Services جديدة", sorted(set(after["services"]) - set(before["services"]))),
    ]
    for title, values in sections:
        lines.extend(["", title, "-" * len(title)])
        if values:
            lines.extend(str(value) for value in values[:250])
        else:
            lines.append("لا يوجد")
    return lines


def quarantine_summary_lines() -> list[str]:
    lines: list[str] = []
    manifests = quarantine_manifests()
    lines.append(f"عدد عمليات العزل: {len(manifests)}")
    for manifest in manifests[:60]:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items = data.get("items", [])
        lines.append(f"{data.get('created_at', '')} | {data.get('program', '')} | عناصر: {len(items)} | {manifest.parent}")
    return lines


def quarantine_path(path: Path, program_name: str) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    target_dir = QUARANTINE_DIR / f"{stamp}_{safe_filename(program_name)}"
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / safe_filename(path.name)


def quarantine(paths: list[Path], program_name: str) -> list[str]:
    moved: list[str] = []
    records: list[dict[str, str]] = []
    for path in paths:
        if not path.exists() or not path_is_safe(path):
            continue
        target = quarantine_path(path, program_name)
        counter = 1
        while target.exists():
            target = target.with_name(f"{target.stem}_{counter}{target.suffix}")
            counter += 1
        shutil.move(str(path), str(target))
        moved.append(str(target))
        records.append({"original": str(path), "quarantined": str(target)})
    if records:
        manifest_path = Path(moved[0]).parent / MANIFEST_NAME
        atomic_write_json(manifest_path, {"program": program_name, "created_at": time.strftime("%Y-%m-%d %H:%M:%S"), "items": records})
    return moved


def restore_latest_quarantine() -> tuple[int, Path | None]:
    if not QUARANTINE_DIR.exists():
        return 0, None
    manifests = sorted(QUARANTINE_DIR.glob(f"*/{MANIFEST_NAME}"), key=lambda item: item.stat().st_mtime, reverse=True)
    if not manifests:
        return 0, None

    manifest_path = manifests[0]
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored = 0
    for item in data.get("items", []):
        original = Path(str(item.get("original", "")))
        quarantined = Path(str(item.get("quarantined", "")))
        if not quarantined.exists():
            continue
        if original.exists():
            continue
        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(quarantined), str(original))
        restored += 1
    return restored, manifest_path


def quarantine_manifests() -> list[Path]:
    if not QUARANTINE_DIR.exists():
        return []
    return sorted(QUARANTINE_DIR.glob(f"*/{MANIFEST_NAME}"), key=lambda item: item.stat().st_mtime, reverse=True)


def delete_quarantine_manifest(manifest_path: Path) -> int:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    deleted = 0
    for item in data.get("items", []):
        quarantined = Path(str(item.get("quarantined", "")))
        if quarantined.exists() and path_is_safe(quarantined):
            if delete_path(quarantined):
                deleted += 1
    try:
        manifest_path.unlink(missing_ok=True)
    except OSError:
        pass
    return deleted


def write_report(report: dict[str, object]) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    program = safe_filename(str(report.get("program", "program")))
    path = LOG_DIR / f"{stamp}_{program}.txt"
    lines = [
        APP_REPORT_NAME,
        "=" * 44,
        f"الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"البرنامج: {report.get('program', '')}",
        f"رمز مزيل التثبيت: {report.get('uninstall_code', '')}",
        f"المخلفات المكتشفة: {report.get('leftovers_found', 0)}",
        f"المخلفات المعزولة: {report.get('leftovers_quarantined', 0)}",
        f"عناصر الكاش المحذوفة: {report.get('cache_deleted', 0)}",
        f"حجم الكاش المحذوف: {report.get('cache_size', '')}",
        "",
        "المخلفات:",
    ]
    for item in report.get("leftovers", []):
        lines.append(str(item))
    lines.extend(["", "العزل:"])
    for item in report.get("quarantine_paths", []):
        lines.append(str(item))
    atomic_write_text(path, "\n".join(lines), encoding="utf-8")
    return path


class WindowsTrayIcon:
    CMD_SHOW = 1001
    CMD_TOGGLE_DHIKR = 1002
    CMD_OPEN_X = 1003
    CMD_EXIT = 1004

    def __init__(self, app: "RootUninstallerApp") -> None:
        self.app = app
        self.hwnd = 0
        self.icon = 0
        self.uid = 1
        self.callback_message = (win32con.WM_USER + 42) if win32con is not None else 0
        self.class_name = f"NiqaaTrayWindow{os.getpid()}"
        self.created = False

    def create(self) -> bool:
        if win32gui is None or win32con is None or win32api is None:
            return False
        try:
            message_map = {
                win32con.WM_DESTROY: self.on_destroy,
                self.callback_message: self.on_tray_event,
            }
            window_class = win32gui.WNDCLASS()
            window_class.hInstance = win32api.GetModuleHandle(None)
            window_class.lpszClassName = self.class_name
            window_class.lpfnWndProc = message_map
            try:
                win32gui.RegisterClass(window_class)
            except win32gui.error:
                pass
            self.hwnd = win32gui.CreateWindow(
                self.class_name,
                APP_NAME,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                window_class.hInstance,
                None,
            )
            self.icon = self.load_icon()
            flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
            data = (self.hwnd, self.uid, flags, self.callback_message, self.icon, f"{APP_NAME} يعمل بالخلفية")
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, data)
            self.created = True
            return True
        except Exception:
            self.created = False
            return False

    def load_icon(self) -> int:
        if win32gui is None or win32con is None:
            return 0
        try:
            large, small = win32gui.ExtractIconEx(sys.executable, 0)
            if small:
                return small[0]
            if large:
                return large[0]
        except Exception:
            pass
        return win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

    def on_destroy(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:
        return 0

    def on_tray_event(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:
        if win32con is None:
            return 0
        if lparam in (win32con.WM_LBUTTONUP, win32con.WM_LBUTTONDBLCLK):
            self.app.after(0, self.app.show_from_tray)
        elif lparam in (win32con.WM_RBUTTONUP, win32con.WM_CONTEXTMENU):
            self.show_menu()
        return 0

    def show_menu(self) -> None:
        if win32gui is None or win32con is None:
            return
        menu = win32gui.CreatePopupMenu()
        dhikr_label = "إيقاف تنبيهات الأذكار" if self.app.dhikr_notifications_enabled else "تشغيل تنبيهات الأذكار"
        win32gui.AppendMenu(menu, win32con.MF_STRING, self.CMD_SHOW, "فتح نقاء")
        win32gui.AppendMenu(menu, win32con.MF_STRING, self.CMD_TOGGLE_DHIKR, dhikr_label)
        win32gui.AppendMenu(menu, win32con.MF_STRING, self.CMD_OPEN_X, "حساب X للتواصل")
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        win32gui.AppendMenu(menu, win32con.MF_STRING, self.CMD_EXIT, "خروج نهائي")
        x, y = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self.hwnd)
        command = win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_RETURNCMD | win32con.TPM_NONOTIFY | win32con.TPM_RIGHTBUTTON,
            x,
            y,
            0,
            self.hwnd,
            None,
        )
        if command:
            self.app.after(0, lambda: self.handle_command(command))
        win32gui.DestroyMenu(menu)

    def handle_command(self, command: int) -> None:
        if command == self.CMD_SHOW:
            self.app.show_from_tray()
        elif command == self.CMD_TOGGLE_DHIKR:
            self.app.toggle_dhikr_notifications()
        elif command == self.CMD_OPEN_X:
            self.app.open_x_profile()
        elif command == self.CMD_EXIT:
            self.app.exit_application()

    def notify(self, message: str) -> None:
        if not self.created or win32gui is None:
            return
        try:
            data = (
                self.hwnd,
                self.uid,
                win32gui.NIF_INFO,
                self.callback_message,
                self.icon,
                f"{APP_NAME} يعمل بالخلفية",
                message,
                7000,
                "نقاء",
            )
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, data)
        except Exception:
            return

    def remove(self) -> None:
        if not self.created or win32gui is None:
            return
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, self.uid))
        except Exception:
            pass
        try:
            win32gui.DestroyWindow(self.hwnd)
        except Exception:
            pass
        self.created = False


class RootUninstallerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1280x780")
        self.minsize(920, 560)
        self.resizable(True, True)
        self.configure(bg="#111827")

        self.programs: list[Program] = []
        self.filtered: list[Program] = []
        self.leftovers: list[LeftoverItem] = []
        self.selected_program: Program | None = None
        self.sort_column = "name"
        self.sort_desc = False
        self.lang = "ar"
        self.ui_text_widgets: dict[str, tk.Widget] = {}
        self.guardian_enabled = False
        self.guardian_startup_baseline: dict[str, str] = {}
        self.tray_icon = None
        self.dhikr_notifications_enabled = False
        self.dhikr_notification_after: str | None = None
        self.dhikr_interval_minutes = DEFAULT_DHIKR_INTERVAL_MINUTES
        self.active_dhikr_toast: tk.Toplevel | None = None
        self.force_exit = False
        self.action_buttons: list[ttk.Button] = []
        self.stat_cards: list[tk.Frame] = []
        self._responsive_after: str | None = None
        self._sash_after: str | None = None
        self._layout_mode = ""
        self._action_columns = 0
        self._stat_columns = 0
        self._pane_orientation = tk.HORIZONTAL

        self.search_var = tk.StringVar()
        self.sort_var = tk.StringVar(value="الاسم")
        self.status_var = tk.StringVar(value="جاهز")
        self.admin_var = tk.StringVar(value="صلاحيات المسؤول: نعم" if is_admin() else "صلاحيات المسؤول: لا")
        self.program_count_var = tk.StringVar(value="0")
        self.leftover_count_var = tk.StringVar(value="0")
        self.selected_name_var = tk.StringVar(value="لم يتم اختيار برنامج")
        self.selected_meta_var = tk.StringVar(value="اختر برنامجًا من القائمة لعرض التفاصيل والخيارات.")
        self.selected_path_var = tk.StringVar(value="")
        self.dhikr_var = tk.StringVar(value=random.choice(ADHKAR))
        self.dhikr_index = 0

        self.create_style()
        self.create_widgets()
        self.create_tray_icon()
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.bind("<Configure>", self.schedule_responsive_layout)
        self.after_idle(self.apply_responsive_layout)
        self.refresh_programs()
        self.animate_dhikr()

    def create_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background="#111827")
        style.configure("Surface.TFrame", background="#172033")
        style.configure("Treeview", background="#111827", foreground="#F9FAFB", fieldbackground="#111827", rowheight=28, borderwidth=0)
        style.configure("Treeview.Heading", background="#312E81", foreground="#FFFFFF", font=("Segoe UI", 9, "bold"), padding=6)
        style.map("Treeview", background=[("selected", "#4F46E5")])
        style.configure("TButton", padding=(9, 5), font=("Segoe UI", 9, "bold"), background="#312E81", foreground="#FFFFFF")
        style.configure("Accent.TButton", padding=(10, 6), font=("Segoe UI", 9, "bold"), background="#4F46E5", foreground="#FFFFFF")
        style.configure("Danger.TButton", padding=(10, 6), font=("Segoe UI", 9, "bold"), background="#B91C1C", foreground="#FFFFFF")
        style.configure("TLabel", background="#111827", foreground="#F9FAFB", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#111827", foreground="#CBD5E1", font=("Segoe UI", 9))
        style.configure("Surface.TLabel", background="#172033", foreground="#F9FAFB", font=("Segoe UI", 10))
        style.configure("SurfaceMuted.TLabel", background="#172033", foreground="#CBD5E1", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#FFFFFF")
        style.configure("Dhikr.TLabel", background="#312E81", foreground="#FFFFFF", font=("Segoe UI", 11, "bold"))
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#CBD5E1")
        style.configure("Stat.TLabel", background="#172033", foreground="#FFFFFF", font=("Segoe UI", 13, "bold"))
        style.configure("StatName.TLabel", background="#172033", foreground="#A5B4FC", font=("Segoe UI", 8, "bold"))

    def create_widgets(self) -> None:
        root = ttk.Frame(self)
        self.root_frame = root
        root.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        self.header = tk.Frame(root, bg="#172033", highlightbackground="#334155", highlightthickness=1)
        self.header.pack(fill=tk.X, pady=(0, 12))
        self.title_area = tk.Frame(self.header, bg="#172033")
        self.title_area.pack(side=tk.RIGHT, fill=tk.Y, padx=12, pady=7)
        self.title_label = ttk.Label(self.title_area, text=APP_NAME, style="Header.TLabel")
        self.title_label.pack(anchor=tk.E)
        self.subtitle_label = ttk.Label(self.title_area, text=APP_SUBTITLE, style="SurfaceMuted.TLabel")
        self.subtitle_label.pack(anchor=tk.E, pady=(4, 0))
        self.social_row = tk.Frame(self.title_area, bg="#172033")
        self.social_row.pack(anchor=tk.E, pady=(6, 0))
        tk.Button(
            self.social_row,
            text=f"X  {CONTACT_HANDLE}",
            command=self.open_x_profile,
            bg="#020617",
            fg="#FFFFFF",
            activebackground="#111827",
            activeforeground="#A5B4FC",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.RIGHT)
        ttk.Label(self.social_row, text=f"المطور: {DEVELOPER_NAME} | {COPYRIGHT_TEXT}", style="SurfaceMuted.TLabel").pack(side=tk.RIGHT, padx=(0, 10))

        self.admin_area = tk.Frame(self.header, bg="#172033")
        self.admin_area.pack(side=tk.LEFT, padx=10, pady=7)
        ttk.Label(self.admin_area, textvariable=self.admin_var, style="Surface.TLabel").pack(anchor=tk.W)
        if not is_admin():
            ttk.Button(self.admin_area, text="تشغيل كمسؤول", command=self.request_admin).pack(anchor=tk.W, pady=(8, 0))
        self.ui_text_widgets["language"] = ttk.Button(self.admin_area, text=TEXT[self.lang]["language"], command=self.toggle_language)
        self.ui_text_widgets["language"].pack(anchor=tk.W, pady=(6, 0))

        self.stats_frame = ttk.Frame(root)
        self.stats_frame.pack(fill=tk.X, pady=(0, 8))
        self.stat_cards = [
            self.add_stat_card(self.stats_frame, "البرامج", self.program_count_var),
            self.add_stat_card(self.stats_frame, "المخلفات", self.leftover_count_var),
            self.add_stat_card(self.stats_frame, "الحالة", self.status_var),
        ]

        dhikr_bar = tk.Frame(root, bg="#312E81", highlightbackground="#818CF8", highlightthickness=1)
        dhikr_bar.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(dhikr_bar, textvariable=self.dhikr_var, style="Dhikr.TLabel").pack(anchor=tk.CENTER, pady=5)

        self.toolbar = tk.Frame(root, bg="#172033", highlightbackground="#334155", highlightthickness=1)
        self.toolbar.pack(fill=tk.X, pady=(0, 8))
        self.search_frame = tk.Frame(self.toolbar, bg="#172033")
        self.search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10, pady=8)
        self.ui_text_widgets["search"] = ttk.Label(self.search_frame, text=TEXT[self.lang]["search"], style="SurfaceMuted.TLabel")
        self.ui_text_widgets["search"].pack(anchor=tk.E, pady=(0, 4))
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, font=("Segoe UI", 12), justify="right")
        self.search_entry.pack(fill=tk.X)
        self.search_entry.bind("<KeyRelease>", lambda _event: self.apply_filter())

        self.sort_frame = tk.Frame(self.toolbar, bg="#172033")
        self.sort_frame.pack(side=tk.RIGHT, padx=(0, 10), pady=8)
        self.ui_text_widgets["sort"] = ttk.Label(self.sort_frame, text=TEXT[self.lang]["sort"], style="SurfaceMuted.TLabel")
        self.ui_text_widgets["sort"].pack(anchor=tk.E, pady=(0, 4))
        self.sort_box = ttk.Combobox(
            self.sort_frame,
            textvariable=self.sort_var,
            values=("الاسم", "الحجم", "الناشر", "الإصدار"),
            state="readonly",
            width=14,
            justify="right",
        )
        self.sort_box.pack()
        self.sort_box.configure(values=("الاسم", "الحجم", "الناشر", "الإصدار", "آخر تثبيت"))
        self.sort_box.bind("<<ComboboxSelected>>", lambda _event: self.apply_sort_choice())

        self.actions_frame = tk.Frame(self.toolbar, bg="#172033")
        self.actions_frame.pack(side=tk.LEFT, padx=10, pady=8)
        self.add_action_button(self.actions_frame, "remove", self.uninstall_selected, 0, 0, "Danger.TButton")
        self.add_action_button(self.actions_frame, "leftovers", self.scan_selected, 0, 1, "Accent.TButton")
        self.add_action_button(self.actions_frame, "security", self.security_scan_selected, 0, 2)
        self.add_action_button(self.actions_frame, "cache", self.clean_cache_selected, 0, 3)
        self.add_action_button(self.actions_frame, "device_cache", self.clean_device_cache_action, 0, 4)
        self.add_action_button(self.actions_frame, "install_watch", self.install_watcher_action, 1, 0)
        self.add_action_button(self.actions_frame, "connections", self.connection_watch_action, 1, 1)
        self.add_action_button(self.actions_frame, "startup", self.startup_hunter_action, 1, 2)
        self.add_action_button(self.actions_frame, "folder_scan", self.portable_folder_scan_action, 1, 3)
        self.add_action_button(self.actions_frame, "health", self.health_report_action, 1, 4)
        self.add_action_button(self.actions_frame, "behavior", self.behavior_monitor_action, 2, 0)
        self.add_action_button(self.actions_frame, "hash", self.hash_baseline_action, 2, 1)
        self.add_action_button(self.actions_frame, "quarantine", self.quarantine_center_action, 2, 2)
        self.add_action_button(self.actions_frame, "forensics", self.forensics_report_action, 2, 3)
        self.add_action_button(self.actions_frame, "refresh", self.refresh_programs, 2, 4)
        self.add_action_button(self.actions_frame, "smart_scan", self.smart_scan_action, 3, 0)
        self.add_action_button(self.actions_frame, "updates", self.software_updates_action, 3, 1)
        self.add_action_button(self.actions_frame, "dns", self.dns_watch_action, 3, 2)
        self.add_action_button(self.actions_frame, "guardian", self.guardian_toggle_action, 3, 3)
        self.add_action_button(self.actions_frame, "snapshot", self.snapshot_action, 3, 4)
        self.add_action_button(self.actions_frame, "allow_block", self.allow_block_center_action, 4, 0)
        self.add_action_button(self.actions_frame, "disable_startup", self.disable_risky_startup_action, 4, 1)
        self.add_action_button(self.actions_frame, "restore_startup", self.restore_disabled_startup_action, 4, 2)
        self.add_action_button(self.actions_frame, "advanced_clean", self.advanced_clean_action, 4, 3)
        self.add_action_button(self.actions_frame, "restore", self.restore_last_quarantine, 4, 4)
        self.add_action_button(self.actions_frame, "dhikr_alerts", self.toggle_dhikr_notifications, 5, 0)
        self.add_action_button(self.actions_frame, "dhikr_interval", self.configure_dhikr_interval, 5, 1)
        self.add_action_button(self.actions_frame, "dhikr_background", self.hide_to_tray, 5, 2)
        self.add_action_button(self.actions_frame, "stop_dhikr_background", self.stop_dhikr_background, 5, 3)
        self.add_action_button(self.actions_frame, "settings_io", self.settings_import_export_action, 6, 0, columnspan=5)

        detail = tk.Frame(root, bg="#172033", highlightbackground="#334155", highlightthickness=1)
        detail.pack(fill=tk.X, pady=(0, 10))
        self.selected_name_label = ttk.Label(detail, textvariable=self.selected_name_var, style="Surface.TLabel", font=("Segoe UI", 11, "bold"))
        self.selected_name_label.pack(anchor=tk.E, padx=12, pady=(7, 1))
        self.selected_meta_label = ttk.Label(detail, textvariable=self.selected_meta_var, style="SurfaceMuted.TLabel")
        self.selected_meta_label.pack(anchor=tk.E, padx=14)
        self.selected_path_label = ttk.Label(detail, textvariable=self.selected_path_var, style="SurfaceMuted.TLabel")
        self.selected_path_label.pack(anchor=tk.E, padx=14, pady=(1, 7))

        self.panes = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.panes.pack(fill=tk.BOTH, expand=True)

        self.program_frame = tk.Frame(self.panes, bg="#172033", highlightbackground="#334155", highlightthickness=1)
        self.leftovers_frame = tk.Frame(self.panes, bg="#172033", highlightbackground="#334155", highlightthickness=1)
        self.panes.add(self.program_frame, weight=3)
        self.panes.add(self.leftovers_frame, weight=2)

        self.ui_text_widgets["programs"] = ttk.Label(self.program_frame, text=TEXT[self.lang]["programs"], style="Surface.TLabel", font=("Segoe UI", 11, "bold"))
        self.ui_text_widgets["programs"].pack(anchor=tk.E, padx=12, pady=(10, 6))

        self.program_tree = ttk.Treeview(
            self.program_frame,
            columns=("size", "install_date", "publisher", "version"),
            show="tree headings",
            selectmode="browse",
        )
        self.program_tree.heading("#0", text="البرنامج", command=lambda: self.sort_by_column("name"))
        self.program_tree.heading("size", text="الحجم", command=lambda: self.sort_by_column("size"))
        self.program_tree.heading("install_date", text="آخر تثبيت", command=lambda: self.sort_by_column("install_date"))
        self.program_tree.heading("publisher", text="الناشر", command=lambda: self.sort_by_column("publisher"))
        self.program_tree.heading("version", text="الإصدار", command=lambda: self.sort_by_column("version"))
        self.program_tree.column("#0", width=255, anchor=tk.E)
        self.program_tree.column("size", width=95, anchor=tk.CENTER)
        self.program_tree.column("install_date", width=95, anchor=tk.CENTER)
        self.program_tree.column("publisher", width=160, anchor=tk.E)
        self.program_tree.column("version", width=85, anchor=tk.CENTER)
        self.program_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.program_tree.bind("<<TreeviewSelect>>", lambda _event: self.on_program_select())

        self.ui_text_widgets["details"] = ttk.Label(self.leftovers_frame, text=TEXT[self.lang]["details"], style="Surface.TLabel", font=("Segoe UI", 11, "bold"))
        self.ui_text_widgets["details"].pack(anchor=tk.E, padx=12, pady=(10, 4))
        self.details_tree = ttk.Treeview(self.leftovers_frame, columns=("value",), show="tree headings", height=6, selectmode="none")
        self.details_tree.heading("#0", text="الحقل")
        self.details_tree.heading("value", text="القيمة")
        self.details_tree.column("#0", width=120, anchor=tk.E)
        self.details_tree.column("value", width=420, anchor=tk.E)
        self.details_tree.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.ui_text_widgets["leftovers_title"] = ttk.Label(self.leftovers_frame, text=TEXT[self.lang]["leftovers_title"], style="Surface.TLabel", font=("Segoe UI", 11, "bold"))
        self.ui_text_widgets["leftovers_title"].pack(anchor=tk.E, padx=12, pady=(2, 2))
        self.leftover_hint_label = ttk.Label(self.leftovers_frame, text="استخدم الكلك يمين للعزل، النسخ، أو فتح المسار.", style="SurfaceMuted.TLabel")
        self.leftover_hint_label.pack(anchor=tk.E, padx=12, pady=(0, 6))
        self.leftover_tree = ttk.Treeview(self.leftovers_frame, columns=("size", "confidence", "reason"), show="tree headings", selectmode="extended")
        self.leftover_tree.heading("#0", text="المسار")
        self.leftover_tree.heading("size", text="الحجم")
        self.leftover_tree.heading("confidence", text="الثقة")
        self.leftover_tree.heading("reason", text="السبب")
        self.leftover_tree.column("#0", width=390, anchor=tk.E)
        self.leftover_tree.column("size", width=85, anchor=tk.CENTER)
        self.leftover_tree.column("confidence", width=70, anchor=tk.CENTER)
        self.leftover_tree.column("reason", width=170, anchor=tk.E)
        self.leftover_tree.pack(fill=tk.BOTH, expand=True, padx=10)
        self.leftover_tree.bind("<Button-3>", self.show_leftover_menu)

        action_bar = tk.Frame(self.leftovers_frame, bg="#172033")
        action_bar.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(action_bar, text="عزل البقايا المحددة", command=self.clean_selected_leftovers).pack(side=tk.LEFT)
        ttk.Button(action_bar, text="فتح مجلد العزل", command=self.open_quarantine).pack(side=tk.LEFT, padx=6)

        self.program_tree.bind("<Button-3>", self.show_program_menu)

        footer = ttk.Frame(root)
        footer.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(footer, textvariable=self.status_var).pack(side=tk.RIGHT)
        ttk.Label(footer, text=f"المطور: {DEVELOPER_NAME} | {COPYRIGHT_TEXT} | X {CONTACT_HANDLE}", style="Muted.TLabel").pack(side=tk.LEFT)

    def add_stat_card(self, parent: tk.Widget, label: str, variable: tk.StringVar) -> tk.Frame:
        card = tk.Frame(parent, bg="#172033", highlightbackground="#334155", highlightthickness=1)
        ttk.Label(card, text=label, style="StatName.TLabel").pack(anchor=tk.E, padx=10, pady=(6, 1))
        ttk.Label(card, textvariable=variable, style="Stat.TLabel").pack(anchor=tk.E, padx=10, pady=(0, 6))
        return card

    def add_action_button(
        self,
        parent: tk.Widget,
        key: str,
        command: object,
        row: int,
        column: int,
        style: str = "TButton",
        columnspan: int = 1,
    ) -> None:
        button = ttk.Button(parent, text=TEXT[self.lang][key], command=command, style=style)
        button.grid(row=row, column=column, columnspan=columnspan, sticky="ew", padx=3, pady=2)
        self.ui_text_widgets[key] = button
        self.action_buttons.append(button)

    def schedule_responsive_layout(self, event: tk.Event | None = None) -> None:
        if event is not None and event.widget is not self:
            return
        if self._responsive_after is not None:
            self.after_cancel(self._responsive_after)
        self._responsive_after = self.after(70, self.apply_responsive_layout)

    def apply_responsive_layout(self) -> None:
        self._responsive_after = None
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)

        header_mode = "compact" if width < 1040 else "wide"
        toolbar_mode = "stacked" if width < 1120 else "wide"
        pane_orientation = tk.VERTICAL if width < 980 else tk.HORIZONTAL
        layout_mode = f"{header_mode}:{toolbar_mode}:{pane_orientation}"

        if layout_mode != self._layout_mode:
            self.layout_header(header_mode)
            self.layout_toolbar(toolbar_mode)
            self.panes.configure(orient=pane_orientation)
            self._pane_orientation = pane_orientation
            self._layout_mode = layout_mode

        stat_columns = 1 if width < 760 else 2 if width < 1040 else 3
        if stat_columns != self._stat_columns:
            self.layout_stat_cards(stat_columns)

        action_columns = 2 if width < 760 else 3 if width < 980 else 4 if width < 1220 else 5
        if action_columns != self._action_columns:
            self.layout_action_buttons(action_columns)

        wrap = max(300, width - 420 if header_mode == "wide" else width - 80)
        self.subtitle_label.configure(wraplength=wrap, justify=tk.RIGHT)
        self.selected_name_label.configure(wraplength=max(320, width - 80), justify=tk.RIGHT)
        self.selected_meta_label.configure(wraplength=max(320, width - 80), justify=tk.RIGHT)
        self.selected_path_label.configure(wraplength=max(320, width - 80), justify=tk.RIGHT)
        self.leftover_hint_label.configure(wraplength=max(260, width // 2), justify=tk.RIGHT)

        self.resize_tree_columns()
        self.animate_pane_sash(width, height)

    def layout_header(self, mode: str) -> None:
        self.title_area.pack_forget()
        self.admin_area.pack_forget()
        if mode == "compact":
            self.title_area.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(8, 4))
            self.admin_area.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(0, 8))
            return
        self.title_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=7)
        self.admin_area.pack(side=tk.LEFT, padx=10, pady=7)

    def layout_toolbar(self, mode: str) -> None:
        self.search_frame.pack_forget()
        self.sort_frame.pack_forget()
        self.actions_frame.pack_forget()
        if mode == "stacked":
            self.search_frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=10, pady=(8, 4))
            self.sort_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 4))
            self.sort_box.pack_configure(fill=tk.X)
            self.actions_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(4, 8))
            return
        self.actions_frame.pack(side=tk.LEFT, padx=10, pady=8)
        self.sort_frame.pack(side=tk.RIGHT, padx=(0, 10), pady=8)
        self.sort_box.pack_configure(fill=tk.NONE)
        self.search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10, pady=8)

    def layout_stat_cards(self, columns: int) -> None:
        self._stat_columns = columns
        for card in self.stat_cards:
            card.grid_forget()
        for column in range(3):
            self.stats_frame.grid_columnconfigure(column, weight=0, uniform="")
        for index, card in enumerate(self.stat_cards):
            row = index // columns
            column = columns - 1 - (index % columns)
            card.grid(row=row, column=column, sticky="ew", padx=4, pady=4)
        for column in range(columns):
            self.stats_frame.grid_columnconfigure(column, weight=1, uniform="stats")

    def layout_action_buttons(self, columns: int) -> None:
        self._action_columns = columns
        for button in self.action_buttons:
            button.grid_forget()
        for column in range(5):
            self.actions_frame.grid_columnconfigure(column, weight=0, uniform="")

        full_width_index = len(self.action_buttons) - 1
        for index, button in enumerate(self.action_buttons):
            if index == full_width_index and columns > 1:
                row = (index + columns - 1) // columns
                button.grid(row=row, column=0, columnspan=columns, sticky="ew", padx=3, pady=3)
                break
            row = index // columns
            column = columns - 1 - (index % columns)
            button.grid(row=row, column=column, sticky="ew", padx=3, pady=3)

        for column in range(columns):
            self.actions_frame.grid_columnconfigure(column, weight=1, uniform="actions")

    def resize_tree_columns(self) -> None:
        program_width = max(self.program_frame.winfo_width() - 38, 520)
        size_width = 92
        date_width = 104
        version_width = 84
        publisher_width = max(120, min(210, program_width // 4))
        name_width = max(180, program_width - size_width - date_width - version_width - publisher_width)
        self.program_tree.column("#0", width=name_width, minwidth=160, anchor=tk.E)
        self.program_tree.column("size", width=size_width, minwidth=76, anchor=tk.CENTER)
        self.program_tree.column("install_date", width=date_width, minwidth=86, anchor=tk.CENTER)
        self.program_tree.column("publisher", width=publisher_width, minwidth=110, anchor=tk.E)
        self.program_tree.column("version", width=version_width, minwidth=72, anchor=tk.CENTER)

        details_width = max(self.leftovers_frame.winfo_width() - 38, 420)
        self.details_tree.column("#0", width=130, minwidth=105, anchor=tk.E)
        self.details_tree.column("value", width=max(260, details_width - 130), minwidth=220, anchor=tk.E)

        leftovers_width = max(self.leftovers_frame.winfo_width() - 38, 520)
        leftover_size_width = 84
        confidence_width = 72
        reason_width = max(120, min(210, leftovers_width // 4))
        path_width = max(240, leftovers_width - leftover_size_width - confidence_width - reason_width)
        self.leftover_tree.column("#0", width=path_width, minwidth=220, anchor=tk.E)
        self.leftover_tree.column("size", width=leftover_size_width, minwidth=72, anchor=tk.CENTER)
        self.leftover_tree.column("confidence", width=confidence_width, minwidth=64, anchor=tk.CENTER)
        self.leftover_tree.column("reason", width=reason_width, minwidth=110, anchor=tk.E)

    def animate_pane_sash(self, width: int, height: int) -> None:
        if self._sash_after is not None:
            self.after_cancel(self._sash_after)
            self._sash_after = None
        try:
            if self._pane_orientation == tk.HORIZONTAL:
                pane_size = self.panes.winfo_width()
                target = int(pane_size * (0.52 if width < 1180 else 0.54))
            else:
                pane_size = self.panes.winfo_height()
                target = int(pane_size * (0.48 if height < 720 else 0.52))
            if pane_size > 80:
                self.ease_sash_to(target)
        except tk.TclError:
            return

    def ease_sash_to(self, target: int) -> None:
        try:
            current = self.panes.sashpos(0)
        except tk.TclError:
            return
        delta = target - current
        if abs(delta) <= 3:
            try:
                self.panes.sashpos(0, target)
            except tk.TclError:
                return
            return
        next_position = current + int(delta * 0.28)
        if next_position == current:
            next_position += 1 if delta > 0 else -1
        try:
            self.panes.sashpos(0, next_position)
        except tk.TclError:
            return
        self._sash_after = self.after(16, lambda: self.ease_sash_to(target))

    def toggle_language(self) -> None:
        self.lang = "en" if self.lang == "ar" else "ar"
        for key, widget in self.ui_text_widgets.items():
            if key in TEXT[self.lang]:
                widget.configure(text=TEXT[self.lang][key])
        self.set_status("Language switched" if self.lang == "en" else "تم تغيير اللغة")

    def open_x_profile(self) -> None:
        webbrowser.open(CONTACT_URL)
        self.set_status(f"تم فتح حساب X: {CONTACT_HANDLE}")

    def create_tray_icon(self) -> None:
        tray = WindowsTrayIcon(self)
        if tray.create():
            self.tray_icon = tray
            self.set_status("نقاء جاهز ويعمل من شريط النظام عند إغلاق النافذة")
        else:
            self.tray_icon = None

    def show_from_tray(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        self.set_status("تم فتح نقاء من شريط النظام")

    def hide_to_tray(self) -> None:
        if self.tray_icon is None:
            self.iconify()
            self.set_status("تم تصغير نقاء")
            return
        if not self.dhikr_notifications_enabled:
            self.toggle_dhikr_notifications(show_message=False)
        self.withdraw()
        self.tray_icon.notify("نقاء يعمل الآن بجانب الساعة. كلك يمين على الأيقونة للتحكم أو الخروج النهائي.")
        self.set_status("نقاء يعمل بالخلفية من شريط النظام")

    def exit_application(self) -> None:
        self.force_exit = True
        self.dhikr_notifications_enabled = False
        if self.dhikr_notification_after is not None:
            self.after_cancel(self.dhikr_notification_after)
            self.dhikr_notification_after = None
        if self.active_dhikr_toast is not None and self.active_dhikr_toast.winfo_exists():
            self.active_dhikr_toast.destroy()
        if self.tray_icon is not None:
            self.tray_icon.remove()
        self.destroy()

    def toggle_dhikr_notifications(self, show_message: bool = True) -> None:
        self.dhikr_notifications_enabled = not self.dhikr_notifications_enabled
        if self.dhikr_notifications_enabled:
            self.schedule_dhikr_notification(first=True)
            self.set_status(f"تم تشغيل تنبيهات الأذكار كل {self.dhikr_interval_minutes} دقائق")
            if show_message:
                self.show_dhikr_notification()
            return
        if self.dhikr_notification_after is not None:
            self.after_cancel(self.dhikr_notification_after)
            self.dhikr_notification_after = None
        self.set_status("تم إيقاف تنبيهات الأذكار")

    def schedule_dhikr_notification(self, first: bool = False) -> None:
        if self.dhikr_notification_after is not None:
            self.after_cancel(self.dhikr_notification_after)
        delay = 2000 if first else max(1, self.dhikr_interval_minutes) * 60 * 1000
        self.dhikr_notification_after = self.after(delay, self.show_dhikr_notification)

    def show_dhikr_notification(self) -> None:
        if not self.dhikr_notifications_enabled:
            return
        message = random.choice(DHIKR_NOTIFICATIONS)
        try:
            if self.active_dhikr_toast is not None and self.active_dhikr_toast.winfo_exists():
                self.active_dhikr_toast.destroy()
            self.active_dhikr_toast = show_dhikr_toast(self, message)
        except tk.TclError:
            pass
        self.schedule_dhikr_notification(first=False)

    def configure_dhikr_interval(self) -> None:
        value = simpledialog.askinteger(
            "فاصل الأذكار",
            "اكتب عدد الدقائق بين كل تنبيه:",
            initialvalue=self.dhikr_interval_minutes,
            minvalue=1,
            maxvalue=180,
            parent=self,
        )
        if value is None:
            return
        self.dhikr_interval_minutes = value
        if self.dhikr_notifications_enabled:
            self.schedule_dhikr_notification(first=True)
        self.set_status(f"تم ضبط تنبيهات الأذكار كل {value} دقائق")

    def stop_dhikr_background(self) -> None:
        if self.dhikr_notifications_enabled:
            self.toggle_dhikr_notifications(show_message=False)
        self.show_from_tray()
        self.set_status("تم إيقاف أذكار الخلفية")

    def animate_dhikr(self) -> None:
        self.dhikr_index = (self.dhikr_index + 1) % len(ADHKAR)
        text = ADHKAR[self.dhikr_index]
        self.dhikr_var.set(f"  {text}  ")
        self.after(4500, self.animate_dhikr)

    def request_admin(self) -> None:
        try:
            relaunch_as_admin()
            self.destroy()
        except OSError as exc:
            messagebox.showerror("خطأ", f"تعذر التشغيل كمسؤول:\n{exc}")

    def set_status(self, value: str) -> None:
        self.status_var.set(value)
        self.update_idletasks()

    def refresh_programs(self) -> None:
        self.set_status("جاري قراءة البرامج المثبتة...")
        self.programs = load_programs()
        self.apply_filter()
        self.program_count_var.set(str(len(self.programs)))
        self.set_status(f"تم العثور على {len(self.programs)} برنامج")

    def apply_filter(self) -> None:
        query = normalize_token(self.search_var.get())
        self.filtered = []
        for program in self.programs:
            haystack = normalize_token(f"{program.name} {program.publisher} {program.version}")
            if not query or query in haystack:
                self.filtered.append(program)

        self.filtered.sort(key=self.program_sort_key, reverse=self.sort_desc)

        self.program_tree.delete(*self.program_tree.get_children())
        for index, program in enumerate(self.filtered):
            self.program_tree.insert(
                "",
                tk.END,
                iid=str(index),
                text=program.name,
                values=(format_program_size(program), format_install_date(program), program.publisher, program.version),
            )

    def program_sort_key(self, program: Program) -> tuple[object, ...]:
        if self.sort_column == "size":
            return (program_size_bytes(program), program.name.lower())
        if self.sort_column == "install_date":
            return (install_date_key(program), program.name.lower())
        if self.sort_column == "publisher":
            return ((program.publisher or "").lower(), program.name.lower())
        if self.sort_column == "version":
            return ((program.version or "").lower(), program.name.lower())
        return (program.name.lower(),)

    def apply_sort_choice(self) -> None:
        mapping = {
            "الاسم": ("name", False),
            "الحجم": ("size", True),
            "الناشر": ("publisher", False),
            "الإصدار": ("version", False),
            "آخر تثبيت": ("install_date", True),
        }
        self.sort_column, self.sort_desc = mapping.get(self.sort_var.get(), ("name", False))
        self.apply_filter()

    def sort_by_column(self, column: str) -> None:
        if self.sort_column == column:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_column = column
            self.sort_desc = column in {"size", "install_date"}
        labels = {
            "name": "الاسم",
            "size": "الحجم",
            "publisher": "الناشر",
            "version": "الإصدار",
            "install_date": "آخر تثبيت",
        }
        self.sort_var.set(labels.get(column, "الاسم"))
        self.apply_filter()

    def on_program_select(self) -> None:
        selected = self.program_tree.selection()
        if not selected:
            self.selected_program = None
            return
        self.selected_program = self.filtered[int(selected[0])]
        self.leftovers = []
        self.leftover_tree.delete(*self.leftover_tree.get_children())
        self.leftover_count_var.set("0")
        publisher = self.selected_program.publisher or "ناشر غير معروف"
        version = self.selected_program.version or "بدون رقم إصدار"
        self.selected_name_var.set(self.selected_program.name)
        self.selected_meta_var.set(f"{publisher} • {version}")
        self.selected_path_var.set(f"الحجم: {format_program_size(self.selected_program)} • المسار: {self.selected_program.install_location or 'لا يوجد مسار تثبيت مسجل'}")
        self.render_program_details(self.selected_program)
        self.set_status("تم اختيار برنامج")

    def render_program_details(self, program: Program) -> None:
        self.details_tree.delete(*self.details_tree.get_children())
        rows = [
            ("الحجم", format_program_size(program)),
            ("المسار", program.install_location or "غير مسجل"),
            ("الناشر", program.publisher or "غير معروف"),
            ("الإصدار", program.version or "غير مسجل"),
            ("آخر تثبيت", format_install_date(program)),
            ("أمر الإزالة", uninstall_command(program)),
        ]
        for index, (label, value) in enumerate(rows):
            self.details_tree.insert("", tk.END, iid=str(index), text=label, values=(value,))

    def require_selected_program(self) -> Program | None:
        if self.selected_program is None:
            messagebox.showwarning("تنبيه", "اختر برنامجًا من القائمة أولًا.")
            return None
        return self.selected_program

    def scan_selected(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        self.set_status("جاري فحص البقايا...")
        self.leftovers = find_leftovers(program)
        self.render_leftovers()
        self.leftover_count_var.set(str(len(self.leftovers)))
        self.set_status(f"تم العثور على {len(self.leftovers)} عنصر بقايا محتمل")

    def render_leftovers(self) -> None:
        self.leftover_tree.delete(*self.leftover_tree.get_children())
        for index, item in enumerate(self.leftovers):
            self.leftover_tree.insert(
                "",
                tk.END,
                iid=str(index),
                text=str(item.path),
                values=(format_size(item.size), item.confidence, item.reason),
            )
        self.leftover_count_var.set(str(len(self.leftovers)))

    def uninstall_selected(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        command = uninstall_command(program)
        confirmed = messagebox.askyesno(
            "تأكيد الإزالة",
            f"سيتم تشغيل مزيل التثبيت الرسمي لهذا البرنامج:\n\n{program.name}\n\nالأمر:\n{command}\n\nهل تريد المتابعة؟",
        )
        if not confirmed:
            return

        def worker() -> None:
            self.after(0, self.set_status, "جاري تشغيل مزيل التثبيت...")
            code = run_uninstall(program)
            self.after(0, self.after_uninstall_cleanup, program, code)

        threading.Thread(target=worker, daemon=True).start()

    def after_uninstall_cleanup(self, program: Program, code: int) -> None:
        self.set_status(f"انتهى مزيل التثبيت برمز: {code}. جاري فحص المخلفات والكاش...")
        self.leftovers = find_leftovers(program)
        program_cache = find_program_cache(program)

        self.render_leftovers()

        message = (
            f"انتهت إزالة {program.name}.\n\n"
            f"المخلفات المحتملة: {len(self.leftovers)}\n"
            f"كاش مرتبط بالبرنامج: {len(program_cache)}\n\n"
            "هل تريد تنظيفها الآن؟\n"
            "مخلفات البرنامج ستنتقل إلى مجلد عزل، والكاش سيتم حذفه لأنه ملفات مؤقتة."
        )
        if messagebox.askyesno("تنظيف بعد الإزالة", message):
            moved = quarantine([item.path for item in self.leftovers], program.name)
            cache_count, cache_bytes = clean_program_cache(program)
            temp_count, temp_bytes = clean_temp_cache()
            log_path = write_report(
                {
                    "program": program.name,
                    "uninstall_code": code,
                    "leftovers_found": len(self.leftovers),
                    "leftovers_quarantined": len(moved),
                    "cache_deleted": cache_count + temp_count,
                    "cache_size": format_size(cache_bytes + temp_bytes),
                    "leftovers": [f"{item.path} | {format_size(item.size)} | {item.confidence} | {item.reason}" for item in self.leftovers],
                    "quarantine_paths": moved,
                }
            )
            self.refresh_programs()
            self.leftover_tree.delete(*self.leftover_tree.get_children())
            self.set_status(
                f"تم عزل {len(moved)} مخلف، وحذف {cache_count + temp_count} عنصر كاش ({format_size(cache_bytes + temp_bytes)})"
            )
            messagebox.showinfo(
                "تم التنظيف",
                f"تم عزل المخلفات: {len(moved)}\n"
                f"تم حذف كاش البرنامج والكاش المؤقت: {cache_count + temp_count}\n"
                f"الحجم المحرر تقريبًا: {format_size(cache_bytes + temp_bytes)}\n\n"
                f"مجلد العزل:\n{QUARANTINE_DIR}\n\n"
                f"التقرير:\n{log_path}",
            )
            self.show_report(log_path)
        else:
            self.set_status(f"تم العثور على {len(self.leftovers)} مخلف محتمل. يمكنك عزلها يدويًا.")

    def clean_cache_selected(self) -> None:
        program = self.selected_program
        target = "الكاش المؤقت الآمن"
        if program is not None:
            target = f"كاش {program.name} والكاش المؤقت الآمن"
        confirmed = messagebox.askyesno(
            "تأكيد تنظيف الكاش",
            f"سيتم تنظيف {target}.\n\n"
            "سيتم حذف ملفات مؤقتة قابلة لإعادة الإنشاء فقط، مع تجاهل الملفات الحديثة أو المقفلة.\n\n"
            "هل تريد المتابعة؟",
        )
        if not confirmed:
            return

        def worker() -> None:
            program_count = 0
            program_bytes = 0
            if program is not None:
                program_count, program_bytes = clean_program_cache(program)
            temp_count, temp_bytes = clean_temp_cache()
            self.after(
                0,
                self.set_status,
                f"تم حذف {program_count + temp_count} عنصر كاش ({format_size(program_bytes + temp_bytes)})",
            )

        self.set_status("جاري تنظيف الكاش...")
        threading.Thread(target=worker, daemon=True).start()

    def clean_device_cache_action(self) -> None:
        self.set_status("جاري فحص كاش الجهاز...")

        def worker() -> None:
            items = scan_device_cache()
            total_bytes = sum(item.size for item in items)
            self.after(0, self.confirm_device_cache_clean, items, total_bytes)

        threading.Thread(target=worker, daemon=True).start()

    def confirm_device_cache_clean(self, items: list[CacheItem], total_bytes: int) -> None:
        if not items:
            self.set_status("لم يتم العثور على كاش قابل للتنظيف")
            messagebox.showinfo("تنظيف كاش الجهاز", "لم يتم العثور على عناصر كاش قابلة للتنظيف الآن.")
            return

        preview = "\n".join(
            f"- {item.category}: {format_size(item.size)} | {item.path}"
            for item in items[:12]
        )
        if len(items) > 12:
            preview += f"\n... و {len(items) - 12} عنصر إضافي"

        confirmed = messagebox.askyesno(
            "تنظيف كاش الجهاز",
            f"تم العثور على {len(items)} عنصر كاش.\n"
            f"الحجم التقريبي: {format_size(total_bytes)}\n\n"
            f"{preview}\n\n"
            "سيتم حذف ملفات كاش مؤقتة قابلة لإعادة الإنشاء، وسيتم تجاهل الملفات المقفلة تلقائيًا.\n\n"
            "هل تريد التنظيف الآن؟",
        )
        if not confirmed:
            self.set_status("تم إلغاء تنظيف كاش الجهاز")
            return

        self.set_status("جاري تنظيف كاش الجهاز...")

        def worker() -> None:
            deleted_count, deleted_bytes = clean_device_cache(items)
            self.after(0, self.finish_device_cache_clean, deleted_count, deleted_bytes)

        threading.Thread(target=worker, daemon=True).start()

    def finish_device_cache_clean(self, deleted_count: int, deleted_bytes: int) -> None:
        self.set_status(f"تم تنظيف كاش الجهاز: {deleted_count} عنصر ({format_size(deleted_bytes)})")
        messagebox.showinfo(
            "تم تنظيف كاش الجهاز",
            f"تم حذف {deleted_count} عنصر كاش.\n"
            f"الحجم المحرر تقريبًا: {format_size(deleted_bytes)}",
        )

    def security_scan_selected(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        self.set_status("جاري فحص أمان البرنامج...")

        def worker() -> None:
            findings = scan_program_security(program)
            persistence = scan_persistence(program)
            self.after(0, self.show_security_report, program, findings, persistence)

        threading.Thread(target=worker, daemon=True).start()

    def show_security_report(self, program: Program, findings: list[SecurityFinding], persistence: list[SecurityFinding]) -> None:
        all_findings = sorted([*findings, *persistence], key=lambda item: item.score, reverse=True)
        top_score = max((item.score for item in all_findings), default=0)
        level = level_for_score(top_score)
        self.set_status(f"فحص الأمان: {level} ({top_score}/100)")

        lines = [
            f"{APP_REPORT_NAME} - تقرير فحص أمان محلي",
            "=" * 58,
            f"البرنامج: {program.name}",
            f"الناشر: {program.publisher or 'غير معروف'}",
            f"المسار: {program.install_location or 'غير مسجل'}",
            f"درجة الخطر: {top_score}/100 - {level}",
            f"ملفات/مؤشرات مشبوهة: {len(all_findings)}",
            "",
            "ملاحظة: هذا فحص Heuristic محلي وليس بديلًا كاملًا لمضاد فيروسات.",
            "",
        ]
        if not all_findings:
            lines.append("لم يتم العثور على مؤشرات خطر واضحة في الملفات التي أمكن فحصها.")
        for item in all_findings[:60]:
            lines.extend(
                [
                    f"[{item.level}] {item.score}/100",
                    f"المسار: {item.path}",
                    "الأسباب:",
                    *[f"- {reason}" for reason in item.reasons],
                    "",
                ]
            )

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        report_path = LOG_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}_{safe_filename(program.name)}_security.txt"
        atomic_write_text(report_path, "\n".join(lines), encoding="utf-8")
        self.show_text_window("تقرير فحص الأمان", "\n".join(lines))

    def install_watcher_action(self) -> None:
        path = filedialog.askopenfilename(
            title="اختر ملف التثبيت أو البرنامج للمراقبة",
            filetypes=[("Executable/Installer", "*.exe *.msi *.bat *.cmd"), ("All files", "*.*")],
        )
        if not path:
            return
        confirmed = messagebox.askyesno(
            "مراقبة تثبيت",
            "سيتم أخذ Snapshot قبل التشغيل، ثم تشغيل الملف، ثم أخذ Snapshot بعد انتهاء العملية.\n\nهل تريد المتابعة؟",
        )
        if not confirmed:
            return
        self.set_status("مراقبة التثبيت: Snapshot قبل التشغيل...")

        def worker() -> None:
            before = install_snapshot()
            result = launch_and_wait(path)
            time.sleep(5)
            after = install_snapshot()
            lines = [
                f"{APP_REPORT_NAME} - Install Black Box",
                "=" * 55,
                f"الملف: {path}",
                f"الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "نتيجة تشغيل المثبت",
                "-" * 24,
                result.text(),
                *diff_install_snapshots(before, after),
            ]
            self.after(0, self.finish_install_watcher, "\n".join(lines))

        threading.Thread(target=worker, daemon=True).start()

    def finish_install_watcher(self, content: str) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        path = LOG_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}_install_black_box.txt"
        atomic_write_text(path, content, encoding="utf-8")
        self.set_status("انتهت مراقبة التثبيت")
        self.show_text_window("Install Black Box", content)

    def connection_watch_action(self) -> None:
        self.set_status("جاري فحص الاتصالات الحالية...")

        def worker() -> None:
            items = scan_connections()
            lines = [
                f"{APP_REPORT_NAME} - Connection Watch",
                "=" * 55,
                f"الاتصالات الحالية: {len(items)}",
                "",
            ]
            for item in items[:250]:
                lines.append(f"{item.process} | PID {item.pid} | {item.protocol} | {item.local} -> {item.remote} | {item.state}")
            self.after(0, self.show_text_window, "Connection Watch", "\n".join(lines))
            self.after(0, self.set_status, f"تم العثور على {len(items)} اتصال")

        threading.Thread(target=worker, daemon=True).start()

    def startup_hunter_action(self) -> None:
        self.set_status("جاري فحص عناصر التشغيل التلقائي...")

        def worker() -> None:
            rows = startup_hunter_rows()
            services = list_services()
            high = sum(1 for row in rows if int(row["score"]) >= 75)
            suspicious = sum(1 for row in rows if 45 <= int(row["score"]) < 75)
            review = sum(1 for row in rows if 20 <= int(row["score"]) < 45)
            low = sum(1 for row in rows if int(row["score"]) < 20)
            lines = [
                f"{APP_REPORT_NAME} - Startup Hunter",
                "=" * 55,
                f"العناصر المفحوصة: {len(rows)}",
                f"خطر: {high} | مشبوه: {suspicious} | مراجعة: {review} | منخفض: {low}",
                f"Services: {len(services)}",
                "",
                "العناصر مرتبة حسب درجة الخطر",
                "-" * 35,
            ]
            for row in rows[:300]:
                lines.extend(
                    [
                        f"[{row['level']}] {row['score']}/100 | {row['type']}",
                        f"المفتاح: {row['key']}",
                        f"الأمر: {row['command']}",
                        "الأسباب التقنية:",
                        *[f"- {reason}" for reason in row["reasons"]],
                        "",
                    ]
                )
            lines.extend(["", "Services Sample", "-" * 20])
            lines.extend(sorted(services)[:300])
            self.after(0, self.show_text_window, "Startup Hunter", "\n".join(lines))
            self.after(0, self.set_status, "انتهى Startup Hunter")

        threading.Thread(target=worker, daemon=True).start()

    def portable_folder_scan_action(self) -> None:
        folder = filedialog.askdirectory(title="اختر مجلدًا لفحص البرامج المحمولة")
        if not folder:
            return
        self.set_status("جاري فحص المجلد...")

        def worker() -> None:
            findings = scan_folder_security(Path(folder))
            lines = [
                f"{APP_REPORT_NAME} - Portable Folder Scanner",
                "=" * 60,
                f"المجلد: {folder}",
                f"المؤشرات: {len(findings)}",
                "",
            ]
            if not findings:
                lines.append("لم يتم العثور على مؤشرات خطر واضحة.")
            for item in findings[:120]:
                lines.append(f"[{item.level}] {item.score}/100 | {item.path}")
                lines.extend(f"- {reason}" for reason in item.reasons)
                lines.append("")
            self.after(0, self.show_text_window, "فحص مجلد محمول", "\n".join(lines))
            self.after(0, self.set_status, f"انتهى فحص المجلد: {len(findings)} مؤشر")

        threading.Thread(target=worker, daemon=True).start()

    def health_report_action(self) -> None:
        self.set_status("جاري إعداد تقرير صحة الجهاز...")

        def worker() -> None:
            programs = load_programs()
            cache_items = scan_device_cache()
            connections = scan_connections()
            startup = list_startup_items()
            largest = sorted(programs, key=program_size_bytes, reverse=True)[:20]
            lines = [
                f"{APP_REPORT_NAME} - One Click Health Report",
                "=" * 60,
                f"البرامج المثبتة: {len(programs)}",
                f"عناصر Startup: {len(startup)}",
                f"الاتصالات الحالية: {len(connections)}",
                f"عناصر الكاش القابلة للتنظيف: {len(cache_items)}",
                f"حجم الكاش التقريبي: {format_size(sum(item.size for item in cache_items))}",
                "",
                "أكبر البرامج",
                "-" * 20,
            ]
            for program in largest:
                lines.append(f"{program.name} | {format_program_size(program)} | {program.publisher or 'غير معروف'}")
            lines.extend(["", "أكثر اتصالات ظاهرة", "-" * 20])
            for item in connections[:50]:
                lines.append(f"{item.process} | {item.remote} | {item.state}")
            self.after(0, self.show_text_window, "تقرير صحة الجهاز", "\n".join(lines))
            self.after(0, self.set_status, "تم إعداد تقرير صحة الجهاز")

        threading.Thread(target=worker, daemon=True).start()

    def behavior_monitor_action(self) -> None:
        messagebox.showinfo("مراقبة سلوك", "سيتم أخذ لقطة الآن، ثم لقطة ثانية بعد 60 ثانية، ثم عرض التغييرات.")
        self.set_status("مراقبة السلوك لمدة 60 ثانية...")

        def worker() -> None:
            before = behavior_snapshot()
            time.sleep(60)
            after = behavior_snapshot()
            lines = [
                f"{APP_REPORT_NAME} - Behavior Monitor",
                "=" * 58,
                f"المدة: 60 ثانية",
                f"الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                *diff_behavior_snapshots(before, after),
            ]
            self.after(0, self.show_text_window, "مراقبة السلوك", "\n".join(lines))
            self.after(0, self.set_status, "انتهت مراقبة السلوك")

        threading.Thread(target=worker, daemon=True).start()

    def hash_baseline_action(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        self.set_status("جاري حساب بصمات البرنامج...")

        def worker() -> None:
            hashes, changes = compare_program_hashes(program)
            lines = [
                f"{APP_REPORT_NAME} - Hash Baseline",
                "=" * 55,
                f"البرنامج: {program.name}",
                f"عدد الملفات المبصمة: {len(hashes)}",
                f"التغييرات منذ آخر بصمة: {len(changes)}",
                "",
                "التغييرات",
                "-" * 20,
                *(changes or ["لا يوجد تغييرات أو هذه أول بصمة محفوظة."]),
                "",
                "البصمات",
                "-" * 20,
            ]
            lines.extend(f"{digest} | {path}" for path, digest in list(hashes.items())[:220])
            self.after(0, self.show_text_window, "بصمات Hash", "\n".join(lines))
            self.after(0, self.set_status, "تم تحديث بصمات البرنامج")

        threading.Thread(target=worker, daemon=True).start()

    def quarantine_center_action(self) -> None:
        lines = [
            f"{APP_REPORT_NAME} - مركز العزل",
            "=" * 46,
            *quarantine_summary_lines(),
            "",
            "الأزرار المتاحة حاليًا: استرجاع آخر عزل من الواجهة الرئيسية، أو فتح مجلد العزل.",
            f"مجلد العزل: {QUARANTINE_DIR}",
        ]
        self.show_text_window("مركز العزل", "\n".join(lines))

    def forensics_report_action(self) -> None:
        self.set_status("جاري إعداد تقرير Forensics...")

        def worker() -> None:
            hosts = scan_hosts_file()
            firewall = scan_firewall_rules()
            wmi = scan_wmi_persistence()
            extensions = scan_browser_extensions()
            startup = startup_hunter_rows()
            lines = [
                f"{APP_REPORT_NAME} - Forensics Report",
                "=" * 56,
                f"Hosts entries: {len(hosts)}",
                f"Firewall rules sampled: {len(firewall)}",
                f"WMI persistence consumers: {len(wmi)}",
                f"Browser extensions: {len(extensions)}",
                f"Startup risk rows: {len(startup)}",
                "",
                "Hosts",
                "-" * 20,
                *(hosts or ["لا يوجد entries غير تعليقات"]),
                "",
                "WMI Persistence",
                "-" * 20,
                *(wmi or ["لا يوجد مؤشرات WMI واضحة"]),
                "",
                "Browser Extensions",
                "-" * 20,
                *(extensions[:180] or ["لا يوجد إضافات مكتشفة"]),
                "",
                "Firewall Rules Sample",
                "-" * 20,
                *(firewall[:180] or ["لا توجد بيانات"]),
            ]
            self.after(0, self.show_text_window, "Forensics", "\n".join(lines))
            self.after(0, self.set_status, "تم إعداد تقرير Forensics")

        threading.Thread(target=worker, daemon=True).start()

    def smart_scan_action(self) -> None:
        self.set_status("جاري الفحص الذكي الشامل...")

        def worker() -> None:
            cache_items = scan_device_cache()
            startup_rows = startup_hunter_rows()
            services = service_risk_rows()
            tasks = scheduled_task_detail_rows()
            connections = scan_connections()
            updates = winget_upgrade_report()
            lines = [
                f"{APP_REPORT_NAME} - Smart Scan",
                "=" * 52,
                f"كاش قابل للتنظيف: {len(cache_items)} عنصر | {format_size(sum(item.size for item in cache_items))}",
                f"Startup مرتفع/مشبوه: {sum(1 for row in startup_rows if int(row['score']) >= 45)}",
                f"Services تحتاج مراجعة: {sum(1 for row in services if int(row['score']) >= 45)}",
                f"Tasks تحتاج مراجعة: {sum(1 for row in tasks if int(row['score']) >= 45)}",
                f"اتصالات حالية: {len(connections)}",
                "",
                "أعلى مخاطر بدء التشغيل",
                "-" * 28,
            ]
            for row in startup_rows[:20]:
                lines.append(f"[{row['level']}] {row['score']}/100 | {row['key']} | {row['command']}")
            lines.extend(["", "أعلى مخاطر الخدمات", "-" * 24])
            for row in services[:20]:
                lines.append(f"[{row['level']}] {row['score']}/100 | {row['name']} | {row['image']}")
            lines.extend(["", "تحديثات التطبيقات عبر winget", "-" * 30, updates])
            self.after(0, self.show_text_window, "الفحص الذكي", "\n".join(lines))
            self.after(0, self.set_status, "انتهى الفحص الذكي")

        threading.Thread(target=worker, daemon=True).start()

    def software_updates_action(self) -> None:
        self.set_status("جاري جلب تحديثات التطبيقات عبر winget...")

        def worker() -> None:
            report = winget_upgrade_report()
            self.after(0, self.confirm_software_updates, report)

        threading.Thread(target=worker, daemon=True).start()

    def confirm_software_updates(self, report: str) -> None:
        self.show_text_window("تحديثات التطبيقات", report)
        if "No installed package found" in report or "لا توجد" in report or "غير متوفر" in report:
            self.set_status("لا توجد تحديثات واضحة")
            return
        confirmed = messagebox.askyesno(
            "تحديث التطبيقات",
            "تم عرض التحديثات المتاحة من winget.\n\nهل تريد تشغيل تحديث كل التطبيقات المتاحة الآن؟",
        )
        if not confirmed:
            self.set_status("تم عرض التحديثات بدون تنفيذ")
            return

        def worker() -> None:
            output = run_winget_upgrade_all()
            self.after(0, self.show_text_window, "نتيجة تحديث التطبيقات", output)
            self.after(0, self.set_status, "انتهى تحديث التطبيقات")

        self.set_status("جاري تحديث التطبيقات عبر winget...")
        threading.Thread(target=worker, daemon=True).start()

    def dns_watch_action(self) -> None:
        lines = [
            f"{APP_REPORT_NAME} - DNS Watch",
            "=" * 45,
            *dns_cache_lines(),
        ]
        self.show_text_window("DNS Watch", "\n".join(lines))

    def guardian_toggle_action(self) -> None:
        self.guardian_enabled = not self.guardian_enabled
        if self.guardian_enabled:
            self.guardian_startup_baseline = list_startup_items()
            self.set_status("تم تشغيل الحارس")
            self.after(60000, self.guardian_tick)
            messagebox.showinfo("الحارس", "تم تشغيل مراقبة دورية لعناصر بدء التشغيل كل دقيقة أثناء فتح البرنامج.")
        else:
            self.set_status("تم إيقاف الحارس")

    def guardian_tick(self) -> None:
        if not self.guardian_enabled:
            return
        current = list_startup_items()
        added = sorted(set(current) - set(self.guardian_startup_baseline))
        changed = sorted(key for key in set(current) & set(self.guardian_startup_baseline) if current[key] != self.guardian_startup_baseline[key])
        if added or changed:
            lines = ["تغييرات بدء التشغيل المكتشفة:", ""]
            if added:
                lines.extend(["عناصر جديدة:", *[f"{key} -> {current[key]}" for key in added], ""])
            if changed:
                lines.extend(["عناصر تغير أمرها:", *[f"{key}\nقبل: {self.guardian_startup_baseline[key]}\nبعد: {current[key]}" for key in changed]])
            content = "\n".join(lines)
            self.show_text_window("تنبيه الحارس", content)
            self.guardian_startup_baseline = current
        self.after(60000, self.guardian_tick)

    def snapshot_action(self) -> None:
        choice = messagebox.askyesno("Snapshot", "نعم = حفظ Snapshot جديدة.\nلا = مقارنة مع Snapshot السابقة.")
        self.set_status("جاري معالجة Snapshot...")

        def worker() -> None:
            if choice:
                path = save_system_snapshot()
                self.after(0, self.set_status, "تم حفظ Snapshot")
                self.after(0, self.show_text_window, "Snapshot", f"تم حفظ Snapshot:\n{path}")
            else:
                lines = compare_saved_snapshot()
                self.after(0, self.show_text_window, "مقارنة Snapshot", "\n".join(lines))
                self.after(0, self.set_status, "تمت مقارنة Snapshot")

        threading.Thread(target=worker, daemon=True).start()

    def allow_block_center_action(self) -> None:
        settings = load_settings()
        program = self.selected_program
        if program is not None:
            if program.publisher and messagebox.askyesno("قائمة السماح", f"إضافة الناشر لقائمة السماح؟\n{program.publisher}"):
                if program.publisher not in settings["allow_publishers"]:
                    settings["allow_publishers"].append(program.publisher)
            if program.install_location and messagebox.askyesno("قائمة السماح", f"إضافة مسار البرنامج لقائمة السماح؟\n{program.install_location}"):
                if program.install_location not in settings["allow_paths"]:
                    settings["allow_paths"].append(program.install_location)
            save_settings(settings)
        lines = [
            f"{APP_REPORT_NAME} - Allow / Block",
            "=" * 48,
            f"ملف الإعدادات: {SETTINGS_PATH}",
            "",
            json.dumps(settings, ensure_ascii=False, indent=2),
        ]
        self.show_text_window("السماح والحظر", "\n".join(lines))

    def disable_risky_startup_action(self) -> None:
        if not messagebox.askyesno("تعطيل بدء التشغيل", "سيتم تعطيل عناصر Startup ذات درجة خطر 45 أو أعلى فقط، مع حفظ إمكانية الاسترجاع.\n\nهل تريد المتابعة؟"):
            return
        count, messages = disable_risky_startup()
        self.show_text_window("تعطيل بدء التشغيل", "\n".join([f"تم تعطيل {count} عنصر.", "", *messages]))

    def restore_disabled_startup_action(self) -> None:
        count, messages = restore_disabled_startup()
        self.show_text_window("استرجاع بدء التشغيل", "\n".join([f"تم استرجاع {count} عنصر.", "", *messages]))

    def advanced_clean_action(self) -> None:
        self.set_status("جاري فحص عناصر التنظيف المتقدم...")

        def worker() -> None:
            cache_items = scan_device_cache()
            privacy_items = scan_privacy_items()
            total = sum(item.size for item in cache_items) + sum(item.size for item in privacy_items)
            self.after(0, self.confirm_advanced_clean, cache_items, privacy_items, total)

        threading.Thread(target=worker, daemon=True).start()

    def confirm_advanced_clean(self, cache_items: list[CacheItem], privacy_items: list[CacheItem], total: int) -> None:
        preview = [
            f"كاش النظام/المتصفحات: {len(cache_items)} عنصر",
            f"خصوصية/Recent/Jump Lists: {len(privacy_items)} عنصر",
            f"الحجم التقريبي: {format_size(total)}",
            "",
            "سيتم تنظيف العناصر المؤقتة والخصوصية، ويمكن اختيار تفريغ سلة المحذوفات أيضًا.",
        ]
        if not messagebox.askyesno("تنظيف متقدم", "\n".join(preview) + "\n\nهل تريد المتابعة؟"):
            self.set_status("تم إلغاء التنظيف المتقدم")
            return
        clean_recycle = messagebox.askyesno("سلة المحذوفات", "هل تريد تفريغ سلة المحذوفات أيضًا؟")
        self.set_status("جاري التنظيف المتقدم...")

        def worker() -> None:
            cache_count, cache_bytes = clean_device_cache(cache_items)
            privacy_count, privacy_bytes = clean_privacy_items(privacy_items)
            recycle_ok = empty_recycle_bin() if clean_recycle else False
            lines = [
                f"{APP_REPORT_NAME} - Advanced Clean",
                "=" * 52,
                f"كاش محذوف: {cache_count} عنصر | {format_size(cache_bytes)}",
                f"خصوصية محذوفة: {privacy_count} عنصر | {format_size(privacy_bytes)}",
                f"سلة المحذوفات: {'تم تفريغها' if recycle_ok else 'لم يتم تفريغها أو لم تُطلب'}",
                f"الإجمالي التقريبي: {format_size(cache_bytes + privacy_bytes)}",
            ]
            self.after(0, self.show_text_window, "تنظيف متقدم", "\n".join(lines))
            self.after(0, self.set_status, "انتهى التنظيف المتقدم")

        threading.Thread(target=worker, daemon=True).start()

    def settings_import_export_action(self) -> None:
        if messagebox.askyesno("استيراد/تصدير", "نعم = تصدير الإعدادات.\nلا = استيراد إعدادات."):
            target = filedialog.asksaveasfilename(
                title="تصدير الإعدادات",
                defaultextension=".json",
                filetypes=[("JSON", "*.json")],
                initialfile="niqaa_settings.json",
            )
            if not target:
                return
            atomic_write_json(Path(target), load_settings())
            self.show_text_window("تصدير الإعدادات", f"تم تصدير الإعدادات إلى:\n{target}")
            return

        source = filedialog.askopenfilename(title="استيراد الإعدادات", filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if not source:
            return
        try:
            data = json.loads(Path(source).read_text(encoding="utf-8"))
            settings = default_settings()
            for key in settings:
                value = data.get(key, [])
                if isinstance(value, list):
                    settings[key] = [str(item) for item in value]
            save_settings(settings)
            self.show_text_window("استيراد الإعدادات", f"تم استيراد الإعدادات من:\n{source}")
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("خطأ", f"تعذر استيراد الإعدادات:\n{exc}")

    def show_text_window(self, title: str, content: str) -> None:
        try:
            report_path = write_html_report(title, content)
            content = f"{content}\n\nHTML Report:\n{report_path}"
        except OSError:
            pass
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("860x620")
        text = tk.Text(window, wrap=tk.WORD, font=("Segoe UI", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        text.insert("1.0", content)
        text.configure(state=tk.DISABLED)

    def clean_selected_leftovers(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        selected = self.leftover_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر عنصرًا واحدًا أو أكثر من البقايا.")
            return
        paths = [self.leftovers[int(item)].path for item in selected]
        confirmed = messagebox.askyesno(
            "تأكيد العزل",
            "سيتم نقل العناصر المحددة إلى مجلد عزل على سطح المكتب بدل حذفها نهائيًا.\n\nهل تريد المتابعة؟",
        )
        if not confirmed:
            return

        try:
            moved = quarantine(paths, program.name)
            write_report(
                {
                    "program": program.name,
                    "uninstall_code": "لم يتم تشغيل مزيل التثبيت",
                    "leftovers_found": len(self.leftovers),
                    "leftovers_quarantined": len(moved),
                    "cache_deleted": 0,
                    "cache_size": "0 B",
                    "leftovers": [str(path) for path in paths],
                    "quarantine_paths": moved,
                }
            )
            self.scan_selected()
            messagebox.showinfo("تم", f"تم عزل {len(moved)} عنصر.\n\nالمجلد:\n{QUARANTINE_DIR}")
        except OSError as exc:
            messagebox.showerror("خطأ", f"تعذر عزل بعض الملفات:\n{exc}")

    def open_quarantine(self) -> None:
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
        os.startfile(str(QUARANTINE_DIR))

    def restore_last_quarantine(self) -> None:
        confirmed = messagebox.askyesno(
            "استرجاع آخر عزل",
            "سيتم استرجاع آخر مجموعة ملفات تم عزلها إلى مساراتها الأصلية إذا كانت المسارات فارغة.\n\nهل تريد المتابعة؟",
        )
        if not confirmed:
            return
        try:
            restored, manifest_path = restore_latest_quarantine()
            if manifest_path is None:
                messagebox.showinfo("لا يوجد عزل", "لم أجد ملفات عزل قابلة للاسترجاع.")
                return
            messagebox.showinfo("تم الاسترجاع", f"تم استرجاع {restored} عنصر.\n\nالملف المرجعي:\n{manifest_path}")
            self.set_status(f"تم استرجاع {restored} عنصر من آخر عزل")
        except OSError as exc:
            messagebox.showerror("خطأ", f"تعذر الاسترجاع:\n{exc}")

    def show_program_menu(self, event: tk.Event) -> None:
        row_id = self.program_tree.identify_row(event.y)
        if row_id:
            self.program_tree.selection_set(row_id)
            self.on_program_select()

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="إزالة كاملة", command=self.uninstall_selected)
        menu.add_command(label="فحص البقايا", command=self.scan_selected)
        menu.add_command(label="فحص أمان", command=self.security_scan_selected)
        menu.add_command(label="تنظيف الكاش", command=self.clean_cache_selected)
        menu.add_separator()
        menu.add_command(label="فتح مسار التثبيت", command=self.open_selected_install_location)
        menu.add_command(label="نسخ اسم البرنامج", command=self.copy_selected_program_name)
        menu.tk_popup(event.x_root, event.y_root)

    def show_leftover_menu(self, event: tk.Event) -> None:
        row_id = self.leftover_tree.identify_row(event.y)
        if row_id:
            self.leftover_tree.selection_set(row_id)

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="عزل المحدد", command=self.clean_selected_leftovers)
        menu.add_command(label="تحديد كل البقايا", command=self.select_all_leftovers)
        menu.add_separator()
        menu.add_command(label="فتح المسار", command=self.open_selected_leftover_location)
        menu.add_command(label="نسخ المسار", command=self.copy_selected_leftover_path)
        menu.tk_popup(event.x_root, event.y_root)

    def open_selected_install_location(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        if not program.install_location or not Path(program.install_location).exists():
            messagebox.showwarning("غير متاح", "لا يوجد مسار تثبيت صالح لهذا البرنامج.")
            return
        os.startfile(program.install_location)

    def copy_selected_program_name(self) -> None:
        program = self.require_selected_program()
        if program is None:
            return
        self.clipboard_clear()
        self.clipboard_append(program.name)
        self.set_status("تم نسخ اسم البرنامج")

    def select_all_leftovers(self) -> None:
        self.leftover_tree.selection_set(self.leftover_tree.get_children())

    def selected_leftover_item(self) -> LeftoverItem | None:
        selected = self.leftover_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر مخلفًا من القائمة أولًا.")
            return None
        return self.leftovers[int(selected[0])]

    def open_selected_leftover_location(self) -> None:
        item = self.selected_leftover_item()
        if item is None:
            return
        target = item.path if item.path.is_dir() else item.path.parent
        if target.exists():
            os.startfile(str(target))

    def copy_selected_leftover_path(self) -> None:
        item = self.selected_leftover_item()
        if item is None:
            return
        self.clipboard_clear()
        self.clipboard_append(str(item.path))
        self.set_status("تم نسخ المسار")

    def show_report(self, log_path: Path) -> None:
        if not log_path.exists():
            return
        window = tk.Toplevel(self)
        window.title("تقرير العملية")
        window.geometry("760x520")
        text = tk.Text(window, wrap=tk.WORD, font=("Segoe UI", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        text.insert("1.0", log_path.read_text(encoding="utf-8"))
        text.configure(state=tk.DISABLED)


def main() -> None:
    ensure_app_dirs()
    app = RootUninstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
