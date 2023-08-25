cd server
docker build -t server_app .
docker run -p 127.0.0.1:1900:1701 server_app
