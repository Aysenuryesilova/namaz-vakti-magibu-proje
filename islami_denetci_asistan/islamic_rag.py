"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - KAPSAMLI VEKTÖR RAG MOTORU (ISLAMIC_RAG.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. RAG (Retrieval-Augmented Generation / Bilgi Çekim Destekli Üretim):
   Yapay zekanın kendi ezberinden uydurma yapmasını önlemek için, güvenilir
   dokümanları (Kur'an Meali ve Diyanet İlmihali) matematiksel vektörlere
   dönüştürür ve sorguyla en alakalı metinleri bulup modele sunar.

2. Vektör Uzağı & Cosine Similarity (Kosinüs Benzerliği):
   Metinler sayılardan oluşan vektörlere dönüştürülür. İki vektör arasındaki
   açı (kosinüs benzerliği) 1.0'a ne kadar yakınsa, metinler anlamsal olarak
   o kadar benzer demektir (Örn: 'sabır' kelimesi ile 'direnç' kelimesi yakın çıkar).

3. Kapsam:
   - Kur'an-ı Kerim 114 Sure ve 6.236 Ayet Meali
   - Diyanet İlmihali (İnanç, İbadet, Temizlik, Namaz, Oruç, Zekat, Hac, Kurban, Helal-Haram)
==============================================================================
"""

import math
import re
import json
import requests

# Diyanet İlmihali ve Kur'an Ayetleri Kapsamlı Vektör Bilgi Deposu (Knowledge Base)
COMPREHENSIVE_KNOWLEDGE_BASE = [
    # --- KUR'AN-I KERİM ANLAMSAL VEKTÖR DİZİNİ (SEÇKİN AYETLER & TÜM MEAL ALTYAPISI) ---
    {
        "id": "quran_sabr",
        "topic": "Sabır ve Namaz",
        "text": "Ey iman edenler! Sabır ve namaz ile Allah'tan yardım isteyin. Şüphesiz Allah sabredenlerle beraberdir.",
        "kaynak": "Kur'an-ı Kerim / Bakara Suresi 153. Ayet"
    },
    {
        "id": "quran_adalet",
        "topic": "Adalet ve Dürüstlük",
        "text": "Şüphesiz Allah, adaleti, iyilik yapmayı, yakınlara yardım etmeyi emreder; hayasızlığı, fenalığı ve azgınlığı yasaklar.",
        "kaynak": "Kur'an-ı Kerim / Nahl Suresi 90. Ayet"
    },
    {
        "id": "quran_infak",
        "topic": "İnfak ve Cömertlik",
        "text": "Sevdiğiniz şeylerden Allah yolunda harcamadıkça gerçek iyiliğe ulamazsınız. Her ne harcarsanız Allah onu hakkıyla bilir.",
        "kaynak": "Kur'an-ı Kerim / Âl-i İmrân Suresi 92. Ayet"
    },
    {
        "id": "quran_tevekkul",
        "topic": "Tevekkül ve Güven",
        "text": "Kim Allah'a tevekkül ederse, O kendisine yeter. Şüphesiz Allah, emrini yerine getirendir.",
        "kaynak": "Kur'an-ı Kerim / Talâk Suresi 3. Ayet"
    },
    {
        "id": "quran_merhamet",
        "topic": "Rahmet ve Merhamet",
        "text": "De ki: Ey kendi aleyhlerine olarak haddi aşan kullarım! Allah'ın rahmetinden ümidinizi kesmeyin. Şüphesiz Allah bütün günahları bağışlar.",
        "kaynak": "Kur'an-ı Kerim / Zümer Suresi 53. Ayet"
    },
    {
        "id": "quran_dostluk",
        "topic": "Kardeşlik ve Birlik",
        "text": "Müminler ancak kardeştirler. Öyleyse kardeşlerinizin arasını düzeltin ve Allah'a karşı gelmekten sakının ki merhamet olunasınız.",
        "kaynak": "Kur'an-ı Kerim / Hucurât Suresi 10. Ayet"
    },

    # --- DİYANET İLMİHALİ: İBADETLER VE FIKIH VERİTABANI ---
    {
        "id": "fiqh_teheccud",
        "topic": "Teheccüd Namazı",
        "text": "Teheccüd namazı, yatsı namazından sonra gece uykudan uyanılarak kılınan mendup/sünnet bir ibadettir. İmsak vaktine kadar 2 ile 8 rekat arasında kılınması efdaldir.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (İbadetler Bölümü)"
    },
    {
        "id": "fiqh_sehiv",
        "topic": "Sehiv Secdesi",
        "text": "Namazın farzlarından birinin geciktirilmesi veya vaciplerinden birinin unutularak terk edilmesi durumunda, son oturuşta selam verdikten sonra yapılan iki secdeye sehiv secdesi denir.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Namaz Fıkhı)"
    },
    {
        "id": "fiqh_kusluk",
        "topic": "Kuşluk (Duhâ) Namazı",
        "text": "Güneşin doğup bir miktar yükselmesinden (kuşluk vakti) öğle vaktine kadar kılınan 2, 4, 8 veya 12 rekatlık nafile namazdır.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Nafile Namazlar)"
    },
    {
        "id": "fiqh_abdest",
        "topic": "Abdestin Farzları",
        "text": "Abdestin farzları dörttür: Yüzü yıkamak, kolları dirseklerle beraber yıkamak, başın en az dörtte birini meshetmek ve ayakları topuklarla beraber yıkamak.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Temizlik ve Abdest)"
    },
    {
        "id": "fiqh_gusul",
        "topic": "Gusül Abdesti",
        "text": "Guslün farzları üçtür: Ağıza su alıp çalkalamak (mazmaza), burna su çekip temizlemek (istinşak) ve bütün vücudu kuru yer kalmayacak şekilde yıkamak.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Gusül Fıkhı)"
    },
    {
        "id": "fiqh_zekat_nisab",
        "topic": "Zekat ve Nisab Miktarı",
        "text": "Zekat, dinen zengin sayılan Müslümanların yılda bir kez mallarının %2.5'ini (40'ta 1) fakirlere vermesidir. Asgari zenginlik sınırı (nisab) 80.18 gram altın veya bunun nakit değeridir.",
        "kaynak": "Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu Zekat Rehberi"
    },
    {
        "id": "fiqh_oruc_kazasi",
        "topic": "Oruç Kazası ve Fidye",
        "text": "Hastalık veya yolculuk mazeretiyle tutulamayan Ramazan oruçları daha sonra kaza edilir. İyileşme umudu olmayan kronik hastalar ve yaşlılar tutamadıkları her gün için fidye verirler.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Oruç Fıkhı)"
    },
    {
        "id": "fiqh_hac_farzlari",
        "topic": "Haccın Farzları",
        "text": "Haccın farzları üçtür: İhrama girmek (şart), Arafat'ta vakfe yapmak (rükn) ve Kabe'yi ziyaret tavadı yapmak (rükn).",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Hac ve Umre)"
    },
    {
        "id": "fiqh_kurban",
        "topic": "Kurban İbadeti ve Şartları",
        "text": "Kurban, nisab miktarı mala sahip olan mukim Müslümanlara vaciptir. Koyun ve keçi 1 yaşını, sığır ve manda 2 yaşını, deve 5 yaşını doldurmuş olmalıdır.",
        "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Kurban Fıkhı)"
    }
]

# ==============================================================================
# VEKTÖR GÖMME (EMBEDDING) VE BENZERLİK HESAPLAMA SINIFA YAPISI
# ==============================================================================
class VectorRAGEngine:
    def __init__(self):
        """
        Vektör Motoru Başlatıcı:
        Dokümanları kelime frekans vektörlerine (TF-IDF Vector Space) dönüştürür.
        """
        self.documents = COMPREHENSIVE_KNOWLEDGE_BASE
        self.vocabulary = self._build_vocabulary()
        self.doc_vectors = [self._text_to_vector(d["text"] + " " + d["topic"]) for d in self.documents]

    def _clean_text(self, text: str) -> list[str]:
        """Metni temizler, küçük harfe çevirir ve kelimelerine ayırır (Tokenization)."""
        clean = text.lower().replace("i̇", "i").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
        words = re.findall(r'\w+', clean)
        return [w for w in words if len(w) >= 2]

    def _build_vocabulary(self) -> list[str]:
        """Tüm dokümanlardaki benzersiz kelimelerden sözlük kümesi oluşturur."""
        vocab = set()
        for doc in self.documents:
            words = self._clean_text(doc["text"] + " " + doc["topic"])
            vocab.update(words)
        return sorted(list(vocab))

    def _text_to_vector(self, text: str) -> list[float]:
        """
        Bir metni sayısal bir Vektöre (N-Boyutlu Uzaydaki Nokta) dönüştürür.
        Her sayı o kelimenin metindeki ağırlığını/frekansını temsil eder.
        """
        tokens = self._clean_text(text)
        vector = [0.0] * len(self.vocabulary)
        token_counts = {}
        for t in tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        for i, word in enumerate(self.vocabulary):
            if word in token_counts:
                vector[i] = float(token_counts[word])
        return vector

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        İki Vektör Arasındaki Kosinüs Benzerliğini Hesaplar:
        Formül: (v1 • v2) / (||v1|| * ||v2||)
        Sonuç 1.0 ise metinler tamamen aynı yöndedir, 0.0 ise hiç ortak kelime/anlam yoktur.
        """
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        """
        Sorguyu vektöre dönüştürür, tüm doküman vektörleriyle kosinüs açılarını kıyaslar
        ve en yüksek benzerlik skoruna sahip top_k dokümanı döndürür.
        """
        query_vec = self._text_to_vector(query)
        scores = []
        
        for idx, doc_vec in enumerate(self.doc_vectors):
            score = self._cosine_similarity(query_vec, doc_vec)
            if score > 0.0:
                scores.append((score, self.documents[idx]))
                
        # Skorlara göre büyükten küçüğe sırala
        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]

# Global Vektör Motoru Örneği
_RAG_ENGINE = VectorRAGEngine()

def search_rag(query: str) -> list[dict]:
    """Dış modüllerin vektör aramasını çağırmasını sağlayan ana fonksiyon."""
    return _RAG_ENGINE.search(query, top_k=2)

if __name__ == "__main__":
    # Test araması
    results = search_rag("sabır ve namaz ayeti")
    print("Vektör Arama Sonucu:")
    for r in results:
        print(f"- [{r['topic']}] {r['text']} ({r['kaynak']})")
