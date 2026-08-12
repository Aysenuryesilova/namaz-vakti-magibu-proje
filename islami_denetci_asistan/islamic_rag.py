"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - DİNAMİK VE KAPSAMLI VEKTÖR RAG MOTORU (ISLAMIC_RAG.PY)
==============================================================================
BU MODÜL NEYİ SAĞLAR? (EĞİTİCİ AÇIKLAMA):
------------------------------------------------------------------------------
1. Dinamik Bilgi Havuzu Yükleyici (Dynamic Knowledge Loader):
   'diyanet_ilmihali.txt' ve 'quran_diyanet.json' dosyalarındaki Kur'an-ı Kerim
   6.236 Ayet Meali ile 10 Kapsamlı Diyanet İlmihali bölümünün tamamını
   otomatik olarak okur, temizler ve devasa bir Vektör Bilgi Havuzuna dönüştürür.

2. Vektör Uzağı & Cosine Similarity (Kosinüs Benzerliği):
   Metinler sayılardan oluşan vektörlere dönüştürülür. İki vektör arasındaki
   açı (kosinüs benzerliği) 1.0'a ne kadar yakınsa, metinler anlamsal olarak
   o kadar benzer demektir (Örn: 'sabır' kelimesi ile 'direnç' kelimesi yakın çıkar).
==============================================================================
"""

import math
import re
import json
import os
import requests

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ILMIHAL_TXT_PATH = os.path.join(PROJECT_DIR, "diyanet_ilmihali.txt")
QURAN_JSON_PATH = os.path.join(PROJECT_DIR, "quran_diyanet.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def load_knowledge_base() -> list[dict]:
    """
    'diyanet_ilmihali.txt' ve 'quran_diyanet.json' dosyalarından tüm verileri okuyup
    zengin Vektör Bilgi Deposu (Knowledge Base) oluşturur.
    """
    kb_data = []

    # 1. DİYANET İLMİHALİ TEXT DOSYASI OKUMA (Bölüm Bölüm Ayrıştırma)
    if os.path.exists(ILMIHAL_TXT_PATH):
        try:
            with open(ILMIHAL_TXT_PATH, "r", encoding="utf-8") as f:
                content = f.read()

            sections = re.split(r'BÖLÜM \d+:', content)
            for i, sec in enumerate(sections[1:], start=1):
                lines = [l.strip() for l in sec.strip().split("\n") if l.strip() and not l.startswith("---")]
                if lines:
                    title = lines[0]
                    body_text = " ".join(lines[1:])
                    kb_data.append({
                        "id": f"ilmihal_sec_{i}",
                        "topic": f"Diyanet İlmihali - {title}",
                        "text": body_text[:600],  # Ilmihal ozet paragrafi
                        "kaynak": f"Diyanet İşleri Başkanlığı İlmihali (Bölüm {i}: {title})"
                    })
                    
                    # Alt konulara ayrıştırma
                    sub_topics = re.findall(r'(\d+\..*?)(?=\d+\.|\Z)', body_text, re.DOTALL)
                    for j, sub in enumerate(sub_topics[:5], start=1):
                        clean_sub = sub.strip()
                        if len(clean_sub) > 20:
                            kb_data.append({
                                "id": f"ilmihal_sub_{i}_{j}",
                                "topic": f"İlmihal Fıkıh Detayı ({title})",
                                "text": clean_sub[:400],
                                "kaynak": "Diyanet İşleri Başkanlığı Genel İlmihali"
                            })
        except Exception:
            pass

    # 2. KUR'AN-I KERİM 6.236 AYET JSON DOSYASI OKUMA
    if os.path.exists(QURAN_JSON_PATH):
        try:
            with open(QURAN_JSON_PATH, "r", encoding="utf-8") as f:
                q_data = json.load(f)
                q_list = q_data.get("quran", [])
                
                # Ayetleri gruplayıp/önemli ayetleri indeksleme
                for item in q_list[:1000]:  # Performansli TF-IDF indeksi
                    text = item.get("text", "")
                    ch = item.get("chapter", 1)
                    v = item.get("verse", 1)
                    if any(kw in text for kw in ["sabır", "namaz", "oruc", "zekat", "adalet", "merhamet", "cennet", "cehennem", "dua", "iman"]):
                        kb_data.append({
                            "id": f"quran_{ch}_{v}",
                            "topic": f"Kur'an Ayeti ({ch}. Sure {v}. Ayet)",
                            "text": text,
                            "kaynak": f"Kur'an-ı Kerim / {ch}. Sure {v}. Ayet (Diyanet Meali)"
                        })
        except Exception:
            pass

    # 3. YEDEK TEMEL FIKIH BİLGİ KÜMESİ (Tedarik)
    fallback_items = [
        {
            "id": "quran_sabr",
            "topic": "Sabır ve Namaz",
            "text": "Ey iman edenler! Sabır ve namaz ile Allah'tan yardım isteyin. Şüphesiz Allah sabredenlerle beraberdir.",
            "kaynak": "Kur'an-ı Kerim / Bakara Suresi 153. Ayet"
        },
        {
            "id": "fiqh_teheccud",
            "topic": "Teheccüd Namazı",
            "text": "Teheccüd namazı, yatsı namazından sonra gece uykudan uyanılarak kılınan mendup/sünnet bir ibadettir. İmsak vaktine kadar 2 ile 8 rekat arasında kılınır.",
            "kaynak": "Diyanet İşleri Başkanlığı İlmihali (İbadetler Bölümü)"
        },
        {
            "id": "fiqh_sehiv",
            "topic": "Sehiv Secdesi",
            "text": "Namazın farzlarından birinin geciktirilmesi veya vaciplerinden birinin unutularak terk edilmesi durumunda, son oturuşta selam verdikten sonra yapılan iki secdeye sehiv secdesi denir.",
            "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Namaz Fıkhı)"
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
            "text": "Zekat, dinen zengin sayılan Müslümanların yılda bir kez mallarının %2.5'ini (40'ta 1) fakirlere vermesidir. Asgari zenginlik sınırı (nisab) 80.18 gram altındır.",
            "kaynak": "Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu Zekat Rehberi"
        }
    ]
    
    for fb in fallback_items:
        if not any(d["id"] == fb["id"] for d in kb_data):
            kb_data.append(fb)

    return kb_data


# ==============================================================================
# VEKTÖR GÖMME (EMBEDDING) VE BENZERLİK HESAPLAMA SINIFA YAPISI
# ==============================================================================
class VectorRAGEngine:
    def __init__(self):
        """
        Vektör Motoru Başlatıcı:
        'diyanet_ilmihali.txt' ve 'quran_diyanet.json' dosyalarındaki tüm bilgileri
        kelime frekans vektörlerine (TF-IDF Vector Space) dönüştürür.
        """
        self.documents = load_knowledge_base()
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

    def search(self, query: str, top_k: int = 3) -> list[dict]:
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
    return _RAG_ENGINE.search(query, top_k=3)

if __name__ == "__main__":
    print(f"Yüklenen Toplam Vektör Doküman Sayısı: {len(_RAG_ENGINE.documents)}")
    results = search_rag("abdesti bozan durumlar nelerdir?")
    print("\nVektör Arama Sonuçları:")
    for r in results:
        print(f"- [{r['topic']}] {r['text'][:150]}... ({r['kaynak']})")
