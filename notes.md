"membangun Docker image untuk service aggregator menggunakan Dockerfile utama"
docker build -t uts-aggregator .

"menjalankan dua service sekaligus, yaitu aggregator dan publisher, menggunakan Docker Compose"
docker compose up --build

"
http://localhost:8080/docs

"mengirim event secara manual lewat Swagger"
{
  "topic": "demo-topic-2",
  "event_id": "evt_demo_002",
  "timestamp": "2025-10-25T09:30:00Z",
  "source": "manual-test",
  "payload": { "message": "Testing topic change!" }
}
