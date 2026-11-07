# 🚀 Panduan Lengkap Deployment Backend FastAPI ke Google Cloud Platform (GCP)

Selamat datang! Dokumen ini adalah panduan langkah demi langkah (SOP) untuk mengunggah (deploy) aplikasi **Backend FastAPI** dan database **PostgreSQL** ke Google Cloud Platform.

Kita akan menggunakan dua layanan utama dari Google:

1. **Cloud SQL**: Tempat kita menyimpan database PostgreSQL.

2. **Cloud Run**: Tempat kita menjalankan kode aplikasi FastAPI kita (tanpa perlu repot mengurus server fisik).

## 📌 Persiapan Awal (Wajib Dibaca)

Sebelum mengetik perintah apa pun, pastikan kamu sudah menyiapkan hal-hal berikut:

1. **Memiliki Akun Google Cloud (GCP):**

   * Kunjungi [console.cloud.google.com](https://console.cloud.google.com/).

   * Login dengan akun Google/Gmail.

   * Jika ini pertama kalinya, aktifkan **Free Trial (\$300)** (Mungkin akan diminta kartu debit/kredit untuk verifikasi, tapi tidak akan dipotong biayanya).

2. **Membuat Proyek (Project) di GCP:**

   * Di bagian atas layar (sebelah logo Google Cloud), klik menu *dropdown* proyek.

   * Klik **New Project**, beri nama (misalnya: `dnpeng-backend-prod`), lalu klik **Create**.

   * Catat **Project ID** kamu (biasanya nama proyek ditambah angka acak, misal: `dnpeng-backend-prod-123456`).

3. **Menginstal Google Cloud CLI (`gcloud`) di Laptop Kamu:**

   * Ini adalah alat agar kita bisa memerintah Google Cloud langsung dari terminal VS Code.

   * Download dan instal dari sini: [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

   * Buka terminal/Command Prompt, lalu ketik `gcloud --version` untuk memastikan instalasi berhasil.

## 🛠️ Langkah 1: Hubungkan Terminal Komputer ke Akun GCP

Kita perlu memberi tahu komputer kita agar terhubung dengan akun Google Cloud yang baru saja kamu buat.

1. Buka Terminal di VS Code.
2. Jalankan perintah ini untuk login, lalu tekan Enter:

   ```
   gcloud auth login
   
   ```
   *(Browser akan otomatis terbuka, silakan pilih akun Gmail kamu dan klik "Allow/Izinkan")*

3. Atur terminal agar fokus menggunakan proyek yang sudah Anda buat tadi:
   ```
   gcloud config set project [MASUKKAN_PROJECT_ID_KAMU_DI_SINI]
   
   ```
   (Penting: Ganti teks di dalam kurung siku dengan Project ID asli milik Anda, tanpa menggunakan tanda kurung siku. Contoh: gcloud config set project dnpeng-backend-prod-123456)

4. Aktifkan fitur-fitur (API) Google Cloud yang akan kita pakai:

   ```
   gcloud services enable run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
   
   ```

## 🗄️ Langkah 2: Membuat Database PostgreSQL (Cloud SQL)

Sekarang kita akan membuat rumah untuk data kita.

1. **Buat server database-nya:**
   Proses ini akan memakan waktu sekitar 3-5 menit. Jangan tutup terminal!

   ```
   gcloud sql instances create dnpeng-db-instance --database-version=POSTGRES_14 --cpu=1 --memory=3840MiB --region=asia-southeast2 --root-password=[BUAT_PASSWORD_YANG_KUAT]
   
   ```

   *(Penjelasan: Kita menamai servernya `dnpeng-db-instance`, menaruhnya di server Jakarta `asia-southeast2` agar cepat diakses)*

2. **Buat database bernama `dnpeng_db` di dalam server tersebut:**

   ```
   gcloud sql databases create dnpeng_db --instance=dnpeng-db-instance
   
   ```

3. **Buat akun pengguna khusus (user) untuk aplikasi FastAPI kita:**

   ```
   gcloud sql users create dnpeng_user --instance=dnpeng-db-instance --password=[BUAT_PASSWORD_UNTUK_USER_INI]
   
   ```

## 📦 Langkah 3: Mengemas Aplikasi (Build Image)

Karena aplikasi kita menggunakan Docker, kita harus membungkus semua file kodenya. Daripada repot mengemas di laptop yang bikin berat, kita suruh Google (Cloud Build) yang mengemasnya.

Pastikan posisi terminal Anda sekarang berada tepat di dalam folder proyek (folder yang berisi file Dockerfile). 

Jalankan perintah ini:

   ```
   gcloud builds submit --tag gcr.io/[MASUKKAN_PROJECT_ID_KAMU_DI_SINI]/dnpeng-backend-fastapi:v1 .

   ```
(Catatan Penting: Jangan lupakan tanda titik  . di paling akhir perintah! Tanda titik itu artinya "tolong bungkus semua file yang ada di folder tempat saya berada saat ini".)

## 🚀 Langkah 4: Luncurkan Aplikasi ke Cloud Run (Deploy)

Ini adalah langkah paling penting. Kita akan meluncurkan aplikasi yang sudah dibungkus tadi ke internet dan menyambungkannya dengan database.

Jalankan perintah panjang ini (ganti bagian yang berada di dalam kurung siku `[...]` sesuai dengan data kamu sebelumnya):

```
gcloud run deploy dnpeng-backend-fastapi \
    --image gcr.io/[PROJECT_ID_KAMU]/dnpeng-backend-fastapi:v1 \
    --platform managed \
    --region asia-southeast2 \
    --allow-unauthenticated \
    --add-cloudsql-instances [PROJECT_ID_KAMU]:asia-southeast2:dnpeng-db-instance \
    --set-env-vars DATABASE_URL="postgresql+psycopg2://dnpeng_user:[PASSWORD_USER_DB_LANGKAH_2]@/dnpeng_db?host=/cloudsql/[PROJECT_ID_KAMU]:asia-southeast2:dnpeng-db-instance"

```

**Jika berhasil:**
Terminal akan memunculkan sebuah **URL (Link Internet)**, misalnya:
`https://dnpeng-backend-fastapi-xyz-et.a.run.app`

Selamat! Aplikasimu sudah online! 🎉

## 🗂️ Langkah 5: Membuat Tabel Database (Migrasi Alembic)

Aplikasi sudah jalan, database sudah ada, tapi tabel-tabelnya (seperti tabel inventori, pklnprt) masih kosong. Kita harus menjalankan migrasi.

Cara paling mudah (via Cloud SQL Auth Proxy lokal):

1. Download dan jalankan Cloud SQL Auth Proxy di lokal kamu agar terhubung ke database cloud. (Lihat panduan lengkapnya di [sini](https://cloud.google.com/sql/docs/postgres/sql-proxy)).

2. Jalankan perintah Proxy di terminal baru:

   ```
   ./cloud-sql-proxy [PROJECT_ID_KAMU]:asia-southeast2:dnpeng-db-instance
   
   ```

3. Buka file `.env` di VS Code kamu, ubah `DATABASE_URL` sementara menjadi:
   `postgresql+psycopg2://dnpeng_user:[PASSWORD_USER_DB_LANGKAH_2]@127.0.0.1:5432/dnpeng_db`

4. Jalankan perintah migrasi di terminal VS Code:

   ```
   alembic upgrade head
   
   ```

## ✅ Langkah 6: Verifikasi Hasil

Buka browser kamu (Chrome/Firefox/Edge) dan masukkan URL yang didapat dari Langkah 4, lalu tambahkan `/docs` di belakangnya.

Contoh:
`https://dnpeng-backend-fastapi-xyz-et.a.run.app/docs`

Jika kamu melihat halaman **Swagger UI FastAPI**, maka deployment kamu telah **100% SUKSES!**