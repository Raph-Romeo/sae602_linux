docker build -t django_sae ./docker_images/django
docker build -t get ./docker_images/get
docker build -t insert ./docker_images/insert
docker-compose -f ./docker_compose/docker-compose.yml up --build
