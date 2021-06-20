#!/usr/bin/env bash
docker run -d \
  --name=nextcloud \
  -e PUID=1000 \
  -e PGID=1001 \
  -e TZ=Europe/London \
  -p 443:443 \
  -v nextcloud-config:/config \
  -v nextcloud-data:/data \
  --restart unless-stopped \
  ghcr.io/linuxserver/nextcloud
