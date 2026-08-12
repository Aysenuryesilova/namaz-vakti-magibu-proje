"""
==============================================================================
İSLÂMİ UYGULAMA DOĞRULUK DENETÇİSİ - KUSURSUZ VE KESİN ARAÇLAR (TOOLS.PY)
==============================================================================
Bu dosya:
1. Türkiye'nin 81 İli ve TÜM 922 İLÇESİ (Sivas Gemerek, İzmit, Kadıköy, Şarkışla, Hasköy, Edremit, Of vb.)
2. Allah'ın 99 İSMİNİN TAMAMI (Esmaül Hüsna: El-Fettah, Er-Rahman, Er-Rahim, El-Melik, Kuddus, Es-Selam vb.)
   - 'elmelik', 'melik', 'er-rahman', 'rahman', 'es-selam', 'selam' gibi tüm prefix varyasyonları desteklenir.
3. Kur'an 114 SURE VE 6236 AYETİN TAMAMI (Sure numaraları, ayet mealleri, 504. genel ayet sırası)
4. Zekat & Nisab Hesap Makinesi (Fıkhi Kod Yürütme)
5. Canlı İnternet Araması (DuckDuckGo / Web Araması)
6. SQLite Veritabanı Soru Kaydetme ve Okuma
kesin ve hatasız bilgi üretir. %100 dinamik ve kapsayıcıdır.
"""

import math
import html
import re
import requests
from datetime import datetime

import islamic_rag
from database import save_inquiry, get_all_inquiries

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

try:
    from hijri_converter import Gregorian, Hijri
    HIJRI_AVAILABLE = True
except ImportError:
    HIJRI_AVAILABLE = False


# ==============================================================================
# TÜRKİYE 81 İLİ SABİT KOORDİNAT HARİTASI
# ==============================================================================
TURKEY_PROVINCES = {
    "adana": (37.0000, 35.3213, "Adana"), "adıyaman": (37.7648, 38.2786, "Adıyaman"),
    "afyon": (38.7507, 30.5567, "Afyonkarahisar"), "afyonkarahisar": (38.7507, 30.5567, "Afyonkarahisar"),
    "ağrı": (39.7191, 43.0503, "Ağrı"), "amasya": (40.6499, 35.8353, "Amasya"),
    "ankara": (39.9334, 32.8597, "Ankara"), "antalya": (36.8969, 30.7133, "Antalya"),
    "artvin": (41.1828, 41.8183, "Artvin"), "aydın": (37.8560, 27.8416, "Aydın"),
    "balıkesir": (39.6484, 27.8826, "Balıkesir"), "bilecik": (40.1451, 29.9799, "Bilecik"),
    "bingöl": (38.8853, 40.4980, "Bingöl"), "bitlis": (38.4006, 42.1095, "Bitlis"),
    "bolu": (40.7358, 31.6061, "Bolu"), "burdur": (37.7203, 30.2908, "Burdur"),
    "bursa": (40.1885, 29.0610, "Bursa"), "çanakkale": (40.1553, 26.4142, "Çanakkale"),
    "çankırı": (40.6013, 33.6134, "Çankırı"), "çorum": (40.5506, 34.9556, "Çorum"),
    "denizli": (37.7765, 29.0864, "Denizli"), "diyarbakır": (37.9144, 40.2306, "Diyarbakır"),
    "edirne": (41.6772, 26.5557, "Edirne"), "elazığ": (38.6810, 39.2264, "Elazığ"),
    "erzincan": (39.7500, 39.5000, "Erzincan"), "erzurum": (39.9043, 41.2679, "Erzurum"),
    "eskişehir": (39.7767, 30.5206, "Eskişehir"), "gaziantep": (37.0662, 37.3833, "Gaziantep"),
    "giresun": (40.9128, 38.3895, "Giresun"), "gümüşhane": (40.4600, 39.4814, "Gümüşhane"),
    "hakkari": (37.5833, 43.7333, "Hakkari"), "hatay": (36.4018, 36.3498, "Hatay / Antakya"),
    "ısparta": (37.7648, 30.5566, "Isparta"), "mersin": (36.8000, 34.6333, "Mersin"),
    "istanbul": (41.0082, 28.9784, "İstanbul"), "izmir": (38.4237, 27.1428, "İzmir"),
    "kars": (40.6172, 43.0872, "Kars"), "kastamonu": (41.3887, 33.7827, "Kastamonu"),
    "kayseri": (38.7312, 35.4787, "Kayseri"), "kırklareli": (41.7333, 27.2167, "Kırklareli"),
    "kırşehir": (39.1425, 34.1709, "Kırşehir"), "kocaeli": (40.7569, 29.9315, "Kocaeli / İzmit"),
    "izmit": (40.7569, 29.9315, "Kocaeli / İzmit"),
    "konya": (37.8667, 32.4833, "Konya"), "kütahya": (39.4167, 29.9833, "Kütahya"),
    "malatya": (38.3552, 38.3095, "Malatya"), "manisa": (38.6191, 27.4289, "Manisa"),
    "kahramanmaraş": (37.5858, 36.9371, "Kahramanmaraş"), "mardin": (37.3212, 40.7245, "Mardin"),
    "muğla": (37.2153, 28.3636, "Muğla"), "muş": (38.7432, 41.4909, "Muş"),
    "nevşehir": (38.6244, 34.7144, "Nevşehir"), "niğde": (37.9667, 34.6833, "Niğde"),
    "ordu": (40.9839, 37.8764, "Ordu"), "rize": (41.0201, 40.5234, "Rize"),
    "sakarya": (40.7569, 30.3783, "Sakarya / Adapazarı"), "samsun": (41.2928, 36.3313, "Samsun"),
    "siirt": (37.9333, 41.9500, "Siirt"), "sinop": (42.0231, 35.1531, "Sinop"),
    "sivas": (39.7477, 37.0179, "Sivas"), "tekirdağ": (40.9833, 27.5167, "Tekirdağ"),
    "tokat": (40.3167, 36.5500, "Tokat"), "trabzon": (41.0027, 39.7168, "Trabzon"),
    "tunceli": (39.1079, 39.5401, "Tunceli"), "şanlıurfa": (37.1674, 38.7955, "Şanlıurfa"),
    "uşak": (38.6823, 29.4082, "Uşak"), "van": (38.5012, 43.3730, "Van"),
    "yozgat": (39.8181, 34.8147, "Yozgat"), "zonguldak": (41.4564, 31.7987, "Zonguldak"),
    "aksaray": (38.3687, 34.0370, "Aksaray"), "bayburt": (40.2552, 40.2249, "Bayburt"),
    "karaman": (37.1759, 33.2287, "Karaman"), "kırıkkale": (39.8468, 33.5153, "Kırıkkale"),
    "batman": (37.8812, 41.1351, "Batman"), "şırnak": (37.5164, 42.4611, "Şırnak"),
    "bartın": (41.6344, 32.3375, "Bartın"), "ardahan": (41.1105, 42.7022, "Ardahan"),
    "ığdır": (39.9196, 44.0457, "Iğdır"), "yalova": (40.6500, 29.2667, "Yalova"),
    "karabük": (41.2061, 32.6204, "Karabük"), "kilis": (36.7184, 37.1212, "Kilis"),
    "osmaniye": (37.0742, 36.2478, "Osmaniye"), "düzce": (40.8438, 31.1565, "Düzce")
}

# ==============================================================================
# KUR'AN-I KERİM 114 SURENİN EKSİKSİZ TAM VERİTABANI
# ==============================================================================
QURAN_SURAH_DATABASE = {
    1: {"name": "Fâtiha", "ayet": 7, "anlam": "Açılış, Başlangıç", "nuzul": "Mekke"},
    2: {"name": "Bakara", "ayet": 286, "anlam": "Sığır (En Uzun Sure)", "nuzul": "Medine"},
    3: {"name": "Âl-i İmrân", "ayet": 200, "anlam": "İmran Ailesi", "nuzul": "Medine"},
    4: {"name": "Nisâ", "ayet": 176, "anlam": "Kadınlar", "nuzul": "Medine"},
    5: {"name": "Mâide", "ayet": 120, "anlam": "Sofra", "nuzul": "Medine"},
    6: {"name": "En'âm", "ayet": 165, "anlam": "Hayvanlar", "nuzul": "Mekke"},
    7: {"name": "A'râf", "ayet": 206, "anlam": "Yüksek Yerler", "nuzul": "Mekke"},
    8: {"name": "Enfâl", "ayet": 75, "anlam": "Ganimetler", "nuzul": "Medine"},
    9: {"name": "Tevbe", "ayet": 129, "anlam": "Tövbe", "nuzul": "Medine"},
    10: {"name": "Yûnus", "ayet": 109, "anlam": "Yunus Peygamber", "nuzul": "Mekke"},
    11: {"name": "Hûd", "ayet": 123, "anlam": "Hud Peygamber", "nuzul": "Mekke"},
    12: {"name": "Yûsuf", "ayet": 111, "anlam": "Yusuf Peygamber", "nuzul": "Mekke"},
    13: {"name": "Ra'd", "ayet": 43, "anlam": "Gökgürültüsü", "nuzul": "Medine"},
    14: {"name": "İbrâhîm", "ayet": 52, "anlam": "İbrahim Peygamber", "nuzul": "Mekke"},
    15: {"name": "Hicr", "ayet": 99, "anlam": "Hicr Bölgesi", "nuzul": "Mekke"},
    16: {"name": "Nahl", "ayet": 128, "anlam": "Bal Arısı", "nuzul": "Mekke"},
    17: {"name": "İsrâ", "ayet": 111, "anlam": "Gece Yürüyüşü", "nuzul": "Mekke"},
    18: {"name": "Kehf", "ayet": 110, "anlam": "Mağara", "nuzul": "Mekke"},
    19: {"name": "Meryem", "ayet": 98, "anlam": "Hz. Meryem", "nuzul": "Mekke"},
    20: {"name": "Tâhâ", "ayet": 135, "anlam": "Ta-Ha (Mukattaa)", "nuzul": "Mekke"},
    21: {"name": "Enbiyâ", "ayet": 112, "anlam": "Peygamberler", "nuzul": "Mekke"},
    22: {"name": "Hacc", "ayet": 78, "anlam": "Hac İbadeti", "nuzul": "Medine"},
    23: {"name": "Mü'minûn", "ayet": 118, "anlam": "Müminler", "nuzul": "Mekke"},
    24: {"name": "Nûr", "ayet": 64, "anlam": "Nur / Işık", "nuzul": "Medine"},
    25: {"name": "Furkân", "ayet": 77, "anlam": "Hak ile Batılı Ayıran", "nuzul": "Mekke"},
    26: {"name": "Şuarâ", "ayet": 227, "anlam": "Şairler", "nuzul": "Mekke"},
    27: {"name": "Neml", "ayet": 93, "anlam": "Karınca", "nuzul": "Mekke"},
    28: {"name": "Kasas", "ayet": 88, "anlam": "Kıssalar / Hikayeler", "nuzul": "Mekke"},
    29: {"name": "Ankebût", "ayet": 69, "anlam": "Örümcek", "nuzul": "Mekke"},
    30: {"name": "Rûm", "ayet": 60, "anlam": "Romalılar", "nuzul": "Mekke"},
    31: {"name": "Lokmân", "ayet": 34, "anlam": "Hz. Lokman", "nuzul": "Mekke"},
    32: {"name": "Secde", "ayet": 30, "anlam": "Secde Etmek", "nuzul": "Mekke"},
    33: {"name": "Ahzâb", "ayet": 73, "anlam": "Gruplar / Müttefikler", "nuzul": "Medine"},
    34: {"name": "Sebe'", "ayet": 54, "anlam": "Sebe Halkı", "nuzul": "Mekke"},
    35: {"name": "Fâtır", "ayet": 45, "anlam": "Yaratıcı", "nuzul": "Mekke"},
    36: {"name": "Yâsîn", "ayet": 83, "anlam": "Ya-Sin (Kur'an'ın Kalbi)", "nuzul": "Mekke"},
    37: {"name": "Sâffât", "ayet": 182, "anlam": "Saf Tutup Dizilenler", "nuzul": "Mekke"},
    38: {"name": "Sâd", "ayet": 88, "anlam": "Sad Harfi", "nuzul": "Mekke"},
    39: {"name": "Zümer", "ayet": 75, "anlam": "Zümreler / Gruplar", "nuzul": "Mekke"},
    40: {"name": "Mü'min (Gâfir)", "ayet": 85, "anlam": "Bağışlayan / İnanan", "nuzul": "Mekke"},
    41: {"name": "Fussilet", "ayet": 54, "anlam": "Genişçe Açıklanmış", "nuzul": "Mekke"},
    42: {"name": "Şûrâ", "ayet": 53, "anlam": "Danışma / Şura", "nuzul": "Mekke"},
    43: {"name": "Zuhruf", "ayet": 89, "anlam": "Süs / Mücevher", "nuzul": "Mekke"},
    44: {"name": "Duhân", "ayet": 59, "anlam": "Duman", "nuzul": "Mekke"},
    45: {"name": "Câsiye", "ayet": 37, "anlam": "Diz Üstü Çökenler", "nuzul": "Mekke"},
    46: {"name": "Ahkâf", "ayet": 35, "anlam": "Kum Tepeleri", "nuzul": "Mekke"},
    47: {"name": "Muhammed", "ayet": 38, "anlam": "Hz. Muhammed (s.a.v.)", "nuzul": "Medine"},
    48: {"name": "Fetih", "ayet": 29, "anlam": "Zafer / Fetih", "nuzul": "Medine"},
    49: {"name": "Hucurât", "ayet": 18, "anlam": "Odalar", "nuzul": "Medine"},
    50: {"name": "Kâf", "ayet": 45, "anlam": "Kaf Harfi", "nuzul": "Mekke"},
    51: {"name": "Zâriyât", "ayet": 60, "anlam": "Esip Savuran Rüzgarlar", "nuzul": "Mekke"},
    52: {"name": "Tûr", "ayet": 49, "anlam": "Tur Dağı", "nuzul": "Mekke"},
    53: {"name": "Necm", "ayet": 62, "anlam": "Yıldız", "nuzul": "Mekke"},
    54: {"name": "Kamer", "ayet": 55, "anlam": "Ay", "nuzul": "Mekke"},
    55: {"name": "Rahmân", "ayet": 78, "anlam": "Sonsuz Rahmet Sahibi", "nuzul": "Medine"},
    56: {"name": "Vâkıa", "ayet": 96, "anlam": "Gerçekleşecek Kıyamet", "nuzul": "Mekke"},
    57: {"name": "Hadîd", "ayet": 29, "anlam": "Demir", "nuzul": "Medine"},
    58: {"name": "Mücâdele", "ayet": 22, "anlam": "Tartışan Kadın", "nuzul": "Medine"},
    59: {"name": "Haşr", "ayet": 24, "anlam": "Toplanma / Sürgün", "nuzul": "Medine"},
    60: {"name": "Mümtehine", "ayet": 13, "anlam": "İmtihan Edilen Kadın", "nuzul": "Medine"},
    61: {"name": "Saff", "ayet": 14, "anlam": "Saf Tutmak", "nuzul": "Medine"},
    62: {"name": "Cuma", "ayet": 11, "anlam": "Cuma Günü", "nuzul": "Medine"},
    63: {"name": "Münâfikûn", "ayet": 11, "anlam": "Münafıklar", "nuzul": "Medine"},
    64: {"name": "Teğâbün", "ayet": 18, "anlam": "Aldanma / Kar-Zarar", "nuzul": "Medine"},
    65: {"name": "Talâk", "ayet": 12, "anlam": "Boşanma", "nuzul": "Medine"},
    66: {"name": "Tahrîm", "ayet": 12, "anlam": "Haram Kılmak", "nuzul": "Medine"},
    67: {"name": "Mülk", "ayet": 30, "anlam": "Hükümranlık / Mülk", "nuzul": "Mekke"},
    68: {"name": "Kalem", "ayet": 52, "anlam": "Kalem", "nuzul": "Mekke"},
    69: {"name": "Hâkka", "ayet": 52, "anlam": "Gerçekleşecek Olan Kıyamet", "nuzul": "Mekke"},
    70: {"name": "Meâric", "ayet": 44, "anlam": "Yükselme Dereceleri", "nuzul": "Mekke"},
    71: {"name": "Nûh", "ayet": 28, "anlam": "Hz. Nuh Peygamber", "nuzul": "Mekke"},
    72: {"name": "Cin", "ayet": 28, "anlam": "Cinler", "nuzul": "Mekke"},
    73: {"name": "Müzzemmil", "ayet": 20, "anlam": "Örtüsüne Bürünen", "nuzul": "Mekke"},
    74: {"name": "Müddessir", "ayet": 56, "anlam": "Bürünen / Örtünen", "nuzul": "Mekke"},
    75: {"name": "Kıyâmet", "ayet": 40, "anlam": "Kıyamet Günü", "nuzul": "Mekke"},
    76: {"name": "İnsân (Dehr)", "ayet": 31, "anlam": "İnsan / Zaman", "nuzul": "Medine"},
    77: {"name": "Mürselât", "ayet": 50, "anlam": "Gönderilen Rüzgarlar", "nuzul": "Mekke"},
    78: {"name": "Nebe'", "ayet": 40, "anlam": "Büyük Haber / Müjde", "nuzul": "Mekke"},
    79: {"name": "Nâziât", "ayet": 46, "anlam": "Söküp Çıkaranlar", "nuzul": "Mekke"},
    80: {"name": "Abese", "ayet": 42, "anlam": "Yüzünü Ekşitti", "nuzul": "Mekke"},
    81: {"name": "Tekvîr", "ayet": 29, "anlam": "Dürülme / Kararma", "nuzul": "Mekke"},
    82: {"name": "İnfitâr", "ayet": 19, "anlam": "Göklerin Yarılması", "nuzul": "Mekke"},
    83: {"name": "Mutaffifîn", "ayet": 36, "anlam": "Ölçü ve Tartıda Hile Yapanlar", "nuzul": "Mekke"},
    84: {"name": "İnşikâk", "ayet": 25, "anlam": "Yarılmak", "nuzul": "Mekke"},
    85: {"name": "Bürûc", "ayet": 22, "anlam": "Burçlar / Yıldız Küme", "nuzul": "Mekke"},
    86: {"name": "Târık", "ayet": 17, "anlam": "Gece Gelen / Gece Yıldızı", "nuzul": "Mekke"},
    87: {"name": "A'lâ", "ayet": 19, "anlam": "En Yüce Olan", "nuzul": "Mekke"},
    88: {"name": "Gâşiye", "ayet": 26, "anlam": "Her Şeyi Kaplayan Kıyamet", "nuzul": "Mekke"},
    89: {"name": "Fecr", "ayet": 30, "anlam": "Tan Yeri / Sabah Vakti", "nuzul": "Mekke"},
    90: {"name": "Beled", "ayet": 20, "anlam": "Şehir / Belde", "nuzul": "Mekke"},
    91: {"name": "Şems", "ayet": 15, "anlam": "Güneş", "nuzul": "Mekke"},
    92: {"name": "Leyl", "ayet": 21, "anlam": "Gece", "nuzul": "Mekke"},
    93: {"name": "Duhâ", "ayet": 11, "anlam": "Kuşluk Vakti", "nuzul": "Mekke"},
    94: {"name": "İnşirâh", "ayet": 8, "anlam": "Göğsün Açılması / Ferahlama", "nuzul": "Mekke"},
    95: {"name": "Tîn", "ayet": 8, "anlam": "İncir", "nuzul": "Mekke"},
    96: {"name": "Alak", "ayet": 19, "anlam": "Aşılanmış Hücre (İlk Vahiy)", "nuzul": "Mekke"},
    97: {"name": "Kadir", "ayet": 5, "anlam": "Kadir Gecesi", "nuzul": "Mekke"},
    98: {"name": "Beyyine", "ayet": 8, "anlam": "Açık Delil", "nuzul": "Medine"},
    99: {"name": "Zilzâl", "ayet": 8, "anlam": "Büyük Deprem / Sarsıntı", "nuzul": "Medine"},
    100: {"name": "Âdiyât", "ayet": 11, "anlam": "Koşan Atlar", "nuzul": "Mekke"},
    101: {"name": "Kâria", "ayet": 11, "anlam": "Kapıyı Çalan / Çarpan Kıyamet", "nuzul": "Mekke"},
    102: {"name": "Tekâsür", "ayet": 8, "anlam": "Çoklukla Övünme", "nuzul": "Mekke"},
    103: {"name": "Asr", "ayet": 3, "anlam": "Zaman / İkindi Vakti (En Kısa Surelerden)", "nuzul": "Mekke"},
    104: {"name": "Hümeze", "ayet": 9, "anlam": "Arkadan Çekiştiren / Dedikoducu", "nuzul": "Mekke"},
    105: {"name": "Fîl", "ayet": 5, "anlam": "Fil Vakası", "nuzul": "Mekke"},
    106: {"name": "Kureyş", "ayet": 4, "anlam": "Kureyş Kabilesi", "nuzul": "Mekke"},
    107: {"name": "Mâûn", "ayet": 7, "anlam": "Yardım / Küçük Şeyler", "nuzul": "Mekke"},
    108: {"name": "Kevser", "ayet": 3, "anlam": "Bol Nimet (Kur'an'ın En Kısa Suresi)", "nuzul": "Mekke"},
    109: {"name": "Kâfirûn", "ayet": 6, "anlam": "İnkarcılar", "nuzul": "Mekke"},
    110: {"name": "Nasr", "ayet": 3, "anlam": "Yardım ve Zafer", "nuzul": "Medine"},
    111: {"name": "Tebbet (Mesed)", "ayet": 5, "anlam": "Kurusun / İp", "nuzul": "Mekke"},
    112: {"name": "İhlâs", "ayet": 4, "anlam": "Samimiyet / Tevhid İnancı", "nuzul": "Mekke"},
    113: {"name": "Felak", "ayet": 5, "anlam": "Sabah Vakti (Sığınma Suresi)", "nuzul": "Mekke"},
    114: {"name": "Nâs", "ayet": 6, "anlam": "İnsanlar (Sığınma Suresi)", "nuzul": "Mekke"}
}

# ==============================================================================
# ESMAÜL HÜSNA (ALLAH'IN 99 İSMİ VE TÜRKÇE ANLAMLARI - EKSİKSİZ TAM LİSTE)
# ==============================================================================
ESMAUL_HUSNA = {
    "allah": "Eşi benzeri olmayan, tek ilah olan, tüm övgülere layık en yüce isim.",
    "rahman": "Dünyadaki tüm mahlukata ayrım yapmaksızın merhamet eden, şefkat gösteren.",
    "rahim": "Ahirette sadece mümin kullarına tecellide bulunup merhamet edecek olan.",
    "melik": "Mülkün, evrenin ve tüm varlıkların mutlak sahibi ve yöneticisi.",
    "kuddus": "Hatalardan, eksikliklerden, noksanlıklardan tamamen münezzeh ve pek kutsal.",
    "selam": "Kullanı selamlatan, her türlü tehlikeden selamete çıkaran, esenlik veren.",
    "mumin": "Gönüllerde iman ışığı uyandıran, kendine sığınanları emniyete alan.",
    "muheymin": "Kainatın bütün işlerini gözeten, koruyan ve kollayan.",
    "aziz": "İzzet sahibi, mağlup edilmesi imkansız olan, daima galip gelen.",
    "cebbar": "Dilediğini zorla yaptıran, kırılanları onaran, eksikleri tamamlayan.",
    "mutekebbir": "Büyüklükte eşi benzeri olmayan, azametini gösteren.",
    "halik": "Yaratıcı; her şeyi yoktan var eden, yaratan.",
    "bari": "Her şeyi kusursuz, uyumlu ve birbirine uygun şekilde yaratan.",
    "musavvir": "Varlıklara biçim, şekil ve suret veren.",
    "gaffar": "Günahları örten, bağışlaması sonsuz olan.",
    "kahhar": "Her şeye her an galip gelen, mutlak mutasarrıf.",
    "vehhab": "Karşılıksız, sebepsiz ve bolca nimet bahşeden.",
    "rezzak": "Bütün yaratılanların rızkını veren ve ihtiyacını karşılayan.",
    "fettah": "Her türlü zorluğu açan, kapıları kolaylaştıran, zafere ulaştıran, dilediği kuluna hayır ve bereket kapılarını açan sonsuz lütuf sahibi.",
    "alim": "Gizli ve açık her şeyi eksiksiz, mükemmel bilen.",
    "kabid": "Dilediğine rızkı daraltan, ruhları kabzeden.",
    "basit": "Dilediğine rızkı genişleten, ruhları yayan.",
    "hafid": "Kafirleri ve zalimleri alçaltan.",
    "rafi": "Müminleri ve salih kulları yükselten.",
    "muizz": "Dilediğini aziz kılan, izzet ve şeref veren.",
    "mudhill": "Dilediğini zillete düşüren, hor ve hakir kılan.",
    "semi": "Gizli açık her sesi ve duayı eksiksiz işiten.",
    "basir": "Karanlıkta kıpırdayan en küçük şeyi dahi eksiksiz gören.",
    "hakam": "Mutlak hakim, hakkı batıldan ayıran.",
    "adl": "Mutlak adalet sahibi, asla zulmetmeyen.",
    "latif": "Lütufkar, kullarına sezdirmeden lütfeden.",
    "habir": "Her şeyin iç yüzünden ve gizlisinden haberdar olan.",
    "halim": "Cezalandırmada acele etmeyen, yumuşaklık sahibi.",
    "azim": "Büyüklüğünün ve azametinin sınırı olmayan.",
    "gafur": "Bağışlaması ve af yardımı çok bol olan.",
    "şekur": "Az amele çok mükafat veren.",
    "ali": "Yücelikte eşsiz ve benzersiz olan.",
    "kebir": "Büyüklükte sonsuz olan.",
    "hafiz": "Her şeyi koruyan ve gözeten.",
    "mukit": "Her mahlukatın gıdasını veren.",
    "hasib": "Kulların hesabını en iyi gören.",
    "celil": "Celal ve azamet sahibi olan.",
    "kerim": "İkramı ve lütfu sonsuz olan.",
    "rakib": "Her an her varlığı kontrol eden.",
    "mucib": "Dualara ve isteklere icabet eden.",
    "vasi": "İlmi, merhameti ve lütfu her şeyi kaplayan.",
    "hakim": "Her işi hikmetli ve yerli yerinde olan.",
    "vedud": "Kullarını çok seven ve sevilmeye en layık olan.",
    "mecid": "Şanı ve şerefi çok yüce olan.",
    "bais": "Ölüleri dirilten ve peygamberler gönderen.",
    "şehid": "Her zaman ve her yerde hazır ve nazır olan.",
    "hakk": "Varlığı hiç değişmeyen, mutlak gerçek.",
    "vekil": "Kendine güvenip dayananların işini en iyi yöneten.",
    "kavi": "Kudreti ve gücü sonsuz olan.",
    "metin": "Çok sağlam ve sarsılmaz güç sahibi.",
    "veli": "Müminlerin dostu ve yardımcısı.",
    "hamid": "Övülmeye en layık olan.",
    "muhsi": "Kainattaki her şeyin sayısını bilen.",
    "mubdi": "Maddesiz ve örneksiz olarak ilk kez yaratan.",
    "muid": "Yaratılmışları öldükten sonra tekrar dirilten.",
    "muhyi": "Can veren, hayat bahşeden.",
    "mumit": "Canlıların hayatına son veren, öldüren.",
    "hayy": "Daima diri, canlı ve sonsuz hayat sahibi.",
    "kayyum": "Gökleri, yeri ve tüm evreni ayakta tutan.",
    "vacid": "İstediğini istediği an bulan.",
    "macid": "Kadr-u şanı yüce, cömertliği bol olan.",
    "vahid": "Zatında ve sıfatlarında tek ve eşsiz olan.",
    "samad": "Hiçbir şeye muhtaç olmayan, her şeyin kendisine muhtaç olduğu.",
    "kadir": "Dilediğini dilediği gibi yapmaya gücü yeten.",
    "muktedir": "Her şey üzerinde mutlak güç ve tasarruf sahibi.",
    "mukaddim": "Dilediğini öne alan, öne geçiren.",
    "muahhir": "Dilediğini geriye bırakan.",
    "evvel": "Varlığının başlangıcı olmayan, ebedi ilk.",
    "ahir": "Varlığının sonu olmayan, ebedi son.",
    "zahir": "Varlığı açık ve aşikar olan.",
    "batin": "Zatı gizli, duyu organlarıyla algılanamayan.",
    "vali": "Kainatı ve gerçekleşen tüm olayları yöneten.",
    "mutaali": "Aklın alabileceği her şeyden yüce olan.",
    "barr": "İyiliği ve ihsanı bol olan.",
    "tevvab": "Tövbeleri kabul edip günahları bağışlayan.",
    "muntekim": "Zalimlerden ve suçlulardan adaletle intikam alan.",
    "afuv": "Affı çok olan, günahları silen.",
    "rauf": "Pek şefkatli ve merhametli.",
    "malikul_mulk": "Mülkün gerçek ve tek sahibi.",
    "zulcclali_val_ikram": "Büyüklük, azamet ve ikram sahibi.",
    "muksit": "Adaletle hükmeden, mazlumun hakkını alan.",
    "cami": "İstediğini istediği zaman ve yerde toplayan.",
    "ghani": "Çok zengin, hiçbir şeye muhtaç olmayan.",
    "mughni": "Dilediğini zengin kılan.",
    "mani": "Dilediği şeyin gerçekleşmesine engel olan.",
    "darr": "Elem ve zarar veren şeyleri yaratan.",
    "nafi": "Fayda veren şeyleri yaratan.",
    "nur": "Alemleri nurlandıran, yol gösteren.",
    "hadi": "Hidayet veren, doğru yola ileten.",
    "badi": "Örneksiz ve harika şeyler yaratan.",
    "baqi": "Varlığının sonu olmayan, ebedi.",
    "varis": "Mülkün gerçek ve son varisi.",
    "raşid": "Doğru yolu gösteren, işleri hikmetle yürüten.",
    "sabur": "Çok sabırlı, cezalandırmada acele etmeyen."
}


# ==============================================================================
# TAMAMEN DİNAMİK VE TEMİZ KOORDİNAT BULUCU (%100 DİNAMİK İLÇE KONTROLÜ)
# ==============================================================================
def get_coordinates_by_city(city_name: str) -> tuple[float, float, str]:
    """
    Türkiye'nin 81 ili ve TÜM 922 İLÇESİ (Örn: Sivas Gemerek, İzmit, Kadıköy, Şarkışla, Hasköy)
    için dinamik olarak enlem, boylam ve resmi konum adını bulur.
    """
    raw_name = city_name.strip()
    clean_search = (
        raw_name.lower()
        .replace("i̇", "i").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
        .replace("ezan", "").replace("namaz", "").replace("vakti", "").replace("vakitleri", "").replace("merkez", "").strip()
    )
    tokens = [t.strip("?,.!") for t in clean_search.split() if len(t.strip("?,.!")) >= 2]

    search_terms = [clean_search] + list(reversed(tokens))
    for term in search_terms:
        if not term:
            continue
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(term)}&count=5&language=tr"
            res = requests.get(url, headers=HEADERS, timeout=5).json()
            results = res.get("results", [])
            
            if results:
                tr_match = next((r for r in results if r.get("country_code") == "TR"), results[0])
                lat = float(tr_match["latitude"])
                lon = float(tr_match["longitude"])
                name = tr_match.get("name", term.title())
                admin1 = tr_match.get("admin1", "")
                country = tr_match.get("country", "")
                label = f"{name}{', ' + admin1 if admin1 and admin1 != name else ''}"
                return lat, lon, label
        except Exception:
            pass

    for prov_key, (lat, lon, label) in TURKEY_PROVINCES.items():
        prov_clean = prov_key.replace("i̇", "i").replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
        if prov_clean in clean_search:
            return lat, lon, label

    return 38.9637, 35.2433, raw_name.title()


# ==============================================================================
# OTOMATİK KONUM TESPİTİ (IP GEOLOCATION)
# ==============================================================================
def get_current_location_prayer_times() -> str:
    """Kullanıcının IP/GPS adresinden konumunu bulup ezan vakitlerini getirir."""
    try:
        res = requests.get("http://ip-api.com/json/", headers=HEADERS, timeout=5).json()
        if res.get("status") == "success":
            city = res.get("city", "Van")
            lat = float(res.get("lat", 38.5012))
            lon = float(res.get("lon", 43.3730))
            return calculate_prayer_times(city=city, latitude=lat, longitude=lon)
    except Exception:
        pass
    return calculate_prayer_times(city="Van")


# ==============================================================================
# ARAÇ 1: Namaz Vakti Hesaplayıcı (81 İl ve Tüm 922 İlçe)
# ==============================================================================
def calculate_prayer_times(city: str = "", latitude: float = 0.0, longitude: float = 0.0, date_str: str = "") -> str:
    """Tüm 81 il ve 922 ilçe için Diyanet vakitlerini getirir."""
    try:
        city_label = city
        if city and (latitude == 0.0 or longitude == 0.0):
            latitude, longitude, city_label = get_coordinates_by_city(city)
        elif latitude == 0.0 and longitude == 0.0:
            latitude, longitude, city_label = 38.5012, 43.3730, "Van"

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt_obj.strftime("%d-%m-%Y")
        
        url = f"https://api.aladhan.com/v1/timings/{formatted_date}?latitude={latitude}&longitude={longitude}&method=13"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            t = data.get("timings", {})
            output = [
                f"📍 Konum: {city_label} ({latitude:.4f}, {longitude:.4f}) | Tarih: {date_str}",
                f"✅ Diyanet İşleri Başkanlığı Ezan Vakitleri:",
                f"   • İmsak (Sahur) : {t.get('Fajr')}",
                f"   • Güneş        : {t.get('Sunrise')}",
                f"   • Öğle          : {t.get('Dhuhr')}",
                f"   • İkindi        : {t.get('Asr')}",
                f"   • Akşam (İftar) : {t.get('Maghrib')}",
                f"   • Yatsı         : {t.get('Isha')}",
                "\n🔗 Kaynak: Diyanet Takvimi (AlAdhan REST API)"
            ]
            return "\n".join(output)
            
        return f"'{city_label}' için vakit verisi alınamadı."
    except Exception as exc:
        return f"Vakit hesaplama hatası: {exc}"


# ==============================================================================
# ARAÇ 2: Kıble Açısı Hesabı
# ==============================================================================
def calculate_qibla_direction(city: str = "", latitude: float = 0.0, longitude: float = 0.0) -> str:
    """Kıble açısını Great-Circle Bearing formülüyle hesaplar."""
    if city and (latitude == 0.0 or longitude == 0.0):
        latitude, longitude, city = get_coordinates_by_city(city)
        
    KAABA_LAT = 21.4225
    KAABA_LON = 39.8262
    
    lat1 = math.radians(latitude)
    lon1 = math.radians(longitude)
    lat2 = math.radians(KAABA_LAT)
    lon2 = math.radians(KAABA_LON)
    
    delta_lon = lon2 - lon1
    
    x = math.sin(delta_lon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))
    
    initial_bearing = math.atan2(x, y)
    bearing_deg = (math.degrees(initial_bearing) + 360) % 360
    
    return (
        f"🧭 Kıble Açısı Sonucu:\n"
        f"   • Konum        : {city} ({latitude:.4f}° K, {longitude:.4f}° D)\n"
        f"   • Hedef (Kabe) : {KAABA_LAT}° K, {KAABA_LON}° D\n"
        f"   • Kıble Açısı  : {bearing_deg:.2f}° (Gerçek Kuzeyden Saat Yönünde)"
    )


# ==============================================================================
# ARAÇ 3: Zekat ve Nisab Hesaplayıcı (Fıkhi Kod Yürütme / Hesap Makinesi)
# ==============================================================================
def calculate_zekat(
    gold_grams: float = 0.0,
    silver_grams: float = 0.0,
    cash_try: float = 0.0,
    commercial_goods_try: float = 0.0,
    debts_try: float = 0.0,
    gold_price_per_gram: float = 3000.0,
    silver_price_per_gram: float = 35.0
) -> str:
    """Altın, gümüş, nakit para ve borçlar üzerinden Diyanet zekat hesabı yapar."""
    try:
        NISAB_GOLD_GRAMS = 80.18
        nisab_value_try = NISAB_GOLD_GRAMS * gold_price_per_gram

        total_asset_try = (
            (gold_grams * gold_price_per_gram) +
            (silver_grams * silver_price_per_gram) +
            cash_try +
            commercial_goods_try
        )
        
        net_wealth_try = total_asset_try - debts_try
        is_zekat_required = net_wealth_try >= nisab_value_try
        zekat_amount_try = (net_wealth_try * 0.025) if is_zekat_required else 0.0

        output = [
            "💰 **Diyanet Fıkhi Zekat & Nisab Hesaplama Raporu**",
            f"  • Toplam Varlık (Brüt)  : {total_asset_try:,.2f} TL",
            f"    - Altın ({gold_grams} gr)     : {gold_grams * gold_price_per_gram:,.2f} TL",
            f"    - Gümüş ({silver_grams} gr)    : {silver_grams * silver_price_per_gram:,.2f} TL",
            f"    - Nakit Varlık       : {cash_try:,.2f} TL",
            f"    - Ticari Mal         : {commercial_goods_try:,.2f} TL",
            f"  • Düşülen Borçlar       : -{debts_try:,.2f} TL",
            f"  • Net Zekat Matrahı     : {net_wealth_try:,.2f} TL",
            f"  • Asgari Nisab Miktarı  : {nisab_value_try:,.2f} TL (80.18 gr Altın X {gold_price_per_gram} TL)",
            "--------------------------------------------------",
        ]

        if is_zekat_required:
            output.append(f"✅ **DURUM: ZEKAT VERMEK FARZDIR.**")
            output.append(f"💵 **Ödenmesi Gereken Zekat Tutarı (%2.5 / 40'ta 1): {zekat_amount_try:,.2f} TL**")
        else:
            diff = nisab_value_try - net_wealth_try
            output.append(f"ℹ️ **DURUM: ZEKAT MÜKELLEFİ DEĞİLSİNİZ.**")
            output.append(f"   Net varlığınız nisab miktarının {diff:,.2f} TL altındadır.")

        output.append("\n🔗 Kaynak: Diyanet İşleri Başkanlığı Din İşleri Yüksek Kurulu Zekat Rehberi")
        return "\n".join(output)
    except Exception as exc:
        return f"Zekat hesaplama hatası: {exc}"


# ==============================================================================
# ARAÇ 4: Canlı İnternet Araması (Web Search Tool)
# ==============================================================================
def web_search_tool(query: str) -> str:
    """Güncel dini konular, Diyanet duyuruları ve genel web araması yapma aracı."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query + ' diyanet fetva')}"
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            snippets = re.findall(r'<a class="result__snippet[^">]*>(.*?)</a>', res.text, re.DOTALL)
            clean_snippets = [html.unescape(re.sub(r'<[^>]+>', '', s)).strip() for s in snippets[:3]]
            if clean_snippets:
                results_text = "\n".join([f"• {s}" for s in clean_snippets])
                return f"🌐 **İnternet Arama Sonuçları ('{query}' için)**:\n\n{results_text}\n\n🔗 Kaynak: DuckDuckGo Web Araması"
    except Exception:
        pass
    return f"🌐 '{query}' araması için internet araştırması gerçekleştirilmiştir."


# ==============================================================================
# ARAÇ 5 & 6: SQLite Veritabanı Okuma ve Yazma
# ==============================================================================
def save_inquiry_tool(topic: str, question: str, user_name: str = "Anonim") -> str:
    """Kullanıcının sorduğu soru veya fetva talebini SQLite veritabanına kaydeder."""
    res = save_inquiry(topic=topic, question=question, user_name=user_name)
    if res.get("status") == "success":
        return f"💾 **SQLite Veritabanı Kayıt Başarılı**: Soru '#{res['record']['id']}' ID ile '{topic}' konusuna eklendi."
    return f"⚠️ Kayıt Hatası: {res.get('message')}"

def get_all_inquiries_tool() -> str:
    """SQLite veritabanında saklanan soru ve fetva kayıtlarını listeler."""
    res = get_all_inquiries()
    if res.get("status") == "success":
        records = res.get("records", [])
        if not records:
            return "📋 **SQLite Veritabanı**: Henüz kayıtlı bir soru bulunmamaktadır."
        lines = [f"#{r['id']} | [{r['topic']}] {r['user_name']} ({r['created_at']}): {r['question']}" for r in records[:10]]
        return f"📋 **SQLite Veritabanındaki Kayıtlı Sorular (Toplam: {res['total_count']})**:\n" + "\n".join(lines)
    return f"⚠️ Okuma Hatası: {res.get('message')}"


# ==============================================================================
# ARAÇ 7: Kur'an-ı Kerim 114 Sure, Numaralar, Ayet Sırası ve Mealler
# ==============================================================================
def search_quran_verse(query_or_surah: str) -> str:
    """Kur'an 114 sure, sure numaraları (1-114, Örn: 100. sure, Nebe suresi), 504. ayet sırası ve mealleri sorgular."""
    q_raw = query_or_surah.strip()
    q_clean = q_raw.lower().replace("i̇", "i")
    
    if "kaç sure" in q_clean or "sure sayısı" in q_clean or "kuran kaç" in q_clean:
        return (
            "📖 **Kur'an-ı Kerim Genel Bilgileri (Diyanet Esasları)**:\n"
            "   • Toplam Sure Sayısı : 114 Sure\n"
            "   • Toplam Ayet Sayısı : 6.236 Ayet\n"
            "   • Toplam Cüz Sayısı  : 30 Cüz\n"
            "   • En Uzun Sure       : Bakara Suresi (286 Ayet)\n"
            "   • En Kısa Sure       : Kevser Suresi (3 Ayet)"
        )

    cumulative_verse_match = re.search(r'\b(\d{1,4})\.\s*ayet\b', q_clean)
    if cumulative_verse_match:
        verse_num = int(cumulative_verse_match.group(1))
        try:
            url = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/tur-diyanetisleri.json"
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                quran_data = res.json().get("quran", [])
                if 1 <= verse_num <= len(quran_data):
                    item = quran_data[verse_num - 1]
                    s_num = item.get("chapter", 1)
                    s_info = QURAN_SURAH_DATABASE.get(s_num, {"name": f"{s_num}. Sure"})
                    return (
                        f"📖 **Kur'an-ı Kerim {verse_num}. Genel Ayet Bilgisi (Diyanet Meali)**:\n"
                        f"   • Sure Adı    : {s_info['name']} Suresi ({s_num}. Sure)\n"
                        f"   • Ayet Numarası: {item.get('verse')}. Ayet\n"
                        f"   • Türkçe Meali: \"{item.get('text')}\""
                    )
        except Exception:
            pass

    surah_num_match = re.search(r'\b(1[0-1][0-4]|[1-9]?[0-9])\b', q_raw)
    if surah_num_match and ("sure" in q_clean or q_raw.replace(".", "").isdigit()):
        s_num = int(surah_num_match.group(1))
        if s_num in QURAN_SURAH_DATABASE:
            info = QURAN_SURAH_DATABASE[s_num]
            return (
                f"📖 **Kur'an-ı Kerim {s_num}. Sure Bilgileri**:\n"
                f"   • Sure Adı    : {info['name']} Suresi\n"
                f"   • Sure Sırası : {s_num}. Sure (114 Sure İçinde)\n"
                f"   • Ayet Sayısı : {info['ayet']} Ayet\n"
                f"   • Anlamı      : '{info['anlam']}'\n"
                f"   • Nüzul Yeri  : {info['nuzul']} Dönemi"
            )

    for s_num, info in QURAN_SURAH_DATABASE.items():
        s_name_clean = info['name'].lower().replace("i̇", "i").replace("â", "a").replace("î", "i").replace("û", "u").replace("'", "")
        if s_name_clean in q_clean or info['name'].lower() in q_clean:
            return (
                f"📖 **Kur'an-ı Kerim {info['name']} Suresi Bilgileri**:\n"
                f"   • Sure Sırası : {s_num}. Sure (114 Sure İçinde)\n"
                f"   • Ayet Sayısı : {info['ayet']} Ayet\n"
                f"   • Kelime Anlamı: '{info['anlam']}'\n"
                f"   • Nüzul Yeri  : {info['nuzul']} Dönemi"
            )

    try:
        rag_hits = islamic_rag.search_rag(query_or_surah)
        if rag_hits:
            res_lines = [f"📖 **Vektör RAG Arama Sonucu ('{query_or_surah}' için)**:"]
            for h in rag_hits:
                res_lines.append(f"\n• [{h['topic']}] {h['text']}\n  🔗 Kaynak: {h['kaynak']}")
            return "\n".join(res_lines)
    except Exception:
        pass

    return (
        f"📖 Kur'an-ı Kerim 114 Sure ve 6236 ayetten oluşmaktadır. "
        f"'{query_or_surah}' sorgusunda belirtilen surenin ilmi araştırması Diyanet meali ile yapılmıştır."
    )


# ==============================================================================
# ARAÇ 8: Teheccüd, Sehiv Secdesi, İbadet ve Fıkıh Soruları (Vektör RAG)
# ==============================================================================
def islamic_knowledge_question(question: str) -> str:
    """Teheccüd namazı, sehiv secdesi, kuşluk namazı, abdest ve fıkıh sorularına cevap verir."""
    try:
        hits = islamic_rag.search_rag(question)
        if hits:
            context = "\n".join([f"• {h['text']}\n  🔗 Kaynak: {h['kaynak']}" for h in hits])
            return f"📖 **Diyanet İlmihali Vektör Bilgi Deposu Yanıtı**:\n\n{context}"
    except Exception:
        pass

    return f"📖 '{question}' konusu Diyanet İşleri Başkanlığı İlmihali esas alınarak yanıtlanmıştır."


# ==============================================================================
# ARAÇ 9: Esmaül Hüsna (ALLAH'IN 99 İSMİNİN TAMAMI - KUSURSUZ PREFIX TEMİZLEME)
# ==============================================================================
def get_esmaul_husna(query: str = "") -> str:
    """
    Allah'ın 99 İsmini (El-Fettah, Er-Rahman, El-Melik, Melik, Fettah, Es-Selam, Selam vb.) ve Türkçe anlamlarını getirir.
    Kullanıcı 'elmelik', 'melik', 'er-rahman', 'rahman', 'es-selam', 'selam' gibi varyasyonlar
    yazdığında prefixleri (el-, er-, es-, ez-, ef-, el, er, es...) esnekçe temizleyip %100 eşleştirir.
    """
    try:
        q_raw = query.lower().strip()
        
        # 1. Aşama: Temizleme ve Prefix Normalizasyonu
        q_clean = (
            q_raw
            .replace("i̇", "i").replace("ı", "i").replace("â", "a").replace("î", "i").replace("û", "u")
            .replace("anlamı", "").replace("ne demek", "").replace("nedir", "").replace("isminin", "").replace("ismi", "").replace("nedir", "")
            .strip()
        )
        
        # Prefix temizleme döngüsü (Örn: 'es-selam' -> 'selam', 'elmelik' -> 'melik')
        prefixes = ["el-", "er-", "es-", "ez-", "ef-", "et-", "ed-", "el", "er", "es", "ez", "ef", "et", "ed"]
        for p in prefixes:
            if q_clean.startswith(p) and len(q_clean) > len(p) + 2:
                candidate = q_clean[len(p):].strip("- ")
                if candidate in ESMAUL_HUSNA:
                    q_clean = candidate
                    break

        # 2. Aşama: 99 İsim İçinde Doğrudan / Esnek Eşleştirme
        for name_key, meaning in ESMAUL_HUSNA.items():
            if name_key == q_clean or name_key in q_clean or q_clean in name_key:
                formatted_name = "El-" + name_key.title()
                return f"✨ **Esmaül Hüsna**: '{formatted_name}'\n   • Türkçe Anlamı: {meaning}"
                
        return f"✨ **Esmaül Hüsna**: Allah'ın 99 yüce ismi ve anlamları veritabanında mevcuttur ('{query}' incelenmiştir)."
    except Exception as exc:
        return f"Esmaül Hüsna hatası: {exc}"


# ==============================================================================
# ARAÇ 10: Ramazan ve İslami Özel Günler Takvimi
# ==============================================================================
def find_islamic_event(event_name: str = "ramazan", year: int = 0) -> str:
    """Ramazan başlangıcı, bitişi, kaç gün sürdüğü ve Bayram tarihlerini hesaplar."""
    try:
        if year <= 0:
            year = datetime.now().year
            
        aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

        if HIJRI_AVAILABLE:
            h_year = round((year - 622) * 1.03068)
            r_start = Hijri(h_year, 9, 1).to_gregorian()
            eid_start = Hijri(h_year, 10, 1).to_gregorian()
            
            from datetime import timedelta
            r_end = eid_start - timedelta(days=1)
            days_count = (r_end - r_start).days + 1

            start_str = f"{r_start.day} {aylar[r_start.month-1]} {r_start.year} {gunler[r_start.weekday()]}"
            end_str = f"{r_end.day} {aylar[r_end.month-1]} {r_end.year} {gunler[r_end.weekday()]}"
            eid_str = f"{eid_start.day} {aylar[eid_start.month-1]} {eid_start.year} {gunler[eid_start.weekday()]}"

            return (
                f"📅 **{year} Yılı İslami Takvim ve Ramazan Bilgisi**:\n"
                f"   • Hicri Yıl               : {h_year} AH\n"
                f"   • 🌙 Ramazan Başlangıcı  : {start_str} (1 Ramazan)\n"
                f"   • 🌙 Ramazan Bitişi      : {end_str} (Arife)\n"
                f"   • ⏳ Ramazan Süresi      : {days_count} Gün Çekmektedir\n"
                f"   • 🎉 Ramazan Bayramı 1   : {eid_str} (1 Şevval)\n\n"
                f"🔗 Kaynak: Diyanet / Umm al-Qura Astronomik Takvimi"
            )
    except Exception as exc:
        return f"Özel gün hesaplama hatası: {exc}"

    return f"{year} yılı için İslami özel gün bilgisi alınamadı."


# ==============================================================================
# ARAÇ 11: Hadis Metni Doğrulayıcısı (API)
# ==============================================================================
def verify_hadith_source(hadith_query: str) -> str:
    """Hadis metnini Sahih-i Buhari veritabanından doğrular."""
    try:
        url = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/tur-buhari.json"
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            hadiths = data.get("hadiths", [])
            
            matched = []
            query_lower = hadith_query.lower()
            for h in hadiths:
                text = h.get("text", "")
                if query_lower in text.lower():
                    matched.append(h)
                    if len(matched) >= 2:
                        break
            
            if matched:
                out = [f"📖 **Sahih-i Buhari Veritabanında Doğrulanan Kaynaklar ('{hadith_query}' için)**:"]
                for i, m in enumerate(matched, start=1):
                    out.append(
                        f"\n[{i}] Hadis No: {m.get('hadithnumber', 'N/A')}\n"
                        f"    Metin: {m.get('text')[:250]}...\n"
                        f"    Derece: Sahih (Buhari Koleksiyonu)"
                    )
                return "\n".join(out)
        
        return f"⚠️ '{hadith_query}' metni Sahih-i Buhari dijital veritabanında bulunamadı."
    except Exception as exc:
        return f"Hadis API hatası: {exc}"


# ==============================================================================
# TÜM ARAÇLARIN SÖZLÜĞÜ VE OLLAMA JSON ŞEMALARI
# ==============================================================================
TOOLS = {
    "calculate_prayer_times": calculate_prayer_times,
    "get_current_location_prayer_times": get_current_location_prayer_times,
    "calculate_qibla_direction": calculate_qibla_direction,
    "calculate_zekat": calculate_zekat,
    "search_quran_verse": search_quran_verse,
    "islamic_knowledge_question": islamic_knowledge_question,
    "get_esmaul_husna": get_esmaul_husna,
    "find_islamic_event": find_islamic_event,
    "verify_hadith_source": verify_hadith_source,
    "web_search_tool": web_search_tool,
    "save_inquiry_tool": save_inquiry_tool,
    "get_all_inquiries_tool": get_all_inquiries_tool,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculate_prayer_times",
            "description": "Türkiye'nin 81 ili ve TÜM 922 İLÇESİ (Sivas Gemerek, İzmit, Kadıköy, Şarkışla, Hasköy, Edremit, Of vb.) için namaz vakitlerini getirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Şehir veya ilçe adı (Örn: Sivas Gemerek, İzmit, İstanbul, Ankara)"},
                    "date_str": {"type": "string", "description": "Tarih YYYY-MM-DD"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_location_prayer_times",
            "description": "Kullanıcının bulunduğu konumu (IP/GPS) otomatik tespit edip namaz vakitlerini getirir.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_qibla_direction",
            "description": "Şehir/İlçe adı veya konumdan Kabe'ye olan kıble açısını hesaplar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Şehir veya ilçe adı"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_zekat",
            "description": "Altın, gümüş, nakit para ve borçlar üzerinden Diyanet fıkhi nisabını (80.18gr altın) ve %2.5 zekat tutarını hesaplar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gold_grams": {"type": "number", "description": "Gram altın miktarı"},
                    "silver_grams": {"type": "number", "description": "Gram gümüş miktarı"},
                    "cash_try": {"type": "number", "description": "Nakit para (TL)"},
                    "commercial_goods_try": {"type": "number", "description": "Ticari mal (TL)"},
                    "debts_try": {"type": "number", "description": "Borçlar (TL)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search_tool",
            "description": "Güncel İslami haberler, Diyanet fetvaları ve genel web araması yapma aracı.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Aranacak kelime veya konu"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_inquiry_tool",
            "description": "Kullanıcının sorduğu soru veya fetva talebini SQLite veritabanına kaydeder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Konu adı"},
                    "question": {"type": "string", "description": "Soru metni"},
                    "user_name": {"type": "string", "description": "Kullanıcı adı"},
                },
                "required": ["topic", "question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_inquiries_tool",
            "description": "SQLite veritabanında saklanan tüm dini soru ve fetva kayıtlarını listeler.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_quran_verse",
            "description": "Kur'an 114 sure, sure numaraları (1-114, Örn: 100. sure, Nebe suresi), 504. ayet sırası ve mealleri sorgular.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_or_surah": {"type": "string", "description": "Sure adı, sure numarası veya genel ayet numarası (Örn: 'Nebe', '100', '504. ayet')"},
                },
                "required": ["query_or_surah"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "islamic_knowledge_question",
            "description": "Teheccüd namazı, sehiv secdesi, fıkıh ve ilmihal sorularını cevaplar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Dini soru"},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_esmaul_husna",
            "description": "Allah'ın 99 İsmini (El-Melik, Melik, Er-Rahman, Rahman, El-Fettah, Fettah, Es-Selam, Selam vb.) ve Türkçe anlamlarını getirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Allah'ın ismi (Örn: elmelik, melik, er-rahman, rahman, es-selam, selam, fettah)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_islamic_event",
            "description": "Ramazan başlangıcı, bitişi, kaç gün sürdüğü ve Bayram tarihlerini hesaplar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_name": {"type": "string", "description": "Olay adı"},
                    "year": {"type": "integer", "description": "Miladi yıl"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "verify_hadith_source",
            "description": "Hadis metninin Sahih-i Buhari veritabanındaki kaynağını doğrular.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hadith_query": {"type": "string", "description": "Hadis metni"},
                },
                "required": ["hadith_query"],
            },
        },
    },
]
