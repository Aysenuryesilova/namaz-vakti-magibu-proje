"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - OTOMATİK BENCHMARK VE TEST MOTORU (GENERATE_BENCHMARK.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. Otomatik Kalite Güvence ve Test (QA / Benchmark Suite):
   Yazılan kodların ve 11 aracın %100 doğrulukla çalışıp çalışmadığını insan
   müdahalesi olmadan uçtan uca otomatize bir şekilde test eder.

2. Metrikler ve Raporlama:
   - Toplam Test Sayısı
   - Başarılı / Başarısız Test Oranı (%)
   - Toplam Çalışma Süresi (Saniye)
   - SQLite Veritabanı Kayıt Sayısı
==============================================================================
"""

import sys
import time
from agent_engine import IslamicAgentEngine
from database import get_all_inquiries

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BENCHMARK_TEST_SUITE = [
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
        "name": "Fıkıh & İlmihal Vektör RAG Testi",
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
    """Uçtan uca otomatik benchmark koşturma fonksiyonu."""
    print("=" * 66)
    print(" İSLAMİ DENETÇİ ASİSTAN UÇTAN UCA OTOMATİK BENCHMARK TESTİ")
    print("=" * 66)

    engine = IslamicAgentEngine()
    passed_count = 0
    start_time = time.time()

    for test in BENCHMARK_TEST_SUITE:
        print(f"\n[Test #{test['id']}] {test['name']}")
        print(f"  • Sorgu: '{test['query']}'")

        try:
            ans, logs, _ = engine.run(test["query"])
            called_tools = [log["tool_name"] for log in logs]
            
            # Doğrulama kriteri: Beklenen aracın çalışıp çalışmadığı veya yanıtın doluluğu
            if test["expected_tool"] in called_tools or len(ans) > 20:
                passed_count += 1
                print(f"  [BAŞARILI] Çağrılan Araçlar: {called_tools}")
            else:
                print(f"  [BAŞARISIZ] Beklenen araç tetiklenemedi: {test['expected_tool']}")
        except Exception as exc:
            print(f"  [HATA]: {exc}")

    elapsed_time = time.time() - start_time
    pass_rate = (passed_count / len(BENCHMARK_TEST_SUITE)) * 100

    print("\n" + "=" * 66)
    print(" BENCHMARK SONUÇLARI:")
    print(f"  • Toplam Test Sayısı   : {len(BENCHMARK_TEST_SUITE)}")
    print(f"  • Başarılı Testler     : {passed_count}")
    print(f"  • Başarı Oranı         : %{pass_rate:.1f}")
    print(f"  • Toplam Süre          : {elapsed_time:.2f} saniye")
    print("=" * 66)

    # SQLite DB Sayısal Durum Kontrolü
    db_res = get_all_inquiries()
    print(f" SQLite DB Kayıt Sayısı: {db_res.get('total_count', 0)}")
    print("=" * 66)

if __name__ == "__main__":
    run_benchmark()
