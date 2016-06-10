# docker-dyndock
Docker base on djdnbs and add a dyndns api to quickly add new domain.
It track all docker event and add/delete dns entry for each
Start docker run -it --name dns -v /var/run/docker.sock:/docker.sock dyndns

You can change the default API user and password by override the API_USER and API_PWD env
You can create you own dns cache or delegate with your isp cache (or google dns) with the FORWARD env
docker run -it --name dns -v /var/run/docker.sock:/docker.sock -e API_PWD=Mypasswd -e FORWARD=8.8.8.8 dyndns
