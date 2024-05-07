role=$1
v=$2

docker build --build-arg role=$role -t ciaa/$role:$v .
docker push ciaa/$role:$v