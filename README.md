This is a simple file sending and receiving service with FastAPI and Nginx. The NGINX is a reverse proxy for the FastAPI service. 

# Set up NGINX Config
1. Get nginx

2. Assuming the nginx etc directory is /etc/nginx; cd into /etc/nginx, check if nginx.conf has the line "include sites-enabled/*". If not, add it.

3. Create the file sites-available/fastapi

4. Copy the contents from fileservice into sites-available/fastapi

5. Run this command
```ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/``` and run ```nginx -t``` to make sure the conf file is fine.

6. Create the ssl certificates
```
cd /etc/nginx
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/selfsigned.key \
    -out /etc/nginx/ssl/selfsigned.crt
```

# Set up FastAPI service

Assuming the files are installed in $DIR
1. Create a pip environment ```python3 -m venv .env```

2. Activate the environment ```source .env/bin/activate```

3. Install the requirements ```pip install requirements.txt```

# Start the service
## Easy service start

1. In a terminal, in the installed directory with the python environment, run ```uvicorn app:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 120```

2. Start the nginx service

Now, test by running ```curl -k https://localhost``` and you should get the return message ```{"message":"Hello World"}```

## Service start in NGINX conf (Not as recommended as the other methods)

In ```/etc/nginx/sites-available/fastapi```, change
```
location / {
    proxy_pass http://127.0.0.1:8000;  # Forward requests to Uvicorn
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
to
```
location /fastapi/ {
    proxy_pass http://127.0.0.1:8000;

    # Ensure Uvicorn is started when NGINX starts
    init_by_lua_block {
        os.execute("nohup /path/to/python/env/bin/uvicorn main:app --host 127.0.0.1 --port 8000 &")
    }
}
```
You may need to install ```ngx_http_lua_module``` for your nginx. 

## Complicated service start
Warning, I couldn't test this because I created on a mac and I have no idea how the service files work on mac. We will make the fastAPI service an actual service on the machine.

1. Make the ```/etc/systemd/system/fastapi.service``` and add the contents:
```
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=your_user_name
WorkingDirectory=/path/to/your/fastapi/app
ExecStart=/path/to/your/python/env/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```
Replace ```your_user_name```, ```/path/to/your/fastapi/app```, and ```/path/to/your/python/env/bin/uvicorn``` with the appropriate values.

2. Run the service, should be called ```fastapi```. You may need to restart your systemd with ```sudo systemctl daemon-reload```
