# Teknik Dokümantasyon — LinkVault

Bu belge LinkVault'un veri modelini, mimari kararlarını ve geliştirme
sürecinde karşılaşılan sorunların çözümlerini açıklar.

---

## 1. Mimari Genel Bakış

LinkVault, Django'nun MVT (Model–View–Template) mimarisini izler:

- **Model katmanı** veri yapısını ve ilişkileri tanımlar.
- **View katmanı** istekleri işler; çoğunlukla Django'nun sınıf tabanlı
  generic view'leri kullanılır.
- **Template katmanı** Bootstrap 5 ile duyarlı arayüzü oluşturur.
- Ayrıca Django REST Framework ile ayrı bir **API katmanı** sunulur.

İstek akışı: `urls.py` → ilgili `View` → `Model` sorgusu → `Template`
render veya JSON yanıt.

---

## 2. Veri Modeli

Üç ana model vardır: `Tag`, `Collection` ve `Bookmark`.

### 2.1 Tag

Etiketleri temsil eder. `name` alanı benzersizdir, böylece aynı etiket
tekrar oluşturulmaz. Bookmark ile çoka-çok ilişkilidir.

### 2.2 Collection

Kullanıcının bağlantılarını gruplamak için kullanılan klasör yapısıdır.

- `owner` — `User` modeline `ForeignKey` (CASCADE). Kullanıcı silinirse
  koleksiyonları da silinir.
- `unique_together = ['owner', 'name']` — Bir kullanıcı aynı isimde iki
  koleksiyon oluşturamaz; veri bütünlüğü veritabanı düzeyinde korunur.

### 2.3 Bookmark

Kaydedilen tek bir bağlantıyı temsil eder.

- `owner` — `User` modeline `ForeignKey` (CASCADE).
- `collection` — `Collection` modeline `ForeignKey` (SET_NULL).
  Koleksiyon silindiğinde bağlantı silinmez, yalnızca koleksiyonsuz
  kalır. Bu, kullanıcı verisinin yanlışlıkla kaybolmasını önler.
- `tags` — `Tag` modeline `ManyToManyField`.
- `is_favorite`, `is_public` — Boolean durum alanları.

### 2.4 İlişki Özeti

```
User 1───* Collection 1───* Bookmark *───* Tag
User 1──────────────────────* Bookmark
```

`related_name` tanımları (`user.bookmarks`, `collection.bookmarks` vb.)
ilişkili nesnelere okunabilir şekilde erişmeyi sağlar.

---

## 3. View Tasarımı

CRUD işlemleri için Django'nun sınıf tabanlı generic view'leri
(`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`)
kullanılmıştır. Bu, tekrar eden kodu azaltır ve Django kurallarına uygun
bir yapı sağlar.

### Erişim Kontrolü

- `LoginRequiredMixin` — Tüm view'ler oturum açmış kullanıcı gerektirir.
- `UserPassesTestMixin` ile `test_func` — Kullanıcının yalnızca kendi
  nesnelerine erişmesini sağlar. Başkasının nesnesine erişim denemesi
  HTTP 403 döndürür.

### Sorgu Verimliliği

`BookmarkListView` içinde `select_related('collection')` ve
`prefetch_related('tags')` kullanılarak N+1 sorgu problemi önlenmiştir.
İlişkili koleksiyon ve etiket verileri tek seferde çekilir.

---

## 4. Form Tasarımı

`BookmarkForm`, modelin standart alanlarına ek olarak `tags_input` adlı
özel bir `CharField` içerir. Kullanıcı etiketleri virgülle ayrılmış
metin olarak girer; `clean_tags_input` metodu bunu temizler ve `save`
sırasında `get_or_create` ile `Tag` nesnelerine dönüştürür. Böylece
kullanıcı arayüzü basit kalırken model ilişkisi doğru kurulur.

Form `__init__` metodunda, koleksiyon seçim listesi yalnızca o
kullanıcıya ait koleksiyonlarla sınırlandırılır.

---

## 5. REST API

Django REST Framework'ün `ModelViewSet` yapısı kullanılır. Her viewset
`get_queryset` ile sorguyu istek sahibinin verisiyle sınırlar ve
`perform_create` ile yeni kayıtların sahibini otomatik atar.

`IsOwner` adlı özel izin sınıfı, nesne düzeyinde yetkilendirme sağlar.
API, oturum tabanlı kimlik doğrulama ve sayfa numarası tabanlı sayfalama
kullanır.

---

## 6. Frontend Kararları

- **Bootstrap 5** CDN üzerinden eklenmiştir; ayrı bir derleme adımı
  gerektirmez ve duyarlı yerleşimi hazır sağlar.
- Şablonlar `base.html` üzerinden kalıtım alır; ortak gezinme çubuğu ve
  mesaj alanı tek yerde tanımlıdır.
- Favori işaretleme, Fetch API ile AJAX üzerinden yapılır. Sunucu JSON
  yanıt döndürür ve yalnızca ilgili simge güncellenir.

---

## 7. Karşılaşılan Sorunlar ve Çözümleri

**Aramada tekrarlanan sonuçlar.** Etiket üzerinden yapılan arama,
çoka-çok birleşimi nedeniyle aynı bağlantıyı birden çok kez döndürüyordu.
Sorgu sonucuna `.distinct()` eklenerek çözüldü.

**Koleksiyon listesinde başka kullanıcıların koleksiyonları.** Bookmark
formundaki koleksiyon alanı başlangıçta tüm koleksiyonları listeliyordu.
Form `__init__` metodunda queryset, oturum sahibinin koleksiyonlarıyla
sınırlandırıldı.

**Koleksiyon silinince bağlantıların da silinmesi.** İlk tasarımda
`Bookmark.collection` alanı CASCADE idi; bir koleksiyon silindiğinde
içindeki tüm bağlantılar kayboluyordu. Alan `SET_NULL` olarak
değiştirildi ve `null=True` eklendi.

**API'de sayfalanmış yanıtın test edilmesi.** API testleri başta yanıtı
düz liste olarak bekliyordu; sayfalama açık olduğu için sonuçlar
`results` anahtarı altında geliyordu. Test, her iki durumu da
karşılayacak şekilde güncellendi.

---

## 8. Olası Geliştirmeler

- Bağlantı eklenirken sayfa başlığının otomatik çekilmesi.
- Ölü (erişilemeyen) bağlantıların tespiti.
- Etiket bulutu ve istatistik görünümü.
- Koleksiyonların başka kullanıcılarla paylaşılması.
