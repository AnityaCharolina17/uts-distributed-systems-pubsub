"membangun Docker image untuk service aggregator menggunakan Dockerfile utama"
docker build -t uts-aggregator .

"menjalankan dua service sekaligus, yaitu aggregator dan publisher, menggunakan Docker Compose"
docker compose up --build

"
http://localhost:8080/docs

"mengirim event secara manual lewat Swagger"
{
  "topic": "demo-topic",
  "event_id": "evt_demo_001",
  "timestamp": "2025-10-24T10:00:00Z",
  "source": "manual-test",
  "payload": { "message": "Hello from demo!" }
}
