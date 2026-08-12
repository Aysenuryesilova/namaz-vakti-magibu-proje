import sys
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from agent_engine import IslamicAgentEngine

engine = IslamicAgentEngine()

queries = [
    'İZMİT MERKEZ EZAN VAKİTLERİ',
    'NEBE SURESİ ANLAMI MEALİ NEDİR?KURANIN KAÇINCI SURESİDİR?',
    '100.SURE NEDİR ?',
    'MEVCUT KIBLEM NE YÖNDE OLMALI ?',
    '100 GRAM ALTIN KAÇ DOLAR EDER'
]

for q in queries:
    print('=== QUERY:', q, flush=True)
    ans, logs, prompt = engine.run(q)
    print('ANSWER:\n', ans, flush=True)
    print('-'*50, flush=True)
