

#Download
````
$ docker pull xt1800i/snapnews-main
````


# Deployment

### Step 1: install docker
Please refer to  [this link](https://www.linode.com/docs/applications/containers/install-docker-ce-ubuntu-1804/)


### Step 2: pull docker image
````
$ docker pull xt1800i/snapnews-main
````
### Step 3: run docker container
*make sure docker volume is mounted*
````
$ docker run -itd -v /media/storage/images:/media/storage/images --restart=always  xt1800i/snapnews-main
````

### Step 4: modify system setting (optional)
*get into docker container bash (optional)*
````
$ docker run -it <your docker container name> bash
````
*modify /app/config.json*
````
{
    "host": "your database host",
    "database": "your database name",
    "username": "your database username",
    "password": "your database password",
    "port": "your database port",
    "text_recognition_api_url": "your text recognition system api url",
    "text_localization_api_url": "your text localization system api url"
}
````



