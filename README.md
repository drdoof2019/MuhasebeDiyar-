# MuhasebeDiyarı - Dükkan Muhasebe Uygulaması

Küçük işletmeler (dükkan, atölye) için geliştirilmiş, Türkçe arayüzlü, web tabanlı muhasebe takip uygulaması.

## Özellikler

- Gelir / Gider / Altın Bozumu / Kasa Notu işlem tipleri
- Çoklu ödeyen desteği (tek işlemde birden fazla kişi)
- Taksitli kredi kartı takibi
- Kategorize raporlama (aylık, yıllık, finansör, kategori, altın, kasa)
- Otomatik yedekleme ve yedekten geri yükleme
- Çok kullanıcılı, yetki kontrollü

## Gereksinimler

- **Python 3.10+** (PATH'te olmalı)
- Windows (batch script ile), Linux/Mac (manuel venv ile)

## Kurulum ve Başlatma

### Windows (Tek Tıkla)

`start.bat` dosyasına çift tıklayın. Betik otomatik olarak:

1. Sanal ortam (`venv/`) yoksa oluşturur, varsa aktif eder
2. Gerekli Python paketlerini venv içine kurar
3. Uygulamayı `http://127.0.0.1:5050` adresinde başlatır
4. Varsayılan admin kullanıcısını oluşturur
5. Tarayıcıy açar

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Tarayıcıdan `http://127.0.0.1:5050` adresine gidin.

## İlk Giriş

| Alan          | Değer       |
|---------------|-------------|
| Kullanıcı Adı | `admin`     |
| Şifre         | `admin123`  |

> ⚠️ **ÖNEMLİ:** İlk girişten sonra Admin şifresini değiştirin veya yeni kullanıcı oluşturup admin'i pasif yapın. Şifreyi değiştirmek için:
> 1. **Kullanıcılar** menüsüne gidin (sadece admin görebilir)
> 2. Admin kullanıcısının yanındaki düzenleme butonuna tıklayın
> 3. Yeni şifrenizi girin ve kaydedin

## Port / Adres Değiştirme

Varsayılan port `5050`'dir. Değiştirmek için [`run.py`](run.py:9) dosyasındaki `port=5050` değerini değiştirin:

```python
app.run(host='0.0.0.0', port=5050, debug=True)
```

## Yedekleme

- Uygulama 7 günde bir yedekleme hatırlatması gösterir
- **Yedekleme** menüsünden manuel yedek alabilir, yedekleri indirebilir ve geri yükleyebilirsiniz
- Yedekler `instance/backups/` klasöründe tutulur

## Güvenlik Notları

- `.env` dosyası oluşturarak `SECRET_KEY` ve `ADMIN_PASSWORD` değerlerini override edebilirsiniz:
  ```
  SECRET_KEY=sizin-ozel-anahtariniz
  ADMIN_PASSWORD=sizin-admin-sifreniz
  ```
- Veritabanı (`instance/muhasebe.db`) hassas veri içerir, paylaşmayın
- Uygulama sadece `127.0.0.1` (localhost) üzerinden erişilebilir şekilde tasarlanmıştır. Dış ağa açmayın.


## Örnek Veri (varsa)

- python seed_sample_data.py


## Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| Python bulunamadı hatası | Python 3.10+ kurun ve PATH'e ekleyin |
| Paketler yüklenemedi | `venv\Scripts\activate` çalıştırıp `pip install -r requirements.txt` manuel deneyin |
| Port 5050 dolu | `run.py` içinde portu değiştirin veya portu kullanan uygulamayı kapatın |
| Veritabanı hatası | `instance/muhasebe.db` dosyasını silip uygulamayı yeniden başlatın (yedekleriniz varsa geri yükleyin) |
| 404 / Sayfa bulunamadı | Tarayıcıdan `http://127.0.0.1:5050/seed-admin` adresini ziyaret edin |

## Lisans

MIT


