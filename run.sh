#!/bin/bash
docker-compose down -v
docker-compose pull
docker-compose up -d
docker-compose logs -f