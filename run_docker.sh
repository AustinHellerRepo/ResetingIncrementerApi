docker network inspect traefik_router_network >/dev/null 2>&1 || \
  docker network create --driver bridge traefik_router_network
docker-compose up -d
