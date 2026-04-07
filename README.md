Красильникова К0609-23

собрать и запушить образ

docker build -t nikanikanika/flask-nginx:latest .
docker push nikanikanika/flask-nginx:latest

задеплоить 
cd ansible
ansible-playbook -i inventory.ini playbook_kubectl_fixed.yml

проверка
curl http://192.168.122.34:30080/api/health