# UTS Sistem Terdistribusi – Log Aggregator (Pub-Sub with Idempotent Consumer)

Proyek ini dibuat untuk memenuhi tugas UTS Sistem Terdistribusi.
Tema: Pub-Sub Log Aggregator dengan Idempotent Consumer dan Deduplication.

## Deskripsi Singkat

Aplikasi ini merupakan layanan log aggregator berbasis FastAPI (Python) yang:

Menerima event dari publisher melalui endpoint /publish

Memproses event melalui subscriber/consumer secara idempotent

Melakukan deduplication agar event yang sama tidak diproses dua kali

Menyimpan event unik ke database SQLite yang tahan restart (persistent)

Menyediakan statistik sistem lewat endpoint /stats

## Arsitektur Sederhana
[Publisher] → POST /publish → [Aggregator (FastAPI)]
                   ↓
            [asyncio Queue]
                   ↓
         [Consumer + SQLite Dedup Store]
                   ↓
           GET /events & /stats


Pattern komunikasi: Publish–Subscribe (local queue)
Semantik pengiriman: At-least-once delivery

## Cara Menjalankan (Build & Run)
1. Build Docker image
docker build -t uts-aggregator .
2. Jalankan container
docker run -p 8080:8080 -v ${PWD}\data:/app\data uts-aggregator


Pastikan Docker Desktop sudah berjalan.
3. Coba akses API
curl http://localhost:8080/stats

## Endpoint API
Method	Endpoint	Deskripsi
POST	/publish	Menerima single event atau batch event
GET	/events?topic=...	Mengambil daftar event unik yang sudah diproses
GET	/stats	Menampilkan statistik sistem (received, unique_processed, duplicate_dropped, dll)
## Contoh Payload
Single Event
{
  "topic": "t",
  "event_id": "e1",
  "timestamp": "2025-10-24T00:00:00Z",
  "source": "cli",
  "payload": {"msg": "hello"}
}

Batch Event
{
  "events": [
    {
      "topic": "t",
      "event_id": "e1",
      "timestamp": "2025-10-24T00:00:00Z",
      "source": "cli",
      "payload": {"msg": "hello"}
    },
    {
      "topic": "t",
      "event_id": "e2",
      "timestamp": "2025-10-24T00:01:00Z",
      "source": "cli",
      "payload": {"msg": "world"}
    }
  ]
}

## Statistik Contoh

Respon dari /stats:

{
  "received": 10,
  "unique_processed": 8,
  "duplicate_dropped": 2,
  "topics": ["t"],
  "uptime_seconds": 122
}

## Fitur Utama

Idempotent consumer: event dengan (topic, event_id) sama hanya diproses sekali.

Deduplication: mencegah event duplikat diproses ulang.

Persistent dedup store: SQLite menyimpan ID event agar tahan restart.

Observability: endpoint /stats memantau performa sistem.

At-least-once semantics: mendukung retry dari publisher.

## Unit Test (pytest)

Jalankan semua test:

pytest -v


Test meliputi:

Validasi schema event

Deduplication

Persistensi setelah restart

Konsistensi /stats dan /events

Stress test kecil (batch event)

## Video Demo
YouTube – Demo UTS Sistem Terdistribusi

https://youtu.be/cdMD3cmt1mE

Isi video:

1. Build Docker image
2. Jalankan container
3. Kirim event unik dan duplikat
4. Tunjukkan hasil /stats dan /events
5. Restart container → dedup tetap bekerja

## Link Laporan
https://drive.google.com/file/d/1sDasug0Mff_UnEoH2i-UUk_PJ1-CX__k/view?usp=sharing


## Referensi

Van Steen, M., & Tanenbaum, A. S. (2023). Distributed systems (4th ed., Version 4.01).

## Identitas

Nama: Anitya C. R. Sinaga

NIM: 11231011

Program Studi: Informatika 2023 – Institut Teknologi Kalimantan (ITK)

Mata Kuliah: Sistem Terdistribusi Kelas A

Dosen Pengampu: Riska Kurniyanto Abdullah, S.T., M.Kom.

## Catatan Tambahan

Sistem ini berjalan sepenuhnya lokal di Docker, tanpa jaringan eksternal.

Jika port 8080 sudah terpakai, gunakan -p 8081:8080.

Folder data/ menyimpan database SQLite dan tidak boleh dihapus jika ingin mempertahankan riwayat event.