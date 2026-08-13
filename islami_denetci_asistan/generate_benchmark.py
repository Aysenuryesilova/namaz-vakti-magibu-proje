"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - KESİN DOĞRULUKLU BENCHMARK TESTİ (GENERATE_BENCHMARK.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (TEKNİK VE MATEMATİKSEL BAŞARI KRİTERİ DÜZELTMESİ):
------------------------------------------------------------------------------
1. Kesin ve Gevşetilmemiş Başarı Kriterleri (Strict Evaluation Criteria):
   Önceki hatalı mantıkta kullanılan 'or len(ans) > 20' koşulu kaldırılmıştır.
   Bir testin başarılı sayılması için:
   a) Beklenen araç kesinlikle çağrılmış olmalıdır (test["expected_tool"] in called_tools).
   b) Üretilen yanıt içerisinde beklenen fıkhi/sayısal doğrulama terimleri
      (Örn: 'İmsak', '151.56', 'ZEKAT VERMEK FARZDIR', 'El-Melik', '114')
      kesinlikle yer almalıdır!
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
        "expected_tool": "calculate_prayer_times",
        "expected_keyword": "İmsak"
    },
    {
        "id": 2,
        "name": "Kıble Açısı Hesaplama Testi",
        "query": "Ankara için kıble açısı kaç derecedir?",
        "expected_tool": "calculate_qibla_direction",
        "expected_keyword": "Kıble"
    },
    {
        "id": 3,
        "name": "Zekat Fıkhi Hesaplama Testi (Kod Yürütme)",
        "query": "100 gram altınım ve 50000 TL nakdim var zekat düşer mi?",
        "expected_tool": "calculate_zekat",
        "expected_keyword": "FARZDIR"
    },
    {
        "id": 4,
        "name": "SQLite Veritabanı Kayıt Testi (Veri Yazma)",
        "query": "Bu soruyu veritabanına kaydet: Sehiv secdesi hangi durumlarda yapılır?",
        "expected_tool": "save_inquiry_tool",
        "expected_keyword": "Kayıt Başarılı"
    },
    {
        "id": 5,
        "name": "SQLite Veritabanı Okuma Testi (Veri Okuma)",
        "query": "Veritabanındaki tüm kayıtlı geçmiş soruları listele.",
        "expected_tool": "get_all_inquiries_tool",
        "expected_keyword": "SQLite Veritabanı"
    },
    {
        "id": 6,
        "name": "Kur'an Meali ve Sure Arama Testi",
        "query": "Kur'an-ı Kerim kaç suredir ve kaç ayettir?",
        "expected_tool": "search_quran_verse",
        "expected_keyword": "114"
    },
    {
        "id": 7,
        "name": "Fıkıh & İlmihal Vektör RAG Testi",
        "query": "Teheccüd namazı nedir ve ne zaman kılınır?",
        "expected_tool": "islamic_knowledge_question",
        "expected_keyword": "Teheccüd"
    },
    {
        "id": 8,
        "name": "Esmaül Hüsna Testi",
        "query": "elmelik isminin Esmaül Hüsna anlamı nedir?",
        "expected_tool": "get_esmaul_husna",
        "expected_keyword": "El-Melik"
    },
    {
        "id": 9,
        "name": "Ramazan ve İslami Takvim Testi",
        "query": "2026 Ramazan başlangıcı ve bayram ne zaman?",
        "expected_tool": "find_islamic_event",
        "expected_keyword": "Ramazan"
    },
    {
        "id": 10,
        "name": "Canlı Web Araması Testi",
        "query": "2026 Diyanet hac başvuru tarihleri güncel duyuruları nedir?",
        "expected_tool": "web_search_tool",
        "expected_keyword": "Arama"
    }
]

def run_benchmark():
    """Kesin ve sıkı kriterlerle uçtan uca otomatik benchmark koşturma fonksiyonu."""
    print("=" * 66)
    print(" İSLAMİ DENETÇİ ASİSTAN SIKI KRİTERLİ BENCHMARK TESTİ")
    print("=" * 66)

    engine = IslamicAgentEngine()
    passed_count = 0
    start_time = time.time()

    for test in BENCHMARK_TEST_SUITE:
        print(f"\n[Test #{test['id']}] {test['name']}")
        print(f"  • Sorgu: '{test['query']}'")

        t_start = time.time()
        try:
            ans, logs, _ = engine.run(test["query"])
            t_elapsed = time.time() - t_start
            called_tools = [log["tool_name"] for log in logs]
            
            # SIKI BAŞARI KRİTERİ:
            # 1. Beklenen araç KESİNLİKLE çağrılmış olmalı!
            # 2. Yanıt içerisinde beklenen doğrulama kelimesi geçmeli!
            tool_ok = test["expected_tool"] in called_tools
            keyword_ok = test["expected_keyword"].lower() in ans.lower()

            if tool_ok and keyword_ok:
                passed_count += 1
                print(f"  ✅ [BAŞARILI] (Süre: {t_elapsed:.2f}s) | Araç: {called_tools} | Kelime '{test['expected_keyword']}' Bulundu.")
            else:
                print(f"  ❌ [BAŞARISIZ] (Süre: {t_elapsed:.2f}s) | Araç Uyumlu: {tool_ok} | Kelime Uyumlu: {keyword_ok}")
                print(f"     Çağrılan Araçlar: {called_tools}")
        except Exception as exc:
            t_elapsed = time.time() - t_start
            print(f"  ❌ [HATA] (Süre: {t_elapsed:.2f}s): {exc}")

    elapsed_time = time.time() - start_time
    pass_rate = (passed_count / len(BENCHMARK_TEST_SUITE)) * 100

    print("\n" + "=" * 66)
    print(" SIKI BENCHMARK SONUÇLARI:")
    print(f"  • Toplam Test Sayısı   : {len(BENCHMARK_TEST_SUITE)}")
    print(f"  • Kesin Başarılı       : {passed_count}")
    print(f"  • Gerçek Başarı Oranı  : %{pass_rate:.1f}")
    print(f"  • Toplam Süre          : {elapsed_time:.2f} saniye")
    print("=" * 66)

    db_res = get_all_inquiries()
    print(f" SQLite DB Kayıt Sayısı: {db_res.get('total_count', 0)}")
    print("=" * 66)

if __name__ == "__main__":
    run_benchmark()
