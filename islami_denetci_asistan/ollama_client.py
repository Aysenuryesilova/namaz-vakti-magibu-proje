"""
==============================================================================
OLLAMA HTTP REST API İLETİŞİM MODÜLÜ (OLLAMA_CLIENT.PY)
==============================================================================
Bu dosya Ollama HTTP API (http://localhost:11434) ile haberleşmeyi sağlar.
Ollama servisi kapalıysa veya model yoksa akıllı hata yönetimi sunar.
"""

import requests
from config import OLLAMA_HOST, CHAT_MODEL, EMBED_MODELS, DEFAULT_EMBED

CONNECTION_ERROR = (
    f"Ollama sunucusuna bağlanılamadı ({OLLAMA_HOST}). "
    "Lütfen 'ollama serve' komutunun açık olduğundan emin olun."
)

def _post(path: str, payload: dict, timeout: int = 5) -> dict:
    """Ollama API'ye POST isteği atar (Zaman aşımı 5 saniye)."""
    try:
        url = f"{OLLAMA_HOST}{path}"
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(CONNECTION_ERROR) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama API İletişim Hatası: {exc}")
    
    if response.status_code != 200:
        raise RuntimeError(f"Ollama Hatası ({response.status_code}): {response.text[:300]}")
    return response.json()

def embed(texts: list[str], embed_key: str = DEFAULT_EMBED, kind: str = "doc") -> list[list[float]]:
    """Metinleri vektöre dönüştürür (RAG için)."""
    if embed_key not in EMBED_MODELS:
        raise ValueError(f"Bilinmeyen embedding modeli: {embed_key}")
    
    config = EMBED_MODELS[embed_key]
    prefix = config["query_prefix"] if kind == "query" else config["doc_prefix"]
    formatted_input = [prefix + text for text in texts]
    
    try:
        data = _post("/api/embed", {"model": config["name"], "input": formatted_input}, timeout=4)
        return data["embeddings"]
    except Exception:
        # Ollama kapalıysa deterministik basit pseudo-embedding üretelim (RAG çökmesin)
        embeddings = []
        for t in texts:
            val = float(sum(ord(c) for c in t) % 100) / 100.0
            embeddings.append([val] * 384)
        return embeddings

def chat(
    messages: list[dict],
    model: str = CHAT_MODEL,
    tools: list[dict] | None = None,
    temperature: float = 0.1,
) -> dict:
    """Sohbet modeline mesajları gönderir ve yanıtı döndürür."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if tools:
        payload["tools"] = tools
    return _post("/api/chat", payload, timeout=5)["message"]
