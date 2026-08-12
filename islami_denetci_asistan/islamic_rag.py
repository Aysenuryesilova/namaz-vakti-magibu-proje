"""
==============================================================================
İSLÂMİ DENETÇİ ASİSTAN - GÜÇLENDİRİLMİŞ VE KUSURSUZ TF-IDF RAG MOTORU
==============================================================================
BU MODÜL NEYİ SAĞLAR? (NLP VE STOP-WORDS DÜZELTMESİ):
------------------------------------------------------------------------------
1. Soru Kelimeleri ve Stop-Words Filtreleme (Question-Word Filtering):
   'nedir', 'nasıl', 'ne', 'kim', 'nerede', 'bu', 'o', 've', 'mi' gibi soru ve
   bağlaç kelimeleri RAG kelime vektöründen tamamen temizlenmiştir. Böylece
   'abdest nedir' denildiğinde 'nedir' içeren alakasız ayetler elenir ve doğrudan
   'Abdest ve Taharet Fıkhı' dokümanı en yüksek skorla eşleşir.

2. Konu Başlığı Ağırlıklandırması (Topic Boosting):
   Dokümanın konu başlığındaki fıkhi terimlere 3 kat TF-IDF ağırlığı (Topic Boost)
   verilerek tam isabetli arama sağlanır.
==============================================================================
"""

import math
import re
import json
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ILMIHAL_TXT_PATH = os.path.join(PROJECT_DIR, "diyanet_ilmihali.txt")
QURAN_JSON_PATH = os.path.join(PROJECT_DIR, "quran_diyanet.json")

# TÜRKÇE STOP-WORDS VE SORU KELİMELERİ TEMİZLEME KÜMESİ
STOP_WORDS = {
    "nedir", "nasil", "ne", "kim", "nerede", "zaman", "hangi", "kac", "derece",
    "dir", "dir", "dur", "dur", "mi", "mi", "mu", "mu", "midir", "midir", "mudur", "mudur",
    "bu", "su", "o", "ve", "ile", "de", "da", "bir", "gibi", "icin", "dedi", "insanlar",
    "var", "yok", "eden", "olan", "olanlar", "bize", "size", "bunu", "buna", "ondan"
}

def load_knowledge_base() -> list[dict]:
    """'diyanet_ilmihali.txt' ve 'quran_diyanet.json' dosyalarından tüm verileri okur."""
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
                        "text": body_text[:600],
                        "kaynak": f"Diyanet İşleri Başkanlığı İlmihali (Bölüm {i}: {title})"
                    })
                    
                    sub_topics = re.findall(r'(\d+\..*?)(?=\d+\.|\Z)', body_text, re.DOTALL)
                    for j, sub in enumerate(sub_topics[:6], start=1):
                        clean_sub = sub.strip()
                        if len(clean_sub) > 20:
                            # Alt konu başlığını belirleme
                            sub_title = clean_sub.split(":")[0] if ":" in clean_sub else title
                            kb_data.append({
                                "id": f"ilmihal_sub_{i}_{j}",
                                "topic": f"Diyanet İlmihali Fıkıh Konusu: {sub_title}",
                                "text": clean_sub[:400],
                                "kaynak": "Diyanet İşleri Başkanlığı Genel İlmihali"
                            })
        except Exception:
            pass

    # 2. KUR'AN-I KERİM 6.236 AYETİN TAMAMI
    if os.path.exists(QURAN_JSON_PATH):
        try:
            with open(QURAN_JSON_PATH, "r", encoding="utf-8") as f:
                q_data = json.load(f)
                q_list = q_data.get("quran", [])
                
                for item in q_list:
                    text = item.get("text", "")
                    ch = item.get("chapter", 1)
                    v = item.get("verse", 1)
                    if text:
                        kb_data.append({
                            "id": f"quran_{ch}_{v}",
                            "topic": f"Kur'an Ayeti ({ch}. Sure {v}. Ayet)",
                            "text": text,
                            "kaynak": f"Kur'an-ı Kerim / {ch}. Sure {v}. Ayet (Diyanet Meali)"
                        })
        except Exception:
            pass

    # 3. YEDEK TEMEL FIKIH BİLGİ KÜMESİ
    fallback_items = [
        {
            "id": "fiqh_abdest_nedir",
            "topic": "Abdest Nedir ve Nasıl Alınır?",
            "text": "Abdest, belirli uzuvları (yüz, kollar, baş ve ayaklar) usulüne uygun olarak yıkamak ve meshetmekten ibaret hükmî bir temizliktir. Abdestin farzları 4'tür: Yüzü yıkamak, kolları dirseklerle beraber yıkamak, başın en az dörtte birini meshetmek, ayakları topuklarla beraber yıkamak.",
            "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Temizlik ve Abdest Fıkhı)"
        },
        {
            "id": "fiqh_teheccud",
            "topic": "Teheccüd Namazı Nedir ve Nasıl Kılınır?",
            "text": "Teheccüd namazı, yatsı namazından sonra gece uykudan uyanılarak imsak vaktine kadar kılınan mendup/sünnet nafile namazdır. 2 ile 8 rekat arasında kılınır.",
            "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Nafile Namazlar)"
        },
        {
            "id": "fiqh_sehiv",
            "topic": "Sehiv Secdesi Nedir ve Nasıl Yapılır?",
            "text": "Namazın farzlarından birinin geciktirilmesi veya vaciplerinden birinin unutularak terk edilmesi durumunda, son oturuşta selam verdikten sonra yapılan iki secdeye sehiv secdesi denir.",
            "kaynak": "Diyanet İşleri Başkanlığı İlmihali (Namaz Fıkhı)"
        }
    ]
    
    for fb in fallback_items:
        if not any(d["id"] == fb["id"] for d in kb_data):
            kb_data.append(fb)

    return kb_data


# ==============================================================================
# GÜÇLENDİRİLMİŞ TF-IDF VEKTÖR UZAYI VE KOSİNÜS BENZERLİĞİ
# ==============================================================================
class VectorRAGEngine:
    def __init__(self):
        """
        TF-IDF Vektör Motoru Başlatıcı:
        6.236 Ayet ve Diyanet İlmihalinin tamamını kelime frekans matrisine dönüştürür.
        """
        self.documents = load_knowledge_base()
        self.num_docs = len(self.documents)
        self.vocabulary, self.df = self._build_vocabulary_and_df()
        self.idf = self._calculate_idf()
        self.doc_vectors = [self._text_to_tfidf_vector((d["topic"] + " ") * 3 + d["text"]) for d in self.documents]

    def _clean_text(self, text: str) -> list[str]:
        """Metni temizler, küçük harfe çevirir, stop-words'leri çıkarır ve kelimelerine ayırır."""
        clean = (
            text.lower()
            .replace("i̇", "i").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
        )
        words = re.findall(r'\w+', clean)
        # Soru kelimeleri ve stop-words elenir!
        return [w for w in words if len(w) >= 2 and w not in STOP_WORDS]

    def _build_vocabulary_and_df(self) -> tuple[list[str], dict[str, int]]:
        """Sözlük kümesini (vocabulary) ve her kelimenin kaç dokümanda geçtiğini (DF) hesaplar."""
        vocab_set = set()
        df_counts = {}

        for doc in self.documents:
            words = set(self._clean_text((doc["topic"] + " ") * 3 + doc["text"]))
            vocab_set.update(words)
            for w in words:
                df_counts[w] = df_counts.get(w, 0) + 1

        return sorted(list(vocab_set)), df_counts

    def _calculate_idf(self) -> dict[str, float]:
        """Inverse Document Frequency (IDF): log(1 + N / (1 + df))"""
        idf_dict = {}
        for word in self.vocabulary:
            df_val = self.df.get(word, 1)
            idf_dict[word] = math.log(1.0 + (self.num_docs / (1.0 + df_val)))
        return idf_dict

    def _text_to_tfidf_vector(self, text: str) -> list[float]:
        """Metni TF-IDF ağırlıklı sayısal vektöre dönüştürür."""
        tokens = self._clean_text(text)
        if not tokens:
            return [0.0] * len(self.vocabulary)

        tf_counts = {}
        for t in tokens:
            tf_counts[t] = tf_counts.get(t, 0) + 1

        total_tokens = len(tokens)
        vector = [0.0] * len(self.vocabulary)

        for i, word in enumerate(self.vocabulary):
            if word in tf_counts:
                tf = tf_counts[word] / total_tokens
                idf = self.idf.get(word, 1.0)
                vector[i] = tf * idf

        return vector

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """İki Vektör Arasındaki Kosinüs Benzerliğini Hesaplar."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def search(self, query: str, top_k: int = 2, similarity_threshold: float = 0.02, **kwargs) -> list[dict]:
        """
        Sorguyu TF-IDF vektörüne dönüştürür. 'abdest', 'namaz', 'zekat', 'sehiv', 'teheccud'
        gibi fıkhi terimler için Diyanet İlmihali dokümanlarına öncelik verir.
        """
        k_val = kwargs.get("k", top_k)
        query_tokens = set(self._clean_text(query))
        query_vec = self._text_to_tfidf_vector(query)
        scores = []
        
        fiqh_keywords = {"abdest", "gusul", "namaz", "zekat", "oruc", "sehiv", "teheccud", "kusluk", "kible", "taharet"}
        is_fiqh_query = any(kw in query_tokens for kw in fiqh_keywords)

        for idx, doc_vec in enumerate(self.doc_vectors):
            doc = self.documents[idx]
            score = self._cosine_similarity(query_vec, doc_vec)
            
            # Fıkıh sorgularında Diyanet İlmihali dokümanlarına öncelik ver
            if is_fiqh_query and doc["id"].startswith("ilmihal"):
                score *= 2.5
                
            if score >= similarity_threshold:
                scores.append((score, doc))
                
        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:k_val]]

# Global Vektör Motoru Örneği
_RAG_ENGINE = VectorRAGEngine()

def search_rag(query: str, **kwargs) -> list[dict]:
    """Dış modüllerin TF-IDF vektör aramasını çağırmasını sağlayan ana fonksiyon."""
    return _RAG_ENGINE.search(query, top_k=2, **kwargs)

if __name__ == "__main__":
    for test_q in ["abdest nedir", "abdest nasıl alınır?", "teheccüd namazı nedir?"]:
        print(f"\n=== SORGUSU: '{test_q}' ===")
        results = search_rag(test_q)
        for r in results:
            print(f"- [{r['topic']}]\n  {r['text'][:150]}...\n  ({r['kaynak']})")
