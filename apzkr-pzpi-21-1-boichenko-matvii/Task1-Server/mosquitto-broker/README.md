# Ready to use Eclipse-mosquitto MQTT broker in container


## Instructions

* Install Docker and docker-compose, instructions [here](https://docs.docker.com/engine/install/)
* (Optional) Set desired configuration in *config/mosquitto.conf file*. More info [HERE](https://mosquitto.org/man/mosquitto-conf-5.html)
* (Optional) Create user/password for connection. Default are *admin/qwerty12345* 
* In terminal/command line go to directory *mosquitto-broker*
* Run container
    ```bash
    # Run the docker container for mqtt
    docker-compose -p mosquitto-broker up -d
    ```
* Check if the container is up and working (note down container-id)
    ```bash
    docker ps
    ```


## Create a user/password in the pwfile

```bash

# login interactively into the mqtt container
docker exec -it <container-id> sh

# add user and it will prompt for password
mosquitto_passwd -c /mosquitto/config/pwfile user1

# delete user command format
mosquitto_passwd -D /mosquitto/config/pwfile <user-name-to-delete>

# type 'exit' to exit out of docker container prompt

```
Then restart the container 
```bash
sudo docker restart <container-id>
```


## Testing with a nice MQTT Web Client
Read more about it here => https://mqttx.app/  

```bash
sudo docker run -d --name mqttx-web -p 80:80 emqx/mqttx-web
```


## Source/Reference for Mosquitto
Github => https://github.com/eclipse/mosquitto
