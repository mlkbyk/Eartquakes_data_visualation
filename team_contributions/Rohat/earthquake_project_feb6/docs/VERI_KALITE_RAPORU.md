# CEN445 — USGS Deprem Verisi Kalite ve Ön İşleme Raporu (6 Şubat güncellemesi)

## 1. Kapsam ve karar
- **Kaynak:** USGS resmi deprem kataloğundan kullanıcı tarafından indirilen `query.csv`.
- **Orijinal:** 13,472 satır × 22 sütun. 8 kayıt deprem türünde değildir.
- **Yeni ana dosya:** **9,889 satır × 34 sütun**; ödevin 2.000–10.000 satır ve en az 7 sütun şartını karşılar.
- **Yeni tarih penceresi:** 1 Şubat 2023 00:00 UTC (dahil) – 1 Haziran 2024 00:00 UTC (hariç): **16 tam ay**.
- **Neden değişti?** Önceki Temmuz 2023–Kasım 2024 döneminde 6 Şubat 2023 Kahramanmaraş depremleri yoktu. Bu güncelleme, iki ana olayı da içerecek şekilde dönemi değiştirir.

## 2. Verinin nasıl hazırlandığı
1. `type == "earthquake"` koşuluyla **8** deprem olmayan kayıt dışarı alındı.
2. Tarih dışında kalan **3,575** deprem (UTC) kapsam dışına çıktı.
3. Kalan **9,889** depremin tamamı korundu; rastgele örnekleme yapılmadı.
4. Orijinal 22 alanın değerleri değiştirilmedi. Var olan 12 yardımcı alan yeniden üretildi.
5. Eksik opsiyonel veri sıfır ya da tahminle doldurulmadı. Grafik bazlı kullanılabilir kayıt sayısı ayrıca belirtilmeli.

## 3. Kontrol sonuçları
| Kontrol | Sonuç |
|---|---:|
| Satır sayısı | 9,889 |
| Sütun sayısı | 34 |
| Benzersiz `id` | 9,889 |
| Tekrarlı ID | 0 |
| Boş `time`, `latitude`, `longitude`, `depth`, `mag` | 0 |
| Deprem inceleme statüsü | {'reviewed': 9889} |
| Tam 10 km derinlik kayıtları | 4,380 (%44.29) |

### Opsiyonel alanlardaki eksikler
| Sütun | Eksik | Oran |
|---|---:|---:|
| `magError` | 96 | %0.97 |
| `magNst` | 78 | %0.79 |
| `dmin` | 40 | %0.40 |
| `horizontalError` | 39 | %0.39 |
| `nst` | 37 | %0.37 |
| `gap` | 37 | %0.37 |

### Yıl bazlı kayıt sayıları (eşit süreler değildir)
| Yıl | Kayıt |
|---|---:|
| 2023 | 6998 |
| 2024 | 2891 |

### Büyüklük grupları
| Grup | Kayıt |
|---|---:|
| M4.5–4.9 | 7577 |
| M5.0–5.9 | 2132 |
| M6.0–6.9 | 161 |
| M7.0+ | 19 |

### Aylık kayıt sayısı
| UTC ay | Kayıt |
|---|---:|
| 2023-02 | 656 |
| 2023-03 | 554 |
| 2023-04 | 538 |
| 2023-05 | 663 |
| 2023-06 | 614 |
| 2023-07 | 484 |
| 2023-08 | 492 |
| 2023-09 | 509 |
| 2023-10 | 677 |
| 2023-11 | 694 |
| 2023-12 | 1117 |
| 2024-01 | 623 |
| 2024-02 | 508 |
| 2024-03 | 509 |
| 2024-04 | 705 |
| 2024-05 | 546 |

## 4. 6 Şubat 2023 Kahramanmaraş olayları doğrulaması
- **M7.8 Pazarcık:** `us6000jllz`, `2023-02-06T01:17:34.342Z` (**04:17:34 Türkiye saati**), enlem 37.2256, boylam 37.0143.
- **M7.5 Elbistan:** `us6000jlqa`, `2023-02-06T10:24:48.811Z` (**13:24:48 Türkiye saati**), enlem 38.0106, boylam 37.1962.
- 6 Şubat 2023 UTC gününde `place` alanında Turkey/Syria ifadesi içeren **111** M4.5+ olay var. Bu sayı, **Kahramanmaraş artçılarının doğrulanmış sayısı değildir**; yalnızca basit bir metin eşleştirmesidir.
- Aynı UTC gününde yaklaşık 35.5–39.5°K ve 35–40.5°D koordinat penceresinde **111** M4.5+ olay bulunuyor. Bu da bilimsel dizi tanımlaması değil, örnek bölgesel filtredir.
- USGS referansları: https://earthquake.usgs.gov/earthquakes/eventpage/us6000jllz ve https://earthquake.usgs.gov/earthquakes/eventpage/us6000jlqa

## 5. Önemli bilimsel sınırlamalar
- M4.5 altındaki depremler dataset içinde **yoktur**; küçük artçıların büyük bölümü kapsanmamıştır.
- Türkiye saati UTC+3'tür. Grafiklerde tarih/saat dilimi açıkça belirtin; 6 Şubat için yerel tarih/UTC gün sınırı farklı olabilir.
- 2023 için Şubat–Aralık (**11 ay**) ve 2024 için Ocak–Mayıs (**5 ay**) kapsanıyor. Tam yıllık toplamları eşit kapsam gibi kıyaslamayın.
- `place` serbest metindir; tek başına güvenilir ülke sütunu değildir.
- USGS, kimi olaylarda tam 10 km derinliğin belirli bir yöntemle atanabildiğini belirtir: https://www.usgs.gov/faqs/why-do-so-many-earthquakes-occur-a-depth-10km
- Veriden can kaybı, bina hasarı, risk veya gelecekte deprem tahmini doğrudan çıkarılamaz.

**Önerilen görsel:** 6 Şubat iki ana olayı ayrı işaretlenmiş harita + 6 Şubat öncesi/sonrası M4.5+ bölgesel zaman serisi. Dizi üyeliğini kanıtlayan veri olmadığından her bölgesel depremi otomatik artçı olarak etiketlemeyin.
