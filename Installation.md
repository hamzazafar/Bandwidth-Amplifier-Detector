## Configuring Master Node 
### DB setup:
#### Install MySQL server:
```sudo apt-get install mysql-server```

#### Run the security script:

```mysql_secure_installation```

#### Login using the root user:

```mysql -u root -p```

#### Create the database named as SCAN:

```create database SCAN default CHARACTER set utf8 default COLLATE utf8_general_ci;```

#### Create sql users and give permissions:
1. User for master node:
```
CREATE USER 'scanner'@'localhost' IDENTIFIED BY <password>; 
GRANT ALL PRIVILEGES ON SCAN.* TO 'scanner'@'localhost';
```

2. User for scanner node:
```
CREATE USER 'scanner'@'<scanner-node-ip>' IDENTIFIED BY <password>;
GRANT ALL PRIVILEGES ON SCAN.* TO 'scanner'@'<scanner-node-ip>';
```
        
3. User for Grafana:
```CREATE USER 'grafana'@'%' IDENTIFIED BY <password>;
GRANT SELECT,EXECUTE ON SCAN.* TO 'grafana'@'%';
```

4. Don't forget this step:
```
FLUSH PRIVILEGES;
exit;
```
Note: 
Make sure mysql server listen for connections from remote hosts. In my 
case I had to comment out the ```bind-address=127.0.0.1``` configuration 
in ```/etc/mysql/mariadb.conf.d/50-server.cnf```
      

### Install RabbitMQ messaging broker:

#### Enable RabbitMQ application repository:
```
echo 'deb http://www.rabbitmq.com/debian/ testing main' | sudo tee /etc/apt/sources.list.d/rabbitmq.list
```

#### Add the verification key for the package:
```
wget -O- https://www.rabbitmq.com/rabbitmq-release-signing-key.asc | sudo apt-key add -
```

#### Update the sources and install
```
sudo apt-get update
sudo apt-get install rabbitmq-server
```

#### Enable management console
```
sudo rabbitmq-plugins enable rabbitmq_management
```

#### Create admin user 
```
sudo rabbitmqctl add_user admin <password>
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

#### Management console is available at ```http://[your-IP-address]:15672/```

### Install Grafana
#### Add repo and install:
```
echo "deb https://packages.grafana.com/oss/deb stable main" >> /etc/apt/sources.list.d/grafana.list
sudo apt-get update
sudo apt-get install -y apt-transport-https
curl https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get install grafana
sudo service grafana-server start
```

#### Configure Grafana to start at boot time
```
sudo update-rc.d grafana-server defaults
```

### Clone code repository
```
git clone https://<path-to-framework-repo>.git
```

### Set configurations in ```framework/settings.py```

1. Set the database details in the DATABASES block e.g
```
      DATABASES = {
        'default': {                                                                
          'ENGINE': 'django.db.backends.mysql',                                   
          'PORT' : '3306',                                                        
          'NAME': 'SCAN',                                                         
          'USER': 'scanner',                                                      
          'PASSWORD': 'scanner',                                                  
          'HOST': '127.0.0.1',
        }                                                                           
      }
```
2. Set CELERY_BROKER_URL in settings.py
```
amqp://<amqp-user>:<amqp-password>@<master-node-ip>:5672//
```

3. To configure email notification, check out the confs starting with ```EMAIL_```
4. To use custom ZMap Installation, set the ```ZMAP_PATH``` configuration
5. To use IPv6 probes, set the ```IPV6_SRC_ADDR``` configuration
6. To set default packet rate, set the ```ZMAP_PACKET_PER_SECOND``` configuration

### Install Python dependencies and run server
#### Install virtual environment
```
python3 -m venv /root/ma-zafar/myenv
source /root/ma-zafar/myenv/bin/activate
```

#### Install MySQL config:
```
sudo apt-get install libmysqlclient-dev
```
If you are using mariadb:
```
sudo apt-get install libmariadbclient-dev
```

#### Install python3-dev
```
sudo apt-get install python3-dev
```

#### Install required packages:
```
pip install -r requirements.txt
```

#### Create database tables:
```
python manage.py migrate
```

#### Start the server
```
python manage.py runserver
```

#### Run the celery scheduler process:
Make sure you have activated the vitual environment
```
celery -A framework beat -l info -S django_celery_beat.schedulers.DatabaseScheduler
```

## Configuring Scanning Node

### Clone code repository
```
git clone https://<path-to-framework-repository>.git
```

### Install packages
```
python3 -m venv /root/ma-zafar/myenv
source /root/ma-zafar/myenv/bin/activate

sudo apt-get install libmysqlclient-dev
# if you are using mariadb:
sudo apt-get install libmariadbclient-dev

sudo apt-get install python3-dev
pip install -r requirements.txt
```

### Set configurations in settings.py
1. Set the DATABASES conf block:
2. Set the db name, user, password and HOST (Master Node's IP)
3. Change the CELERY_BROKER_URL to ```amqp://<amqp-user>:<amqp-password>@<master-node-ip>:5672//```
4. To configure email notification, check out the confs starting with ```EMAIL_```
5. To use custom ZMap Installation, set the ```ZMAP_PATH``` configuration
6. To use IPv6 probes, set the ```IPV6_SRC_ADDR``` configuration
7. To set default packet rate, set the ```ZMAP_PACKET_PER_SECOND``` configuration

NOTE: EMails are sent by the Scanning Node, so make sure correct EMail settings are in place.

### Run Worker Process
```
celery -A framework worker -l info 
```

## Grafana Settings
### Grafana web-ui
1. Open grafana web-ui in your browser: ```http://<master-node-ip>:3000```
2. Create a new MYSQL Datasource in Grafana using the grafana database user we have created earlier
3. Import the dashboards using the JSON files located under ```framework/granfana_dashboards```
  
