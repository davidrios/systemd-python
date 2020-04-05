# Run uwsgi in systemd

These instruction are meant to be used on Ubuntu 18.04. The default configurations assume you'll
serve the apps by socket with `nginx`.

We will configure uWSGI to run in emperor mode.

Install dependencies:

    # apt install uwsgi

You will also need to install `uwsgi-plugin-python` for Python 2 and `uwsgi-plugin-python3` for
Python 3 apps.

Stop and mask uWSGI's default service:

    # systemctl stop uwsgi
    # systemctl mask uwsgi

Copy files `emperor.ini` and `vassals-default.ini` to `/etc/uwsgi`.

You can edit `vassals-default.ini` if you want to add more settings that are common to all apps.
The provided values for keys `chmod-socket` and `chown-socket` assume nginx is running as user
`www-data`, which is the default on Ubuntu.

Copy file `vassals-create-dirs.py` to `/usr/local/bin` and set the executable flag.

Copy file `emperor.uwsgi.service` to `/etc/systemd/system`.

Enable and start the emperor service:

    # systemctl daemon-reload
    # systemctl enable emperor.uwsgi
    # systemctl start emperor.uwsgi

The emperor now should be running and ready to manage apps. You can check the log at
`/var/log/uwsgi/emperor.log`.

To run apps you'll put their uWSGI ini configuration in `/etc/uwsgi/apps-available`, as is standard
on Ubuntu. Please note that the ini file must have a configuration `vassal-name = %n` inside section
`[uwsgi]` and the file name must have the '.ini' extension.

Check the file `myapp.ini` for a sample app configuration.

The file name will define the app name that will be used to save logs/pids/etc. For example, if
you save the configuration as `/etc/uwsgi/apps-available/myapp.ini`, the app name will be `myapp`
and its files will be saved at:

- log: `/var/log/uwsgi/app/myapp.log`
- pid: `/run/uwsgi/app/myapp/pid`
- socket: `/run/uwsgi/app/myapp/socket`

To enable or disable an app, simply create on delete a symbolic link of the configuration on
`/etc/uwsgi/apps-enabled`, for example:

    # cd /etc/uwsgi/apps-enabled
    # ln -s ../apps-available/myapp.ini  # enable app
    # rm myapp.ini  # disable app

To restart the app, simply touch the configuration file:

    # touch /etc/uwsgi/apps-enabled/myapp.ini

That's all for uWSGI. The configuration for nginx would be something like:

    location @myapp {
        include uwsgi_params;
        uwsgi_pass unix:/var/run/uwsgi/app/myapp/socket;
    }

    location / {
        try_files $uri $uri/ @myapp;
    }
