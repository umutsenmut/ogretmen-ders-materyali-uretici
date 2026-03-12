# 📚 Öğretmen Ders Materyali Üretim Sistemi

Teknik öğretmenler için yıllık ders planı yönetimi ve yapay zeka destekli materyal üretim uygulaması.

---

## 🎯 Ne Yapar?

Bu uygulama ile şunları yapabilirsiniz:

| Özellik | Açıklama |
|---------|----------|
| 📂 **Yıllık Plan Yükleme** | PDF, Word (.docx) veya Excel (.xlsx) formatındaki yıllık planınızı sisteme yükleyin. Tablo yapısı otomatik okunur. |
| 🗓️ **Haftalık Ders Programı** | Pazartesi–Cuma arası derslerinizi girin. Bugün ve yarının dersleri otomatik vurgulanır. |
| 🤖 **Materyal Üretimi** | Bir ders konusu ve kazanım girerek yapay zeka ile bilgi kartı, sunum, test ve öğretmen notu üretin. |
| 📥 **İndirme** | Üretilen materyalleri PDF, Word, HTML veya TXT formatında indirin. |

---

## ⚙️ Gereksinimler

- **Python 3.9 veya üzeri** (3.10, 3.11, 3.12 de çalışır)
- **pip** (Python ile birlikte gelir)
- İnternet bağlantısı (yapay zeka özelliği için OpenAI veya Google Gemini hesabı)

> **Python kurulu değilse:** https://www.python.org/downloads/ adresine gidip işletim sisteminize uygun sürümü indirin. Kurulum sırasında **"Add Python to PATH"** seçeneğini mutlaka işaretleyin.

---

## 🚀 Kurulum (Adım Adım)

### 1. Dosyaları Bilgisayarınıza İndirin

Eğer Git yüklüyse terminalde şunu çalıştırın:

```bash
git clone https://github.com/umutsenmut/ogretmen-ders-materyali-uretici.git
cd ogretmen-ders-materyali-uretici
```

Git yoksa GitHub sayfasında yeşil **"Code"** butonuna tıklayıp **"Download ZIP"** seçin, ardından zip dosyasını açın ve klasöre girin.

---

### 2. Sanal Ortam (Virtual Environment) Oluşturun

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> Başarılı olursa komut satırının başında `(venv)` ibaresi görünür.

---

### 3. Gerekli Kütüphaneleri Kurun

```bash
pip install -r requirements.txt
```

Bu komut yaklaşık 2–5 dakika sürer, internet bağlantısı gerektirir.

---

### 4. Yapılandırma Dosyasını Oluşturun

`.env.example` dosyasını kopyalayarak `.env` adıyla kaydedin:

**Windows:**
```cmd
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Ardından `.env` dosyasını bir metin editörüyle açın (Not Defteri, VS Code vb.) ve düzenleyin:

```
OPENAI_API_KEY=sk-buraya-api-anahtarinizi-yazin
SECRET_KEY=gizli-bir-sifre-yazin
```

> **API anahtarı olmadan da çalışır!** Anahtar yoksa sistem hazır şablon içerikler üretir. Gerçek yapay zeka içerikleri için bir sonraki bölümü okuyun.

---

### 5. Uygulamayı Başlatın

```bash
python app.py
```

Terminal şöyle bir çıktı gösterirse uygulama hazırdır:

```
 * Running on http://127.0.0.1:5000
```

Tarayıcınızda (Chrome, Firefox vb.) şu adresi açın:

**[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Yapay Zeka API Anahtarı Alma (İsteğe Bağlı)

API anahtarı olmadan uygulama çalışır; ancak üretilen içerikler gerçek yapay zeka yerine hazır şablonlardan oluşur.
Gerçek, konuya özel içerik üretmek için aşağıdaki iki seçenekten **birini** kullanabilirsiniz:

---

### Seçenek A — Google Gemini (Ücretsiz kota ile başla)

1. **https://aistudio.google.com/app/apikey** adresine gidin (Google hesabıyla giriş yapın).
2. **"Create API Key"** butonuna tıklayın.
3. Oluşan anahtarı kopyalayın.
4. `.env` dosyasını açın ve `GEMINI_API_KEY=` satırının sağına yapıştırın:
   ```
   GEMINI_API_KEY=AIzaSy...buraya-anahtarinizi-yazin
   ```
5. Uygulamayı yeniden başlatın (`Ctrl+C` ile durdurup tekrar `python app.py`).

> **Maliyet:** Gemini 1.5 Flash modeli **ücretsiz kotayla** gelir (dakikada 15 istek, aylık 1 milyon token). Okul kullanımı için yeterlidir.

---

### Seçenek B — OpenAI (GPT-3.5)

1. **https://platform.openai.com/signup** adresine gidin ve ücretsiz hesap oluşturun.
2. Sol menüden **"API keys"** seçin → **"Create new secret key"** butonuna tıklayın.
3. Oluşan `sk-...` ile başlayan anahtarı kopyalayın.
4. `.env` dosyasını açın ve `OPENAI_API_KEY=` satırının sağına yapıştırın:
   ```
   OPENAI_API_KEY=sk-...buraya-anahtarinizi-yazin
   ```
5. Uygulamayı yeniden başlatın.

> **Maliyet:** GPT-3.5-turbo ile her materyal üretimi yaklaşık **0,01–0,05 USD** tutar. Ücretsiz kayıt kredisi genellikle 5 USD'dir.

---

> **Not:** Her iki anahtar da tanımlıysa OpenAI önceliklidir. Materyal üretim sayfasında hangi yapay zekanın aktif olduğunu görebilirsiniz.

---

## 📖 Kullanım Kılavuzu

### 1️⃣ Yıllık Planı Yükleme

1. Sol üst menüden **"Yıllık Plan"** bağlantısına tıklayın veya **[http://localhost:5000/upload-plan](http://localhost:5000/upload-plan)** adresine gidin.
2. **"Ders Adı"** alanına dersin adını yazın (örn: `Araç Teknolojisi Atölyesi`).
3. **"Eğitim Yılı"** alanına yılı yazın (örn: `2024-2025`).
4. Dosyanızı seçmek için **"Dosya Seç"** butonuna tıklayın veya dosyayı sürükleyip bırakın.
   - Desteklenen formatlar: **PDF**, **Word (.docx)**, **Excel (.xlsx)**
   - Maksimum boyut: **10 MB**
5. **"Planı Yükle"** butonuna tıklayın.
6. Sistem dosyayı okur, tablo yapısını ayrıştırır ve veritabanına kaydeder.

> **İpucu:** Excel formatı en iyi sonucu verir. Tablonuzda şu sütunlar varsa otomatik tanınır: Hafta, Ünite/Konu, Kazanım, Öğretim Teknikleri, Araç-Gereç, Ölçme Değerlendirme.

---

### 2️⃣ Haftalık Ders Programı Oluşturma

1. Menüden **"Ders Programı"** seçin veya **[http://localhost:5000/schedule](http://localhost:5000/schedule)** adresine gidin.
2. **"Gün"** alanından bir gün seçin (Pazartesi–Cuma).
3. **"Saat Aralığı"** alanına ders saatini yazın (örn: `08:00–09:00`).
4. **"Ders Adı"** alanına dersin adını yazın (örn: `Dizist Taksi Sistemleri`).
5. **"Ekle"** butonuna tıklayın.
6. Tablo güncellenerek yeni girdinizi gösterir.

Tablo görünümünde:
- **Sarı ile vurgulanan** satırlar → **Bugünün** dersleri
- **Mavi ile vurgulanan** satırlar → **Yarının** dersleri

Bir girişi silmek için ilgili satırdaki **🗑️ çöp kutusu** ikonuna tıklayın.

---

### 3️⃣ Materyal Üretme

1. Menüden **"Materyal Üret"** seçin veya **[http://localhost:5000/generate](http://localhost:5000/generate)** adresine gidin.
2. **"Ders Adı"** alanına dersin adını yazın (örn: `Araç Teknolojisi Atölyesi-9`).
3. **"Konu"** alanına bu hafta işlenecek konuyu yazın (örn: `Piston Biyel Mekanizması Kontrolü`).
4. **"Kazanımlar"** alanına öğrencilerin öğreneceği hedefleri yazın (örn: `Piston-biyel kontrolünü ve değişimini yapar`).
5. Üretmek istediğiniz materyal türlerini işaretleyin:
   - ☑️ **Bilgi Kartları** – 5-10 adet soru-cevap kartı
   - ☑️ **Sunum** – 10-15 slaytlık sunum içeriği
   - ☑️ **Test** – 20-30 çoktan seçmeli + 5 açık uçlu soru
   - ☑️ **Öğretmen Notları** – Detaylı ders anlatım metni
6. **"Materyal Üret"** butonuna tıklayın.
7. Birkaç saniye bekleyin (yapay zeka içerik üretirken yükleme çubuğu görünür).
8. Üretilen materyaller ekranda görüntülenir.

---

### 4️⃣ Materyalleri İndirme ve Önizleme

Materyal üretildikten sonra her materyal kartının altında şu düğmeler görünür:

| Düğme | Açıklama |
|-------|----------|
| 👁️ **Önizle** | Materyali tarayıcıda tam görünümde açar |
| 📄 **PDF İndir** | Yazdırılabilir PDF olarak indirir |
| 📝 **Word İndir** | Düzenlenebilir `.docx` olarak indirir (test ve notlar için) |
| 🌐 **HTML İndir** | Tek dosya web sayfası olarak indirir |
| 📋 **TXT İndir** | Düz metin olarak indirir |

Daha önce üretilmiş materyallere erişmek için **[http://localhost:5000/api/materials](http://localhost:5000/api/materials)** adresine gidin veya bir materyalin ID numarasını kullanarak **[http://localhost:5000/preview/ID](http://localhost:5000/preview/1)** adresine gidin.

---

## 📁 Desteklenen Dosya Formatları

### Yükleme (Yıllık Plan)

| Format | Uzantı | Notlar |
|--------|--------|--------|
| Excel | `.xlsx` | En iyi sonuç; tablo başlıkları otomatik tanınır |
| Word | `.docx` | Tablo içeren belgeler desteklenir |
| PDF | `.pdf` | Tablo içeren PDF'ler desteklenir; karmaşık düzenler değişken sonuç verebilir |

### İndirme (Üretilen Materyaller)

| Format | Kullanım |
|--------|----------|
| `.pdf` | Tüm materyal türleri; yazdırma için ideal |
| `.docx` | Test ve öğretmen notları; Word'de düzenlenebilir |
| `.html` | Bilgi kartları ve sunumlar; tarayıcıda açılabilir |
| `.txt` | Tüm materyal türleri; düz metin |

---

## 🛠️ Sık Karşılaşılan Sorunlar

**`python: command not found` hatası:**
- Windows'ta `python` yerine `py` komutunu deneyin.
- Python'un PATH'e eklendiğinden emin olun veya yeniden kurun.

**`pip install` sırasında hata:**
- Sanal ortamın aktif olduğunu kontrol edin (`(venv)` görmüyor musunuz?).
- `pip install --upgrade pip` çalıştırıp tekrar deneyin.

**Uygulama başlamıyor / port hatası:**
- Başka bir uygulama 5000 portunu kullanıyor olabilir. Şu komutla farklı portta başlatın:
  ```bash
  flask run --port 5001
  ```
  Ardından `http://localhost:5001` adresini açın.

**Dosya yükleme çalışmıyor:**
- Dosya boyutunun 10 MB'den küçük olduğunu kontrol edin.
- Dosya uzantısının `.pdf`, `.docx` veya `.xlsx` olduğunu kontrol edin.

**Materyal üretimi çok hızlı bitiyor / içerik kısa:**
- API anahtarı girilmemiş olabilir; bu durumda sistem şablon içerik üretir.
- `.env` dosyasında `OPENAI_API_KEY` veya `GEMINI_API_KEY` satırının doğru doldurulduğunu kontrol edin.
- Materyal üretim sayfasındaki **"Aktif yapay zeka"** etiketine bakın; "şablon" gösteriyorsa anahtar okunamıyor demektir.
- Uygulamayı durdurup (`Ctrl+C`) yeniden başlatın.

**Veritabanı sıfırlamak istiyorum:**
- `materials.db` dosyasını silin. Uygulama bir sonraki başlangıçta boş veritabanı oluşturur.

---

## 📂 Proje Dosya Yapısı

```
ogretmen-ders-materyali-uretici/
├── app.py                 # Ana uygulama – tüm sayfa ve API rotaları
├── config.py              # Yapılandırma (.env'den okur)
├── requirements.txt       # Python bağımlılıkları
├── .env.example           # Çevre değişkenleri şablonu (.env'i bu dosyadan oluşturun)
├── database/
│   ├── db_manager.py      # Veritabanı işlemleri (kaydet, oku, sil)
│   └── models.py          # Tablo şemaları
├── parsers/
│   ├── pdf_parser.py      # PDF'den tablo okuma
│   ├── word_parser.py     # Word'den tablo okuma
│   └── excel_parser.py    # Excel'den tablo okuma
├── generators/
│   ├── flashcard_generator.py    # Bilgi kartı üretimi
│   ├── presentation_generator.py # Sunum üretimi
│   ├── test_generator.py         # Test sorusu üretimi
│   └── notes_generator.py        # Öğretmen notu üretimi
├── exporters/
│   ├── pdf_exporter.py    # PDF oluşturma (reportlab)
│   └── word_exporter.py   # Word belgesi oluşturma
├── static/
│   ├── css/style.css      # Özel stil dosyası
│   ├── js/main.js         # Ön yüz JavaScript
│   └── uploads/           # Yüklenen dosyalar (otomatik oluşturulur)
├── templates/             # HTML şablonlar (Jinja2)
│   ├── base.html          # Temel sayfa düzeni (navbar, footer)
│   ├── index.html         # Ana sayfa
│   ├── upload_plan.html   # Plan yükleme sayfası
│   ├── schedule.html      # Ders programı sayfası
│   ├── generate.html      # Materyal üretim sayfası
│   └── preview.html       # Materyal önizleme sayfası
└── tests/
    └── test_parsers.py    # Birim testler
```

---

## 📝 Lisans

Bu proje eğitim amaçlı hazırlanmıştır.
