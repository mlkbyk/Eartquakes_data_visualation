# SEISMOSCOPE — Gerçek Model Eğitim Sonuçları

**Veri:** USGS, dünya genelinde M4.5+; 1 Şubat 2023–31 Mayıs 2024. 6 Şubat Kahramanmaraş depremleri dahildir. **9,889 satır × 34 sütun.**

## Eğitim protokolü
- **K-Means:** Gözetimsiz olduğu için bütün 9,889 olayın tamamı üzerinde eğitildi. K=3…7 için silhouette; her K için aynı 1.500 örnek üzerinde skor hesaplandı.
- **Decision Tree (classification/regression):** İlk **7,911** olay eğitim, sonraki **1,978** olay kronolojik test olarak ayrıldı. Test başlangıcı: **2024-02-16 20:47:29.448000+00:00**. Hiperparametreler yalnızca eğitim döneminde `TimeSeriesSplit(4)` ile seçildi.
- **Önemli:** Bu modeller geçmişte kaydedilmiş olayların özelliklerini inceler. Gelecekteki depremlerin zamanı, konumu, büyüklüğü veya hasarını tahmin etmez.

## Model 1 — K-Means Clustering
- Seçilen küme sayısı: **7**
- Örneklem silhouette skoru: **0.287** (küme ayrımı belirgin değil; keşifsel yorumlanmalı).
- Özellikler: jeodezik birim küre koordinatları (`geo_x/y/z`), `mag`, `log1p(depth)`; tüm özellikler `StandardScaler` ile ölçeklendi.
- Küme boyutları: 0: 645, 1: 751, 2: 1,315, 3: 1,587, 4: 1,236, 5: 3,235, 6: 1,120.
- Küme etiketleri **tektonik fay/risk bölgesi** anlamına gelmez.

## Model 2 — Decision Tree Classification (önerilen ikinci ML modeli)
- Hedef: **depth_category** (sığ/orta/derin); girişler: dünya üzerindeki birim küre konumu ve ölçülmüş büyüklük. **Depth, depth_category ve depth_exactly_10km giriş olarak kullanılmadı.**
- Seçilen hiperparametreler: `max_depth=10`, `min_samples_leaf=20`, `class_weight='balanced'`.
- Kronolojik test **balanced accuracy: 78.7%** (sadece çoğunluk sınıfı seçen model: 33.3%).
- Kronolojik test **macro F1: 0.625**, **overall accuracy: 69.8%**.
- **Dürüst karşılaştırma:** Baseline'ın sıradan doğruluğu 77.6% ve bu ağaçtan daha yüksektir. Ağaç azınlıktaki derinlik kategorilerini tanımaya çalıştığı için sınıflar arası dengeli doğrulukta daha iyidir. Yalnızca accuracy'yi öne çıkarmayın.
- Coğrafi dağılıma ve veri seti seçimine bağlıdır; farklı dönem/ölçüm sistemlerinde performans değişebilir.

## Deneysel model — Decision Tree Regression (dashboard için **önerilmiyor**)
- Hedef: deprem büyüklüğü. Girişler: konum ve derinlik bilgisi (hedef değerin kendisi veya türevleri girdi değil).
- Kronolojik test **MAE: 0.2643**, sabit ortalama baseline **MAE: 0.2605**.
- **R²: -0.0251**. Daha zayıf bir model: kullanıma sunmuyoruz; deney ve neden elendiği şeffafça belgelenmiştir.

## Sınırlılıklar ve etik kullanım
1. USGS M4.5+ derlemi bütün depremleri kapsamaz; M4.5 altı olaylar dışarıda.
2. Çok sayıda 10 km derinlik kaydı sabitlenmiş/varsayılan olabilir; özellikle derinlik sınıflandırmasında dikkat edilmelidir.
3. Küresel tektonik bölgeler sınıfların dengesini ve kümelenmeyi etkiler; modeller 'deprem tahmini' olarak adlandırılmamalıdır.
4. 6 Şubat olayı eğitim dönemindedir; bu olaylarla ilgili sınıflandırma değerlendirmesi yapılmış gibi sunulmaz.
5. Eğitimle elde edilen `.joblib` dosyaları yalnızca güvenilir ve bilinen kaynaktan yüklenmelidir (pickle güvenliği).

## Üretilen dosyalar
- `ml/models/kmeans_pipeline.joblib`
- `ml/models/decision_tree_classifier.joblib`
- `ml/models/decision_tree_regressor_experimental.joblib`
- `ml/reports/metrics.json` — ölçümler ve confusion matrix
- `ml/reports/cluster_profiles.csv` — kümelerin karşılaştırması
- `ml/reports/ml_scored_events.csv` — her olay için küme, test olayları için tahminler
- `ml/ml_dashboard.py` — Streamlit ML bölümü

**Not:** K-Means ve Decision Tree iki temel algoritma ailesidir; sınıflandırma ana demo, regresyon sadece olumsuz deneydir. Bu bölümü hocanın istediği 9 özgün görselleştirmenin yerine saymayın.
