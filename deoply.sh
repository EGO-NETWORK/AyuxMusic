docker container rm AyuXop -f > /dev/null
sleep 2
echo "Starting and Deploying Bot as AyuXop"
docker run -d --restart=always --name AyuXop AyuXop
