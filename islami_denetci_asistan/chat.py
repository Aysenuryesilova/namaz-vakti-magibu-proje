

import sys
import config
import ollama_client
import tools
import islamic_rag

def run_tool_calls(tool_calls: list[dict]) -> list[dict]:
    """Modelin dinamik olarak çağırmak istediği araçları çalıştırır."""
    messages = []
    for call in tool_calls:
        name = call["function"]["name"]
        arguments = call["function"].get("arguments") or {}
        print(f"\n  🔧 [ARAÇ ÇAĞRILDI]: {name}({arguments})")

        function = tools.TOOLS.get(name)
        if function is None:
            output = f"'{name}' adında bir araç bulunamadı."
        else:
            try:
                output = function(**arguments)
            except Exception as exc:
                output = f"Araç çalıştırılamadı: {exc}"

        print(f"  📥 [ARAÇ ÇIKTISI]:\n{output}\n")
        messages.append({"role": "tool", "content": str(output)})
    return messages

def main():
    print("==================================================================")
    print("  İSLAMİ UYGULAMA DOĞRULUK & KAYNAK DENETÇİSİ (EZAN VAKTİ AGENT)")
    print("==================================================================")
    print(f"  • Sohbet Modeli : {config.CHAT_MODEL}")
    print(f"  • Ollama Adresi : {config.OLLAMA_HOST}")
    print("  • Çıkmak için   : 'çık' veya 'exit' yazın\n")

    # RAG Veritabanı Kurulumu
    try:
        islamic_rag.seed_knowledge_base()
    except Exception as e:
        print(f"  [Not: RAG ilk yükleme: {e}]")

    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("Geliştirici/Kullanıcı > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nÇıkış yapılıyor...")
            break

        if not user_input:
            continue
        if user_input.lower() in {"çık", "cik", "exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})

        try:
            # ReAct Döngüsü: Model araç çağırır, biz sonucu veririz, model cevabı tamamlar.
            for round_num in range(config.MAX_TOOL_ROUNDS):
                response_msg = ollama_client.chat(
                    messages=messages,
                    model=config.CHAT_MODEL,
                    tools=tools.TOOL_SCHEMAS
                )
                messages.append(response_msg)

                tool_calls = response_msg.get("tool_calls")
                if not tool_calls:
                    break

                tool_messages = run_tool_calls(tool_calls)
                messages.extend(tool_messages)

            final_answer = (response_msg.get("content") or "").strip()
            print(f"\n🤖 Denetçi Asistan >\n{final_answer}\n")
            print("-" * 65)

        except Exception as exc:
            print(f"\nHata oluştu: {exc}\n")

if __name__ == "__main__":
    main()
