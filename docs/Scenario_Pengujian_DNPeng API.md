# Skenario Pengujian API — Autentikasi & 7 Modul Data (`DNPeng API`)

Dokumen ini berisi rincian skenario pengujian lengkap untuk seluruh *endpoint* pada **DNPeng API**, mencakup **Autentikasi** serta **7 modul data**: **PKRT**, **PKP**, **PMTB**, **EKSIM**, **PDB**, **PKLNPRT**, dan **INVENTORI**.

Seluruh *endpoint* modul data dilindungi oleh mekanisme autentikasi **Bearer Token (JWT)** dan diuji menggunakan **Postman Collection Runner** dengan tiga kategori kasus pengujian:
* **Positive Case:** Alur normal dengan token, parameter query, dan *payload* yang valid.
* **Edge Case:** Kondisi batas seperti data kosong (*empty array/object*) atau satu titik data pada perhitungan pertumbuhan.
* **Negative Case:** Pengujian duplikasi data pada `POST .../data` (`kode_wilayah`, `kode`, `tahun`, `freq`, `period` yang sama), akses tanpa token/token tidak valid (`401`), serta kesalahan tipe/format parameter maupun *payload* (`400`/`409`/`422`).

---

## Ringkasan Daftar Endpoint & Skenario per Modul

### A. Modul Autentikasi (`Auth` — 1 Endpoint)

| No | Nama Request | Method | Endpoint | Autentikasi |
| :---: | :--- | :---: | :--- | :---: |
| 1 | Login User | `POST` | `/api/v1/auth/login` | No Auth |

---

### B. Modul Berbasis Frekuensi Bulanan/Triwulanan (`PKRT`, `PKP`, `PMTB`, `EKSIM`, `PKLNPRT`, `INVENTORI` — 16 Request per Modul)

Setiap modul pada kelompok ini memiliki **16 *request*** (termasuk pengujian duplikat pada `POST .../data`) dengan pola *endpoint* sebagai berikut *(ganti `{modul}` dengan `pkrt`, `pkp`, `pmtb`, `eksim`, `pklnprt`, atau `inventori`)*:

| No | Nama Request | Method | Endpoint | Autentikasi |
| :---: | :--- | :---: | :--- | :---: |
| 1 | Add Data | `POST` | `/api/v1/{modul}/data` | Bearer Token |
| 2 | Add Data (Duplicate - Expect Fail) | `POST` | `/api/v1/{modul}/data` | Bearer Token |
| 3 | Get Data | `GET` | `/api/v1/{modul}/data` | Bearer Token |
| 4 | Get Data by Kode | `GET` | `/api/v1/{modul}/kode` | Bearer Token |
| 5 | Get Data by Periode | `GET` | `/api/v1/{modul}/periode` | Bearer Token |
| 6 | Get Timeseries Data by Kode | `GET` | `/api/v1/{modul}/timeseries` | Bearer Token |
| 7 | Get Indikator | `GET` | `/api/v1/{modul}/indikator` | Bearer Token |
| 8 | Get Latest Data | `GET` | `/api/v1/{modul}/latest` | Bearer Token |
| 9 | Get Growth Data by Kode and Type | `GET` | `/api/v1/{modul}/growth` | Bearer Token |
| 10 | Get Quarter Data by Kode | `GET` | `/api/v1/{modul}/quarter` | Bearer Token |
| 11 | Get Annual Data by Kode | `GET` | `/api/v1/{modul}/annual` | Bearer Token |
| 12 | Get Chart Data by Kode | `GET` | `/api/v1/{modul}/chart` | Bearer Token |
| 13 | Get Growth Chart Data by Kode and Type | `GET` | `/api/v1/{modul}/growth/chart` | Bearer Token |
| 14 | Get Quarter Chart Data by Kode | `GET` | `/api/v1/{modul}/quarter/chart` | Bearer Token |
| 15 | Get Annual Chart Data by Kode | `GET` | `/api/v1/{modul}/annual/chart` | Bearer Token |
| 16 | Get Aggregated Data | `GET` | `/api/v1/{modul}/aggregated` | Bearer Token |

---

### C. Modul Produk Domestik Bruto (`PDB` — 13 Request)

Modul **PDB** memiliki struktur data berbasis triwulanan dengan parameter `jenis` (`ADHB` / `ADHK`) dan tipe `kode` berupa bilangan bulat (`integer`), terdiri dari **13 *request***:

| No | Nama Request | Method | Endpoint | Autentikasi |
| :---: | :--- | :---: | :--- | :---: |
| 1 | Add Data | `POST` | `/api/v1/pdb/data` | Bearer Token |
| 2 | Add Data (Duplicate - Expect Fail) | `POST` | `/api/v1/pdb/data` | Bearer Token |
| 3 | Get Data | `GET` | `/api/v1/pdb/data` | Bearer Token |
| 4 | Get Data by Kode | `GET` | `/api/v1/pdb/kode` | Bearer Token |
| 5 | Get Data by Periode | `GET` | `/api/v1/pdb/periode` | Bearer Token |
| 6 | Get Timeseries Data by Kode | `GET` | `/api/v1/pdb/timeseries` | Bearer Token |
| 7 | Get Indikator | `GET` | `/api/v1/pdb/indikator` | Bearer Token |
| 8 | Get Latest Data | `GET` | `/api/v1/pdb/latest` | Bearer Token |
| 9 | Get Growth Data by Kode and Type | `GET` | `/api/v1/pdb/growth` | Bearer Token |
| 10 | Get Annual Data by Kode | `GET` | `/api/v1/pdb/annual` | Bearer Token |
| 11 | Get Chart Data by Kode | `GET` | `/api/v1/pdb/chart` | Bearer Token |
| 12 | Get Growth Chart Data by Kode and Type | `GET` | `/api/v1/pdb/growth/chart` | Bearer Token |
| 13 | Get Annual Chart Data by Kode | `GET` | `/api/v1/pdb/annual/chart` | Bearer Token |

---

## Rincian Skenario Pengujian per Endpoint

### 1. Autentikasi — `POST Login User`

* **Endpoint:** `{{base_url}}/api/v1/auth/login`
* **Body (`x-www-form-urlencoded`):** `username` (`admin@admin.com`), `password` (`admin123`)
* **Skenario Pengujian:**
  1. **\[Positive\] Login dengan kredensial valid:**
     * **Ekspektasi:** Status kode `200 OK`, `Content-Type` `application/json`, dan waktu respons di bawah `1000 ms`.
     * **Validasi Struktur:** *Response body* memiliki *key* `access_token`, `refresh_token`, `token_type` (`bearer`), dan objek `user` (`id`, `name`, `email`, `role`).
     * **Aksi Lanjutan:** Menyimpan nilai `access_token` dan `refresh_token` ke dalam *environment variable* Postman untuk seluruh *request* berikutnya.
  2. **\[Edge Case\] Input username mengandung spasi di awal/akhir atau perbedaan huruf kapital:**
     * **Ekspektasi:** Sistem menangani normalisasi atau menolak dengan bersih (`401` / `422`) tanpa memicu `500 Internal Server Error`.
  3. **\[Negative\] Login dengan password salah, user tidak terdaftar, atau field wajib kosong:**
     * **Ekspektasi:** Mengembalikan status `401 Unauthorized` atau `422 Unprocessable Entity` dalam format JSON valid.

---

### 2. Insert Data — `POST /api/v1/{modul}/data` (`Add Data`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Header:** `Authorization: Bearer {{access_token}}`
* **Contoh Parameter Khusus:**
  * `pkrt`, `pkp`, `pmtb`, `eksim`, `pklnprt`, `inventori`: `kode` bertipe `string` (contoh: `"MA1014"`, `"MKP001"`), `periode` format `YYYYM1-12` atau `YYYYQ1-4`.
  * `pdb`: `kode` bertipe `integer` (contoh: `10000`), `jenis` (`"ADHB"` atau `"ADHK"`), `periode` format `YYYYQ1-4`.
* **Skenario Pengujian:**
  1. **\[Positive\] Tambah data baru dengan payload dan token valid:**
     * **Ekspektasi:** Status kode `200 OK` (atau `201 Created`) dengan *response body* JSON yang sesuai skema modul.
  2. **\[Edge Case\] Pengiriman nilai angka `0` atau nilai negatif pada komponen tertentu (misal perubahan inventori / net ekspor):**
     * **Ekspektasi:** Sistem menerima angka *floating-point* valid dan menyimpannya dengan benar tanpa *error* validasi.
  3. **\[Negative\] Akses tanpa token atau token kedaluwarsa:**
     * **Ekspektasi:** Mengembalikan status `401 Unauthorized` atau `403 Forbidden`.
  4. **\[Negative\] Format payload tidak valid (misal format `periode` salah, `jenis` selain `ADHB`/`ADHK` pada PDB, atau tipe data salah):**
     * **Ekspektasi:** Mengembalikan status `400 Bad Request` atau `422 Unprocessable Entity`.

---

### 3. Validasi Duplikasi Insert Data — `POST /api/v1/{modul}/data` (`Add Data (Duplicate - Expect Fail)`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Header:** `Authorization: Bearer {{access_token}}`
* **Skenario Pengujian:**
  1. **\[Negative\] Insert ulang data dengan kunci unik yang sama (`kode_wilayah`, `kode`, `tahun`, `freq`, dan `period` identik — serta `jenis` yang sama untuk PDB):**
     * **Ekspektasi:** Sistem menolak proses penyimpanan ganda (*IntegrityError* ditangani dengan baik), melakukan *rollback* transaksi database, dan mengembalikan status `409 Conflict` (atau `400`/`422`) dalam format JSON valid tanpa memicu `500 Internal Server Error`.

---

### 4. Ambil Semua Data Wilayah — `GET /api/v1/{modul}/data` (`Get Data`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00` (opsional: `kode`, `periode`, serta `jenis` khusus PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil daftar data berdasarkan `kode_wilayah` valid dengan token aktif:**
     * **Ekspektasi:** Status `200 OK`, waktu respons `< 1000 ms`, dan *body* berupa *array* JSON valid.
  2. **\[Edge Case\] Wilayah belum memiliki data pada tabel modul terkait:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong `[]`.
  3. **\[Negative\] Akses tanpa Bearer Token atau tanpa parameter wajib `kode_wilayah`:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `422 Unprocessable Entity`.

---

### 5. Ambil Data Berdasarkan Kode — `GET /api/v1/{modul}/kode` (`Get Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode_indikator}` (ditambah `&jenis=ADHK` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil seluruh histori data untuk kombinasi `kode_wilayah` dan `kode` tertentu:**
     * **Ekspektasi:** Status `200 OK` dan respons *array* JSON valid sesuai tipe data `kode` masing-masing modul (`string` untuk 6 modul, `number` untuk PDB).
  2. **\[Edge Case\] `kode` indikator tidak ditemukan pada wilayah yang diminta:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong `[]`.
  3. **\[Negative\] Parameter wajib `kode` tidak dikirim atau tipe parameter tidak sesuai (misal `kode=abc` pada PDB):**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` (atau `401` jika tanpa token).

---

### 6. Ambil Data Berdasarkan Periode — `GET /api/v1/{modul}/periode` (`Get Data by Periode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&periode={periode}` (ditambah `&jenis=ADHB` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil seluruh indikator pada `kode_wilayah` dan `periode` tertentu:**
     * **Ekspektasi:** Status `200 OK`, `Content-Type` `application/json`, dan *body* JSON valid.
  2. **\[Edge Case\] Periode memiliki format valid namun belum memiliki data:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong `[]`.
  3. **\[Negative\] Format `periode` salah (misal `2025-12`) atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `400`/`422` atau `401 Unauthorized`.

---

### 7. Ambil Data Deret Waktu — `GET /api/v1/{modul}/timeseries` (`Get Timeseries Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}&start={start}&end={end}` (ditambah `&jenis=ADHB` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data *timeseries* dalam rentang periode `start` hingga `end`:**
     * **Ekspektasi:** Status `200 OK`, properti `kode` sesuai parameter query, dan properti `data` berisi *array* objek `{ periode, nilai }`.
  2. **\[Edge Case\] `start` sama dengan `end` atau rentang periode kosong:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan `data` berisi 1 elemen atau *array* kosong `[]`.
  3. **\[Negative\] `start` lebih besar dari `end`, parameter wajib hilang, atau tanpa token:**
     * **Ekspektasi:** Mengembalikan `400`/`422` atau `401 Unauthorized`.

---

### 8. Ambil Daftar Indikator — `GET /api/v1/{modul}/indikator` (`Get Indikator`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00`
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil daftar kode dan deskripsi indikator unik pada suatu wilayah:**
     * **Ekspektasi:** Status `200 OK`, respons bertipe *array*, setiap item memiliki `kode` dan `deskripsi` yang tidak kosong.
  2. **\[Edge Case\] Wilayah belum memiliki indikator terdaftar:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong `[]`.
  3. **\[Negative\] Parameter `kode_wilayah` hilang atau token tidak valid:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

### 9. Ambil Data Periode Terbaru — `GET /api/v1/{modul}/latest` (`Get Latest Data`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00` (opsional: `&jenis=ADHB` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil seluruh data pada periode paling mutakhir yang tersedia di database:**
     * **Ekspektasi:** Status `200 OK`, waktu respons `< 1000 ms`, dan *body* JSON valid.
  2. **\[Edge Case\] Tabel modul kosong untuk wilayah tersebut:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong `[]` tanpa *error* `500`.
  3. **\[Negative\] Akses tanpa token atau parameter `kode_wilayah` tidak dikirim:**
     * **Ekspektasi:** Mengembalikan `401 Unauthorized` atau `422 Unprocessable Entity`.

---

### 10. Ambil Data Pertumbuhan — `GET /api/v1/{modul}/growth` (`Get Growth Data by Kode and Type`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}&type={type}` (ditambah `&jenis=ADHK` untuk PDB; opsi `type`: `qtoq`, `mtom`, `yony_m`, `yotd`, `yony`, `ctoc`, `annual`)
* **Skenario Pengujian:**
  1. **\[Positive\] Hitung pertumbuhan berdasarkan `kode` dan `type`:**
     * **Ekspektasi:** Status `200 OK`, respons objek JSON dengan `kode` dan `type` yang cocok dengan query, serta `data` berisi objek `{ periode, nilai, growth }`.
  2. **\[Edge Case\] Periode awal yang tidak memiliki periode pembanding atau nilai pembanding bernilai `0`:**
     * **Ekspektasi:** Status `200 OK` dengan nilai `growth: null` pada titik tersebut tanpa memicu `ZeroDivisionError` (`500`).
  3. **\[Negative\] Nilai `type` di luar opsi yang didukung atau tanpa token:**
     * **Ekspektasi:** Mengembalikan `400`/`422` atau `401 Unauthorized`.

---

### 11. Ambil Agregasi Triwulanan — `GET /api/v1/{modul}/quarter` (`Get Quarter Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}`
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data hasil konversi/agregasi triwulanan berdasarkan `kode`:**
     * **Ekspektasi:** Status `200 OK`, objek JSON valid dengan `kode` sesuai query dan `data` bertipe *array*.
  2. **\[Edge Case\] Data bulanan belum lengkap untuk membentuk triwulan atau `kode` tidak ditemukan:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan `data: []`.
  3. **\[Negative\] Parameter wajib hilang atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

### 12. Ambil Agregasi Tahunan — `GET /api/v1/{modul}/annual` (`Get Annual Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}` (ditambah `&jenis=ADHK` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data hasil agregasi tahunan berdasarkan `kode`:**
     * **Ekspektasi:** Status `200 OK`, objek JSON valid dengan `kode` sesuai query dan `data` bertipe *array*.
  2. **\[Edge Case\] Data tahunan belum tersedia untuk `kode` tersebut:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan `data: []`.
  3. **\[Negative\] Parameter wajib kosong atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

### 13. Ambil Data Grafik Standar — `GET /api/v1/{modul}/chart` (`Get Chart Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}` (ditambah `&jenis=ADHK` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil struktur data siap pakai untuk visualisasi grafik (`kode`, `xAxis`, `series`):**
     * **Ekspektasi:** Status `200 OK`, waktu respons `< 1000 ms`, dan properti `xAxis` serta `series` bertipe *array*.
  2. **\[Edge Case\] Data indikator kosong pada wilayah yang diminta:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan `xAxis: []` dan `series: []`.
  3. **\[Negative\] Parameter wajib tidak dikirim atau tanpa token:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

### 14. Ambil Data Grafik Pertumbuhan — `GET /api/v1/{modul}/growth/chart` (`Get Growth Chart Data by Kode and Type`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}&type={type}` (ditambah `&jenis=ADHK` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data visualisasi grafik pertumbuhan (`kode`, `type`, `xAxis`, `series`):**
     * **Ekspektasi:** Status `200 OK` dan seluruh properti grafik memiliki tipe data yang sesuai.
  2. **\[Edge Case\] Data pertumbuhan kosong atau hanya memiliki 1 titik periode:**
     * **Ekspektasi:** Mengembalikan `200 OK` tanpa *server error*.
  3. **\[Negative\] Parameter `type` tidak valid atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `400`/`422` atau `401 Unauthorized`.

---

### 15. Ambil Data Grafik Triwulanan — `GET /api/v1/{modul}/quarter/chart` (`Get Quarter Chart Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}`
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data visualisasi grafik triwulanan (`kode`, `xAxis`, `series`):**
     * **Ekspektasi:** Status `200 OK` dengan struktur `xAxis` dan `series` bertipe *array*.
  2. **\[Edge Case\] Data triwulanan kosong:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong.
  3. **\[Negative\] Parameter wajib kosong atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

### 16. Ambil Data Grafik Tahunan — `GET /api/v1/{modul}/annual/chart` (`Get Annual Chart Data by Kode`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pdb`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00&kode={kode}` (ditambah `&jenis=ADHK` untuk PDB)
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil data visualisasi grafik tahunan (`kode`, `xAxis`, `series`):**
     * **Ekspektasi:** Status `200 OK` dan JSON valid.
  2. **\[Edge Case\] Data tahunan kosong:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan *array* kosong.
  3. **\[Negative\] Parameter wajib kosong atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

### 17. Ambil Data Teragregasi Wilayah — `GET /api/v1/{modul}/aggregated` (`Get Aggregated Data`)

* **Berlaku untuk:** `pkrt`, `pkp`, `pmtb`, `eksim`, `pklnprt`, `inventori`
* **Parameter Query:** `kode_wilayah=00`
* **Skenario Pengujian:**
  1. **\[Positive\] Ambil seluruh paket data indikator dan seri waktu teragregasi pada suatu wilayah:**
     * **Ekspektasi:** Status `200 OK`, memiliki properti tingkat atas `data` bertipe *object*, setiap entri memuat `indikator` (`kode`, `deskripsi`, `satuan`, `freq`, `konversi`) dan `series` dengan panjang *array* `periods` dan `values` yang sama persis.
  2. **\[Edge Case\] Wilayah belum memiliki data teragregasi:**
     * **Ekspektasi:** Mengembalikan `200 OK` dengan `data: {}` tanpa memicu `404 Not Found` maupun `500 Internal Server Error`.
  3. **\[Negative\] Parameter `kode_wilayah` tidak dikirim atau akses tanpa token:**
     * **Ekspektasi:** Mengembalikan `422 Unprocessable Entity` atau `401 Unauthorized`.

---

## Rekapitulasi Jumlah Request per Modul (Sinkron dengan Postman Collection)

| No | Folder / Modul | Jumlah Request | Keterangan |
| :---: | :--- | :---: | :--- |
| 1 | `Auth` | 1 | `POST /api/v1/auth/login` |
| 2 | `PKRT` | 16 | Termasuk `POST Add Data` & `POST Add Data (Duplicate - Expect Fail)` |
| 3 | `PKP` | 16 | Termasuk `POST Add Data` & `POST Add Data (Duplicate - Expect Fail)` |
| 4 | `PMTB` | 16 | Termasuk `POST Add Data` & `POST Add Data (Duplicate - Expect Fail)` |
| 5 | `EKSIM` | 16 | Termasuk `POST Add Data` & `POST Add Data (Duplicate - Expect Fail)` |
| 6 | `PDB` | 13 | Tanpa `/quarter`, `/quarter/chart`, dan `/aggregated`; termasuk duplikat `POST` |
| 7 | `PKLNPRT` | 16 | Termasuk `POST Add Data` & `POST Add Data (Duplicate - Expect Fail)` |
| 8 | `INVENTORI` | 16 | Termasuk `POST Add Data` & `POST Add Data (Duplicate - Expect Fail)` |
| **Total** | **Seluruh Koleksi** | **110** | **100% Konsisten antara Dokumentasi MD & Postman Collection** |