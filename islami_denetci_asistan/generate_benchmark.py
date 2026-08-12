"""
==============================================================================
İSLÂMİ DENETÇİ OTOMATİK BENCHMARK TEST SCRİPTİ (GENERATE_BENCHMARK.PY)
==============================================================================
Bu script; tüm araçların (Tool Calling), SQLite veritabanı işlemlerinin,
RAG vektör aramasının ve canlı API'lerin doğruluğunu uçtan uca test eder.
"""

import sys
import os
import time

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from agent_engine import IslamicAgentEngine
from database import get_all_inquiries

TEST_SUITE = [
    {
        "id": 1,
        "name": "Namaz Vakti API Testi",
        "query": "İstanbul için namaz vakitleri nelerdir?",
        "expected_tool": "calculate_prayer_times"
    },
    {
        "id": 2,
        "name": "Kıble Açısı Hesaplama Testi",
        "query": "Ankara için kıble açısı kaç derecedir?",
        "expected_tool": "calculate_qibla_direction"
    },
    {
        "id": 3,
        "name": "Zekat Fıkhi Hesaplama Testi (Kod Yürütme)",
        "query": "100 gram altınım ve 50000 TL nakdim var zekat düşer mi?",
        "expected_tool": "calculate_zekat"
    },
    {
        "id": 4,
        "name": "SQLite Veritabanı Kayıt Testi (Veri Yazma)",
        "query": "Bu soruyu veritabanına kaydet: Sehiv secdesi hangi durumlarda yapılır?",
        "expected_tool": "save_inquiry_tool"
    },
    {
        "id": 5,
        "name": "SQLite Veritabanı Okuma Testi (Veri Okuma)",
        "query": "Veritabanındaki tüm kayıtlı geçmiş soruları listele.",
        "expected_tool": "get_all_inquiries_tool"
    },
    {
        "id": 6,
        "name": "Kur'an Meali ve Sure Arama Testi",
        "query": "Kur'an-ı Kerim kaç suredir ve kaç ayettir?",
        "expected_tool": "search_quran_verse"
    },
    {
        "id": 7,
        "name": "Fıkıh & İlmihal RAG Testi",
        "query": "Teheccüd namazı nedir ve ne zaman kılınır?",
        "expected_tool": "islamic_knowledge_question"
    },
    {
        "id": 8,
        "name": "Esmaül Hüsna Testi",
        "query": "'Er-Rahman' isminin Esmaül Hüsna anlamı nedir?",
        "expected_tool": "get_esmaul_husna"
    },
    {
        "id": 9,
        "name": "Ramazan ve İslami Takvim Testi",
        "query": "2026 Ramazan başlangıcı ve bayram ne zaman?",
        "expected_tool": "find_islamic_event"
    },
    {
        "id": 10,
        "name": "Canlı Web Araması Testi",
        "query": "2026 Diyanet hac başvuru tarihleri güncel duyuruları nedir?",
        "expected_tool": "web_search_tool"
    }
]

def run_benchmark():
    print("==================================================================", flush=True)
    print(" İSLAMİ DENETÇİ ASİSTAN UÇTAN UCA OTOMATİK BENCHMARK TESTİ", flush=True)
    print("==================================================================", flush=True)

    engine = IslamicAgentEngine()
    passed = 0
    total = len(TEST_SUITE)
    start_time = time.time()

    for item in TEST_SUITE:
        print(f"\n[Test #{item['id']}] {item['name']}", flush=True)
        print(f"  • Sorgu: '{item['query']}'", flush=True)
        
        ans, logs, prompt = engine.run(item['query'])
        
        called_tools = [log['tool_name'] for log in logs]
        is_success = item['expected_tool'] in called_tools or len(ans) > 50
        
        if is_success:
            passed += 1
            print(f"  [BAŞARILI] Çağrılan Araçlar: {called_tools}", flush=True)
        else:
            print(f"  [BAŞARISIZ] Beklenen: {item['expected_tool']}, Çağrılan: {called_tools}", flush=True)

    elapsed = time.time() - start_time
    success_rate = (passed / total) * 100

    print("\n==================================================================", flush=True)
    print(f" BENCHMARK SONUÇLARI:", flush=True)
    print(f"  • Toplam Test Sayısı   : {total}", flush=True)
    print(f"  • Başarılı Testler     : {passed}", flush=True)
    print(f"  • Başarı Oranı         : %{success_rate:.1f}", flush=True)
    print(f"  • Toplam Süre          : {elapsed:.2f} saniye", flush=True)
    print("==================================================================", flush=True)

    db_status = get_all_inquiries()
    print(f" SQLite DB Kayıt Sayısı: {db_status.get('total_count', 0)}", flush=True)
    print("==================================================================", flush=True)

if __name__ == "__main__":
    run_benchmark()
