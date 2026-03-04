# scratch-gui

## Modified version of scratch-gui

This is a modified version of the [scratch-gui repository](https://github.com/scratchfoundation/scratch-gui) that allowes to host scratch projects on an other server than the official scratch project server https://projects.scratch.mit.edu. It also implements the possibility to implement the fullscreen mode by default by setting the `fullscreen=true` option in the project url.

## Hosting this project on your server

In the root directory of this repository create an `settings.json` file with the following content:

```
{
    "project_host": "https://your.server.example.com/projects",
    "asset_host": "https://your.server.example.com/assets"
}
```

In your server create a folder `/var/www/scratch-data/assets` that contains all assets of the scratch projects (png files, svg files, ...).
Create a second folder `/var/www/scratch-data/projects` on the server that contains all the scratch json files named like numbers.

On your local machine go back in the root directory of this repository and execute `npm run build`.
Copy the content of the `build` directory of this repository into a folder `/var/www/scratch` that you create on the server.

If you are using nginx use the following config:

```
server{
        listen 443 ssl;
        listen [::]:443 ssl;

        server_name your.server.example.com;
        ssl_certificate /etc/letsencrypt/live/your.server.example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/your.server.example.com/privkey.pem;

        location / {
            root /var/www/scratch/;
        }

        location /assets/ {
            root /var/www/scratch-data/;
        }

        location /projects/ {
            root /var/www/scratch-data/;
        }
}
```

The scratch project 1 can now be accessed by calling `https://your.server.example.com/#1`.
It can be opened in fullscreen mode by calling `https://your.server.example.com/#1?fullscreen=true`

## Testing the project locally

To test the project locally enter the followin in the `settings.json` file:

```
{
    "project_host": "http://localhost:8123/projects",
    "asset_host": "http://localhost:8123/assets",
    "serve_build_port": 8123
}
```

Go to the root of this directory and place all the projects in the `data/projects` folder and all the assets in the `data/assets`folder.

Build the project with `npm run build`.

Start the server with `python serve_build.py`.

In the browser open `http://localhost:8123`.
The scratch project 1 can now be accessed by calling `http://localhost:8123/#1`.
It can be opened in fullscreen mode by calling `http://localhost:8123/#1?fullscreen=true`
