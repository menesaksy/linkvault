# LinkVault — Bookmark Yöneticisi

LinkVault, kullanıcıların internette beğendikleri bağlantıları kaydedip
etiketleyebildiği, koleksiyonlara ayırabildiği ve hızlıca arayabildiği
çok kullanıcılı bir web uygulamasıdır. Django ile geliştirilmiştir.

> Yeditepe Üniversitesi — Django Dönem Projesi

---

## İçindekiler

- [Özellikler](#özellikler)
- [Teknoloji Yığını](#teknoloji-yığını)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [REST API](#rest-api)
- [Testler](#testler)
- [Proje Yapısı](#proje-yapısı)

---

## Özellikler

- **Kullanıcı Hesapları** — Kayıt olma, giriş ve çıkış (Django auth).
- **Yetkilendirme** — Her kullanıcı yalnızca kendi bağlantı ve
  koleksiyonlarını görüntüleyip düzenleyebilir.
- **Bookmark CRUD** — Bağlantı ekleme, listeleme, düzenleme ve silme.
- **Koleksiyonlar** — Bağlantıları klasör mantığıyla gruplama.
- **Etiketleme** — Virgülle ayrılmış metin girişiyle çoklu etiket;
  etiketler arka planda otomatik oluşturulur.
- **Arama ve Filtreleme** — Başlık, açıklama, URL ve etiket üzerinden
  arama; koleksiyona ve favori durumuna göre filtreleme.
- **Sayfalama** — Bağlantı listesi sayfa sayfa gösterilir.
- **AJAX** — Favori işaretleme, sayfa yeniden yüklenmeden yapılır.
- **REST API** — Django REST Framework ile bookmark ve koleksiyon
  uç noktaları.
- **Duyarlı Arayüz** — Bootstrap 5 ile mobil, tablet ve masaüstü uyumu.

---

## Teknoloji Yığını

| Katman      | Teknoloji                          |
|-------------|------------------------------------|
| Backend     | Python 3, Django                   |
| API         | Django REST Framework              |
| Veritabanı  | SQLite (geliştirme)                |
| Frontend    | HTML, Bootstrap 5, Bootstrap Icons |
| Dinamik UI  | Vanilla JavaScript (Fetch API)     |
| Dağıtım     | Gunicorn, WhiteNoise               |

---

## Kurulum

### Gereksinimler

- Python 3.10 veya üzeri
- pip ve venv

### Adımlar

```bash
# 1. Depoyu klonla
git clone https://github.com/menesaksy/linkvault.git
cd linkvault

# 2. Sanal ortam oluştur ve etkinleştir
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Veritabanını hazırla
python manage.py migrate

# 5. Yönetici hesabı oluştur
python manage.py createsuperuser

# 6. Sunucuyu başlat
python manage.py runserver
```

Uygulama `http://127.0.0.1:8000` adresinde çalışır.
Yönetim paneli `http://127.0.0.1:8000/admin` adresindedir.

---

## Kullanım

1. `/signup` üzerinden bir hesap oluştur veya `/login` ile giriş yap.
2. **Yeni Bookmark** butonuyla bir bağlantı ekle; istersen koleksiyon
   seç ve virgülle ayrılmış etiketler gir.
3. Ana sayfadaki arama kutusu ve açılır menülerle bağlantılarını
   filtrele.
4. Bağlantı kartındaki yıldıza tıklayarak favorilere ekle.
5. **Koleksiyonlar** sayfasından klasörlerini yönet.

---

## REST API

Tüm uç noktalar oturum açmış kullanıcı gerektirir.

| Yöntem | Uç Nokta                  | Açıklama                       |
|--------|---------------------------|--------------------------------|
| GET    | `/api/bookmarks/`         | Kullanıcının bağlantıları      |
| POST   | `/api/bookmarks/`         | Yeni bağlantı oluşturur        |
| GET    | `/api/bookmarks/{id}/`    | Tek bir bağlantı               |
| PUT    | `/api/bookmarks/{id}/`    | Bağlantıyı günceller           |
| DELETE | `/api/bookmarks/{id}/`    | Bağlantıyı siler               |
| GET    | `/api/collections/`       | Kullanıcının koleksiyonları    |
| POST   | `/api/collections/`       | Yeni koleksiyon oluşturur      |

Tarayıcıdan test etmek için `/api-auth/login/` üzerinden giriş yapıp
`/api/bookmarks/` adresini ziyaret edebilirsiniz.

---

## Testler

```bash
python manage.py test
```

Test paketi model davranışlarını, yetkilendirme kurallarını, CRUD
işlemlerini, arama filtresini, AJAX uç noktasını ve REST API'yi kapsar.

---

## Proje Yapısı

```
linkvault/
├── config/              # Proje ayarları ve kök URL yapılandırması
│   ├── settings.py
│   └── urls.py
├── bookmarks/           # Ana uygulama
│   ├── models.py        # Bookmark, Collection, Tag modelleri
│   ├── views.py         # CRUD view'leri ve AJAX uç noktası
│   ├── forms.py         # Bookmark ve Collection formları
│   ├── serializers.py   # REST API serializer'ları
│   ├── api.py           # REST API viewset'leri
│   ├── urls.py          # Uygulama URL'leri
│   ├── admin.py         # Yönetim paneli yapılandırması
│   ├── tests.py         # Test paketi
│   └── templates/       # HTML şablonları
├── static/css/          # Özel stiller
├── requirements.txt
└── manage.py
```
