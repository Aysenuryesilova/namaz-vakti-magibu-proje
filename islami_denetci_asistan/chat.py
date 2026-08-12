"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - RENKLİ TERMINAL ARAYÜZÜ (CHAT.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. CLI (Command Line Interface / Komut Satırı Arayüzü):
   Kullanıcının terminal/komut satırı üzerinden asistanla canlı sohbet etmesini
   sağlayan ana çalışma girişidir (Entry Point).

2. Rich Kütüphanesi & Görsellik:
   `rich` kütüphanesi kullanılarak konsol panelleri, renkli araç çağrı kutuları
   ve biçimlendirilmiş çıktılar (Markdown) üretilir.

3. UTF-8 Standardizasyonu:
   Windows locale ortamlarında Türkçe karakter ve emoji basarken oluşan
   'UnicodeEncodeError' hatalarını önlemek için `sys.stdout.reconfigure` kullanır.
==============================================================================
"""

import sys
import os

# Windows konsolunda Türkçe karakter ve emoji desteğini garantileme
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stdin and hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")

from agent_engine import IslamicAgentEngine

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

console = Console() if RICH_AVAILABLE else None

def print_header():
    """Uygulama açılış başlığını ve bilgi panelini basar."""
    if RICH_AVAILABLE:
        header_text = (
            "[bold green]🕌 İSLAMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ (EZAN VAKTİ AGENT)[/bold green]\n"
            "[cyan]Local LLM (Qwen2.5:3b) + Tool Calling + Vector RAG + SQLite DB + Web Search[/cyan]\n"
            "[yellow]Çıkmak için 'çık' veya 'exit' | Hafızayı sıfırlamak için 'temizle' veya 'reset' yazın.[/yellow]"
        )
        console.print(Panel(header_text, title="✨ Magibu Proje Seviye 5 Asistanı", border_style="bright_blue"))
    else:
        print("=== İSLAMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ ===")

def main():
    """Terminal sohbet ana döngüsü (CLI Loop)."""
    engine = IslamicAgentEngine()
    print_header()

    while True:
        try:
            user_input = input("\nKullanıcı > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["çık", "exit", "quit"]:
            print("Güle güle! Hayırlı günler dileriz.")
            break

        if user_input.lower() in ["temizle", "reset", "clear"]:
            engine.clear_memory()
            if RICH_AVAILABLE:
                console.print("[bold yellow]🧹 Sohbet geçmişi ve hafıza temizlendi![/bold yellow]")
            else:
                print("Sohbet geçmişi temizlendi.")
            continue

        # Agent Engine Yürütme
        final_ans, trace_logs, _ = engine.run(user_input)

        # Çağrılan Araçların Loglarını Ekrana Basma
        for log in trace_logs:
            tool_msg = f"🔧 [ARAÇ ÇAĞRILDI]: {log['tool_name']}({log['arguments']})"
            if RICH_AVAILABLE:
                console.print(f"  [bold yellow]{tool_msg}[/bold yellow]")
                console.print(Panel(str(log['response'])[:300] + "...", title="📥 Araç Çıktısı", border_style="yellow"))
            else:
                print(f"  {tool_msg}")

        # Nihai Yanıtı Ekrana Basma
        print("\n🤖 Denetçi Asistan >")
        if RICH_AVAILABLE:
            console.print(Markdown(final_ans))
        else:
            print(final_ans)
        print("-" * 65)

if __name__ == "__main__":
    main()
