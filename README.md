# Static Site Proxy

[![N|Solid](https://avatars3.githubusercontent.com/u/20544498?s=200&v=4)](https://github.com/upenndigitalscholarship/)

Static Site Proxy allows you to have a Django user authentication wall around your static site!

### Installation

You must have Docker, Python and Django installed for this to run. Clone this github repo, and add your static html files into the folder named `static_pages`.

Now open a terminal or Git Bash and run

```
docker-compose -f local.yml build
```

This should build the stack and it will take awhile to complete. After completion, run this next command to put up the server:

```
docker-compose -f local.yml up
```

If you have an older version of Windows and user Docker Toolbox, your site will be viewable at [http://192.168.99.100:3000](http://192.168.99.100:3000). If you're running the newest version of Docker, it might be up at [http://localhost:3000](http://localhost:3000).

Now, if you add the file name of your desired html webpage that you added into `static pages`, into the browser, like for exmaple http://192.168.99.100:3000/index.html you will be faced with a login page.

To create a superuser to login to the page, open up the terminal and cd into the `static_site_proxy` directory and type in

```
docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

If you are running on windows and get an error saying:

```
Superuser creation skipped due to not running in a TTY. You can run manage.py createsuperuser in your project to create one manually.
```

you can fix this by adding `winpty` to the front of the command, giving:

```
winpty docker-compose -f local.yml run --rm django python manage.py createsuperuser
```

This will prompt you to create a username, email, and password. After you do this, go to [http://192.168.99.100:3000/admin](http://192.168.99.100:3000/admin) and login. Now click on `Email Addresses` and click on the email address you provided and check off `verified` and `primary`. Hit save and now navigate back to the webpage you previously tried to see. You should be given the same login page, and you can now login with those credentials and you should be redirected to your webpage.
