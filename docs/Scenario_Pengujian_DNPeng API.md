# Skenario Pengujian API — Autentikasi & Modul PKRT (`DNPeng API`)

Dokumen ini berisi rincian skenario pengujian lengkap untuk setiap *endpoint* yang terlibat dalam alur kerja modul **PKRT**, dimulai dari proses login (`POST Login User`) hingga pengambilan data agregasi (`GET Aggregated Data`). Setiap *endpoint* dilengkapi dengan pengujian **Positive Case** (kondisi normal), **Edge Case** (kondisi batas/data kosong), dan **Negative Case** (autentikasi, validasi parameter/payload, serta pencegahan *error* `500`).

## Ringkasan Alur Pengujian

| No | Nama Request | Method | Endpoint | Autentikasi |
| ----- | ----- | ----- | ----- | ----- |
| 1 | Login User | `POST` | `/api/v1/auth/login` | No Auth |
| 2 | Add Data | `POST` | `/api/v1/pkrt/data` | Bearer Token |
| 3 | Get Data | `GET` | `/api/v1/pkrt/data` | Bearer Token |
| 4 | Get Data by Kode | `GET` | `/api/v1/pkrt/kode` | Bearer Token |
| 5 | Get Data by Periode | `GET` | `/api/v1/pkrt/periode` | Bearer Token |
| 6 | Get Timeseries Data by Kode | `GET` | `/api/v1/pkrt/timeseries` | Bearer Token |
| 7 | Get Indikator | `GET` | `/api/v1/pkrt/indikator` | Bearer Token |
| 8 | Get Latest Data | `GET` | `/api/v1/pkrt/latest` | Bearer Token |
| 9 | Get Growth Data by Kode and Type | `GET` | `/api/v1/pkrt/growth` | Bearer Token |
| 10 | Get Quarter Data by Kode | `GET` | `/api/v1/pkrt/quarter` | Bearer Token |
| 11 | Get Annual Data by Kode | `GET` | `/api/v1/pkrt/annual` | Bearer Token |
| 12 | Get Chart Data by Kode | `GET` | `/api/v1/pkrt/chart` | Bearer Token |
| 13 | Get Growth Chart Data by Kode and Type | `GET` | `/api/v1/pkrt/growth/chart` | Bearer Token |
| 14 | Get Quarter Chart Data by Kode | `GET` | `/api/v1/pkrt/quarter/chart` | Bearer Token |
| 15 | Get Annual Chart Data by Kode | `GET` | `/api/v1/pkrt/annual/chart` | Bearer Token |
| 16 | Get Aggregated Data | `GET` | `/api/v1/pkrt/aggregated` | Bearer Token |

---

## Rincian Skenario Pengujian per Endpoint

### 1. Auth — `POST Login User`

* **Endpoint:** `{{base_url}}/api/v1/auth/login`
* **Body (`x-www-form-urlencoded`):** `username` (`admin@admin.com`), `password` (`admin123`)
* **Skenario Pengujian:**
  1. **\[Positive\] Login dengan kredensial valid:**
     * **Ekspektasi:** Status kode `200 OK`, `Content-Type` berupa `application/json`, dan waktu respons di bawah `1000 ms`.
     * **Validasi Struktur:** *Response body* wajib memiliki *key* `access_token`, `refresh_token`, `token_type` (`bearer`), dan objek `user` (`id`, `name`, `email`, `role`).
     * **Aksi Lanjutan:** Menyimpan nilai `access_token` dan `refresh_token` ke dalam *environment variable* Postman untuk digunakan oleh seluruh *request* PKRT berikutnya.
  2. **\[Edge Case\] Input username mengandung spasi di awal/akhir atau huruf kapital berbeda (case-sensitivity):**
     * **Ekspektasi:** Sistem menangani normalisasi email secara konsisten atau menolak secara bersih (`401 Unauthorized` / `422 Unprocessable Entity`) tanpa memicu `500 Internal Server Error`.
  3. **\[Negative\] Login dengan password salah, user tidak terdaftar, atau field wajib kosong:**
     * **Ekspektasi:** Mengembalikan status `401 Unauthorized` (kredensial salah) atau `422 Unprocessable Entity` (*field* hilang) dalam format JSON yang valid tanpa memperbarui token di *environment*.

---

### 2. PKRT — `POST Add Data`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/data`
* **Header:** `Authorization: Bearer {{access_token}}`
* **Skenario Pengujian:**
  1. **\[Positive\] Tambah data PKRT dengan payload dan token valid:**
     * **Ekspektasi:** Status kode `200 OK` (atau `201 Created`) dengan *response body* berupa JSON valid.
  2. **\[Edge Case\] Pengiriman data duplikat (kombinasi `kode_wilayah`, `kode`, dan `periode` sudah ada) atau nilai `0` / negatif:**
     * **Ekspektasi:** Sistem menangani sesuai aturan bisnis (*upsert*/*update* atau menolak dengan status `400`/`409` dengan pesan JSON jelas) tanpa *crash* pada database.
  3. **\[Negative\] Akses tanpa token, token kedaluwarsa, atau role tidak memiliki izin tulis:**
     * **Ekspektasi:** Mengembalikan status `401 Unauthorized` atau `403 Forbidden` dengan pesan *error* JSON yang jelas.
  4. **\[Negative\] Body request kosong, format JSON rusak, atau tipe data field salah (misalnya `nilai` berisi string):**
     * **Ekspektasi:** Mengembalikan status `400 Bad Request` atau `422 Unprocessable Entity` dengan detail kesalahan validasi pada *field* terkait.

---

### 3. PKRT — `GET Get Data`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/data?kode_wilayah=00`
* **Parameter Query:** `kode_wilayah` (contoh: `00`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data PKRT berdasarkan `kode_wilayah` yang valid:**
     * **Ekspektasi:** Status kode `200 OK` dan *response body* berupa JSON valid.
  2. **\[Edge Case\] Data belum tersedia di database untuk `kode_wilayah` yang diminta:**
     * **Ekspektasi:** Tetap mengembalikan `200 OK` dengan JSON valid (misalnya *array* kosong `[]`) tanpa memicu *error* `500`.
  3. **\[Negative\] Akses tanpa token valid atau parameter `kode_wilayah` kosong/tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (tanpa token valid) atau `400`/`422` (jika parameter wajib tidak terpenuhi) dalam format JSON.

---

### 4. PKRT — `GET Get Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/kode?kode_wilayah=00&kode=MA1014`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA1014`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data berdasarkan kombinasi `kode_wilayah` dan `kode` indikator:**
     * **Ekspektasi:** Status kode `200 OK` dan respons berupa JSON valid.
  2. **\[Edge Case\] `kode` indikator tidak ditemukan pada `kode_wilayah` tersebut:**
     * **Ekspektasi:** Tetap merespons `200 OK` dengan JSON valid (*array* kosong `[]`) dan tidak terjadi *crash* pada *server*.
  3. **\[Negative\] Parameter wajib (`kode` atau `kode_wilayah`) tidak dikirim atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (token invalid) atau `400`/`422` (parameter kurang) dengan pesan detail JSON.

---

### 5. PKRT — `GET Get Data by Periode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/periode?kode_wilayah=00&periode=2025M12`
* **Parameter Query:** `kode_wilayah` (`00`), `periode` (`2025M12`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data PKRT berdasarkan `kode_wilayah` dan `periode` tertentu:**
     * **Ekspektasi:** Status kode `200 OK`, `Content-Type` `application/json`, waktu respons cepat, dan *body* berupa JSON valid.
  2. **\[Edge Case\] Periode valid secara format (misal `2025M12` atau `2019Q2`) namun belum memiliki data di database:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong `[]` tanpa *server error*.
  3. **\[Negative\] Format `periode` tidak sesuai standar (misal `2025-12` atau `abc`), parameter kosong, atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (jika tidak terautentikasi) atau `400`/`422` (jika format/parameter tidak valid) dalam format JSON.

---

### 6. PKRT — `GET Get Timeseries Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/timeseries?kode_wilayah=00&kode=MA100&start=2024M1&end=2024M12`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`), `start` (`2024M1`), `end` (`2024M12`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data deret waktu (*timeseries*) dalam rentang `start` hingga `end`:**
     * **Ekspektasi:** Status kode `200 OK`, waktu respons di bawah `1000 ms`, dan JSON valid.
     * **Validasi Struktur:** Properti `kode` pada respons sesuai dengan parameter `kode` yang diminta, serta memiliki properti `data` bertipe *array* berisi objek `{ periode, nilai }`.
  2. **\[Edge Case\] Rentang periode `start` sama dengan `end` (1 titik data) atau rentang periode belum memiliki data:**
     * **Ekspektasi:** Status `200 OK` dengan properti `data` berupa *array* berisi 1 elemen atau *array* kosong `[]` secara konsisten.
  3. **\[Negative\] Periode `start` lebih besar dari `end`, format periode salah (misal bulan `M13`), parameter wajib hilang, atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dengan pesan error yang jelas dan tidak mengembalikan `500`.

---

### 7. PKRT — `GET Get Indikator`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/indikator?kode_wilayah=00`
* **Parameter Query:** `kode_wilayah` (`00`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil daftar indikator PKRT pada suatu wilayah:**
     * **Ekspektasi:** Status kode `200 OK`, waktu respons di bawah `1000 ms`, dan JSON valid bertipe *array*.
     * **Validasi Struktur Item:** Jika *array* tidak kosong, setiap elemen harus memiliki *field* `kode` dan `deskripsi` bertipe *string* non-kosong serta nilai `kode` yang unik.
  2. **\[Edge Case\] `kode_wilayah` tidak ditemukan / belum memiliki indikator:**
     * **Ekspektasi:** Status `200 OK` dengan respons berupa *array* kosong `[]`.
  3. **\[Negative\] Parameter `kode_wilayah` tidak dikirim atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (token invalid) atau `400`/`422` (parameter wajib hilang) dalam format JSON.

---

### 8. PKRT — `GET Get Latest Data`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/latest?kode_wilayah=00`
* **Parameter Query:** `kode_wilayah` (`00`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data PKRT periode terbaru berdasarkan `kode_wilayah`:**
     * **Ekspektasi:** Status kode `200 OK`, `Content-Type` `application/json`, waktu respons di bawah `1000 ms`, dan *body* berupa JSON valid.
  2. **\[Edge Case\] Belum ada data sama sekali pada `kode_wilayah` tersebut:**
     * **Ekspektasi:** Status tetap `200 OK` dengan respons JSON kosong (*array* `[]`) tanpa memicu *error* `500` akibat *query* nilai maksimum/terbaru yang kosong.
  3. **\[Negative\] Parameter `kode_wilayah` kosong atau token autentikasi tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dengan pesan error JSON yang informatif.

---

### 9. PKRT — `GET Get Growth Data by Kode and Type`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/growth?kode_wilayah=00&kode=MA1014&type=qtoq`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA1014`), `type` (`qtoq`, opsi lain: `mtom`, `yony_m`, `yotd`, `yony`, `ctoc`, `annual`)
* **Skenario Pengujian:**
  1. **\[Positive\] Hitung dan ambil data pertumbuhan berdasarkan `kode` dan `type`:**
     * **Ekspektasi:** Status kode `200 OK`, respons JSON berbentuk *object* dengan *field* `kode` dan `type` yang sesuai query.
     * **Validasi Struktur Data:** Properti `data` bertipe *array* di mana tiap item memiliki `periode`, `nilai` (*finite number*), dan `growth` (`null` pada periode awal yang tidak punya pembanding, dan angka valid pada periode berikutnya).
  2. **\[Edge Case\] Data hanya tersedia 1 periode (sehingga belum bisa dihitung pertumbuhannya) atau data kosong:**
     * **Ekspektasi:** Status `200 OK` dengan `growth: null` pada periode pertama atau `data: []` tanpa memicu error pembagian dengan nol (`ZeroDivisionError`).
  3. **\[Negative\] Parameter `type` tidak dikenali (di luar daftar jenis growth), parameter wajib hilang, atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (token invalid) atau `400`/`422` dengan detail kesalahan pada parameter `type`/`kode`.

---

### 10. PKRT — `GET Get Quarter Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/quarter?kode_wilayah=00&kode=MA100`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil agregasi data triwulanan berdasarkan `kode_wilayah` dan `kode`:**
     * **Ekspektasi:** Status kode `200 OK`, respons berupa objek JSON valid dengan *field* `kode` yang sesuai query dan properti `data` bertipe *array*.
  2. **\[Edge Case\] Kode tidak dikenal, data bulanan tidak lengkap dalam satu triwulan, atau data kosong:**
     * **Ekspektasi:** Mengembalikan `200 OK`, `data: []`, serta tetap mencantumkan `kode` yang diminta tanpa *error* `500`.
  3. **\[Negative\] Parameter wajib (`kode`/`kode_wilayah`) kosong atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dengan pesan detail JSON (`detail`/`message`), bukan `500`.

---

### 11. PKRT — `GET Get Annual Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/annual?kode_wilayah=00&kode=MA100`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil agregasi data tahunan berdasarkan `kode_wilayah` dan `kode`:**
     * **Ekspektasi:** Status kode `200 OK`, respons objek JSON valid dengan `kode` yang sesuai query dan properti `data` bertipe *array*.
  2. **\[Edge Case\] Kode tidak dikenal atau data tahunan belum tersedia:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan `data: []` dan tetap melakukan *echo* terhadap `kode` yang diminta tanpa *internal server error* (`500`).
  3. **\[Negative\] Parameter wajib hilang/kosong atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dengan pesan detail JSON.

---

### 12. PKRT — `GET Get Chart Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/chart?kode_wilayah=00&kode=MA100`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data format grafik standar berdasarkan `kode`:**
     * **Ekspektasi:** Status kode `200 OK`, waktu respons di bawah `500 ms`, dan JSON valid.
     * **Validasi Struktur:** Memiliki properti `kode`, `xAxis`, dan `series` (bertipe *array*).
  2. **\[Edge Case\] Data kosong untuk `kode` atau `kode_wilayah` tertentu:**
     * **Ekspektasi:** Tetap mengembalikan `200 OK` dengan struktur `xAxis` dan `series` berupa *array* kosong `[]` agar komponen grafik *frontend* tidak *error*.
  3. **\[Negative\] Parameter wajib (`kode`/`kode_wilayah`) tidak dikirim atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (tanpa token valid) atau `400`/`422` (parameter tidak lengkap) dalam format JSON.

---

### 13. PKRT — `GET Get Growth Chart Data by Kode and Type`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/growth/chart?kode_wilayah=00&kode=MA100&type=ctoc`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`), `type` (`ctoc`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data format grafik pertumbuhan berdasarkan `kode` dan `type`:**
     * **Ekspektasi:** Status kode `200 OK`, waktu respons di bawah `500 ms`, dan JSON valid.
     * **Validasi Struktur:** Memiliki properti `kode`, `type`, `xAxis` (*array*), dan `series` (*array*).
  2. **\[Edge Case\] Data pertumbuhan kosong atau nilai pembanding bernilai nol:**
     * **Ekspektasi:** Tetap mengembalikan `200 OK` dengan `xAxis: []` dan `series: []` (atau nilai `null` pada titik yang tidak terdefinisi) tanpa memicu `500 Internal Server Error`.
  3. **\[Negative\] Parameter `type` tidak valid, parameter wajib kosong, atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dengan pesan error JSON yang jelas.

---

### 14. PKRT — `GET Get Quarter Chart Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/quarter/chart?kode_wilayah=00&kode=MA100`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data format grafik triwulanan berdasarkan `kode`:**
     * **Ekspektasi:** Status kode `200 OK`, waktu respons di bawah `500 ms`, dan JSON valid.
     * **Validasi Struktur:** Memiliki properti `kode`, `xAxis`, dan `series` (*array*).
  2. **\[Edge Case\] Data triwulanan belum tersedia untuk kode/wilayah tersebut:**
     * **Ekspektasi:** Tetap mengembalikan `200 OK` dengan `xAxis` dan `series` berupa *array* kosong `[]`.
  3. **\[Negative\] Parameter wajib hilang/kosong atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dalam format JSON tanpa error `500`.

---

### 15. PKRT — `GET Get Annual Chart Data by Kode`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/annual/chart?kode_wilayah=00&kode=MA100`
* **Parameter Query:** `kode_wilayah` (`00`), `kode` (`MA100`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data format grafik tahunan berdasarkan `kode`:**
     * **Ekspektasi:** Status kode `200 OK` dan JSON valid dengan kode metadata yang mencerminkan `kode` dan `kode_wilayah` pada parameter *request*.
  2. **\[Edge Case\] Kode tidak dikenal / data tahunan kosong:**
     * **Ekspektasi:** Tetap mengembalikan `200 OK` dengan *array* data kosong dan tetap melakukan *echo* terhadap `kode` yang diminta tanpa *error* `500`.
  3. **\[Negative\] Token tidak valid atau parameter wajib kosong/tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `400`/`422` dengan detail pesan error yang jelas dan tidak pernah mengembalikan `500 Internal Server Error`.

---

### 16. PKRT — `GET Get Aggregated Data`

* **Endpoint:** `{{base_url}}/api/v1/pkrt/aggregated?kode_wilayah=00`
* **Parameter Query:** `kode_wilayah` (`00`)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil seluruh data teragregasi PKRT pada suatu wilayah:**
     * **Ekspektasi:** Status kode `200 OK`, `Content-Type` `application/json`, waktu respons di bawah `500 ms`, dan *body* berupa objek JSON valid.
     * **Validasi Struktur:**
       * Memiliki properti tingkat atas `data` bertipe *object* (bukan *array*).
       * Setiap entri indikator di dalam `data` memuat objek `indikator` (memiliki *field* `string`: `kode`, `deskripsi`, `satuan`, `freq`, `konversi`) dan objek `series`.
       * Pada setiap *bucket* di dalam `series` yang memiliki `periods` dan `values`, keduanya bertipe *array* dengan panjang elemen (`length`) yang sama persis.
  2. **\[Edge Case\] Wilayah belum memiliki data teragregasi atau sebagian *bucket* frekuensi (bulanan/triwulanan/tahunan) kosong:**
     * **Ekspektasi:** Tetap mengembalikan `200 OK` dengan struktur objek `data` kosong `{}` atau *array* `periods` dan `values` yang sama-sama kosong `[]` tanpa *server error*.
  3. **\[Negative\] Parameter `kode_wilayah` tidak dikirim/tidak valid atau token autentikasi tidak valid:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` (tanpa token valid) atau `400`/`422` (parameter wajib hilang) dalam format JSON yang valid.