# 🕌 İslami Uygulama Doğruluk & Kaynak Denetçisi (Ezan Vakti Agent)

> **Yerel (Local) LLM tabanlı, Tool-Calling destekli İslami Mobil Uygulamalar için Kur'an, Hadis, Esmaül Hüsna, 81 İl ve İlçeleri kapsayan Doğrulama Asistanı**

Bu proje; [ezan-vakti](https://github.com/Aysenuryesilova/ezan-vakti) uygulaması için özel olarak geliştirilmiş tam teşekküllü bir denetçi asistandır.

---

## 🚀 Kapsam ve Araç Envanteri

1. **81 İl ve Tüm İlçeler Vakitleri (`calculate_prayer_times`)**: Türkiye'nin 81 ili ve **tüm ilçeleri** (*Sivas Şarkışla*, *İstanbul Kadıköy*, *Trabzon Of*, *Muş*, *Muğla Bodrum* vb.) için Diyanet vakitlerini getirir.
2. **Otomatik Konum Tespiti (`get_current_location_prayer_times`)**: Kullanıcının IP/GPS adresinden bulunduğu yeri otomatik algılayıp ezan vakitlerini söyler.
3. **Kur'an-ı Kerim Modülü (`search_quran_verse`)**: Tüm sureler, mealler, ayet sayıları, sure anlamları ve nüzul açıklamalarını sorgular.
4. **Hadisler ve Raviler Modülü (`search_hadith_and_narrators`)**: Hadis metinlerini, ravileri (*Hz. Ebu Hureyre, Hz. Aişe* vb.), ravi biyografilerini ve geliş sebeplerini denetler.
5. **Esmaül Hüsna Modülü (`get_esmaul_husna`)**: Allah'ın 99 İsmini ve Türkçe anlamlarını getirir.
6. **Kıble Açısı (`calculate_qibla_direction`)**: Tüm il ve ilçelerden Kabe'ye olan trigonometrik kıble açısını hesaplar.
7. **İslami Takvim & Özel Günler (`find_islamic_event`)**: Ramazan başlangıcı, bitişi, kaç gün sürdüğü ve Bayram tarihlerini hesaplar.
8. **Fıkıh & İlmihal RAG (`islamic_knowledge_question`)**: Sehiv secdesi, abdest, namaz ve fıkıh sorularını ChromaDB RAG katmanıyla yanıtlar.

---

## 🛠️ Çalıştırma

```bash
cd C:\Users\aysenur\Desktop\islami_denetci_asistan
pip install -r requirements.txt
ollama pull qwen2.5:3b
python chat.py
```
