"""
==============================================================================
İSLÂMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ CLI TERMINAL ARAYÜZÜ (CHAT.PY)
==============================================================================
Bu dosya:
1. Zengin Terminal (CLI - Rich kütüphanesi) üzerinden kullanıcı ile etkileşime geçer.
2. Tool call adımlarını, parametrelerini ve renkli trace logları canlı basar.
"""

import sys
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from agent_engine import IslamicAgentEngine
from database import get_all_inquiries

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

def print_banner():
    if RICH_AVAILABLE:
        console.print(Panel.fit(
            "[bold green]🕌 İSLAMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ (EZAN VAKTİ AGENT)[/bold green]\n"
            "[cyan]Local LLM (Qwen2.5:3b) + Tool Calling + RAG + SQLite DB + DuckDuckGo Web Search[/cyan]\n"
            "[yellow]Çıkmak için 'çık' veya 'exit' yazın.[/yellow]",
            title="  İSLAMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ (EZAN VAKTİ AGENT)",
            border_style="green"
        ))
    else:
        print("==================================================================")
        print("  Local LLM (Qwen2.5:3b) + Tool Calling + RAG + SQLite DB")
        print("  Çıkmak için 'çık' veya 'exit' yazın.")
        print("==================================================================")

def main():
    parser = argparse.ArgumentParser(description="İslami Denetçi Asistan CLI Arayüzü")
    parser.add_argument("--query", type=str, help="Tek bir soru sorup çıkmak için")
    args = parser.parse_args()

    engine = IslamicAgentEngine()
    print_banner()

    if args.query:
        print(f"\n👤 Kullanıcı > {args.query}")
        ans, logs, prompt = engine.run(args.query)
        if logs:
            for log in logs:
                print(f"\n  🔧 [TOOL CALL]: {log['tool_name']}({log['arguments']})")
                print(f"  📥 [RESULT]:\n{log['response']}")
        if RICH_AVAILABLE:
            console.print("\n🤖 [bold green]Denetçi Asistan >[/bold green]")
            console.print(Markdown(ans))
        else:
            print(f"\n🤖 Denetçi Asistan >\n{ans}")
        return

    while True:
        try:
            if RICH_AVAILABLE:
                user_input = console.input("\n[bold cyan]Kullanıcı > [/bold cyan]").strip()
            else:
                user_input = input("\nKullanıcı > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        if not user_input:
            continue
        if user_input.lower() in {"çık", "cik", "exit", "quit"}:
            print("Görüşmek üzere!")
            break

        ans, logs, prompt = engine.run(user_input)

        if logs:
            for log in logs:
                if RICH_AVAILABLE:
                    console.print(f"\n  [bold yellow]🔧 [ARAÇ ÇAĞRILDI]:[/bold yellow] [bold white]{log['tool_name']}[/bold white]({log['arguments']})")
                    console.print(Panel(str(log['response']), title="📥 Araç Çıktısı", border_style="yellow"))
                else:
                    print(f"\n  🔧 [ARAÇ ÇAĞRILDI]: {log['tool_name']}({log['arguments']})")
                    print(f"  📥 [ARAÇ ÇİKİTİSİ]:\n{log['response']}\n")

        if RICH_AVAILABLE:
            console.print("\n🤖 [bold green]Denetçi Asistan >[/bold green]")
            console.print(Markdown(ans))
            console.print("[dim]" + "-" * 65 + "[/dim]")
        else:
            print(f"\n🤖 Denetçi Asistan >\n{ans}\n")
            print("-" * 65)

if __name__ == "__main__":
    main()
