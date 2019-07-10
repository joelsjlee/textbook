# Text Book

[![N|Solid](https://avatars3.githubusercontent.com/u/20544498?s=200&v=4)](https://github.com/upenndigitalscholarship/)

This tool allows you to analyze news articles within the context of a book, using Jekyll, Django, Docker, and Voyant Tools.

### Installation

Clone the repo into your local folder:

```
git clone https://github.com/joelslee/textbook
```

This project was built through Docker, and there are some additional configuration settings that must be set by the user.

First, `cd` and `nano` into `textbook/compose/traefik/traefik.toml` and change the `main` url under `[[acme.domains]]` to your desired url. Under `[frontends]`, change the rules under `[frontends.voyant.routes.dr1], [frontends.nginx.routes.corpora], [frontends.django.routes.dr1]` to your desired urls.

Second, `cd` and `nano` into `textbook/voyant_gen/voyant_gen.py` and on line 56 change the `url_template` to your desired url.

Now, run:

```
sudo docker-compose build
```
And when that finishes building, run

```
sudo docker-compose up
```

### Running and Additional Configuration


After running the docker-compose up command, you should be able to go to your desired url and will see the django user login page.

If the login page gives a 500 error, open up a new terminal and put in the command:

```
sudo docker-compose run --rm django python manage.py migrate
```

And then refresh the page. From here, you should be able to sign up, and then sign in. Once signing in successfully, the home page should show the texts. If this is a new project, then there should be no text links to click. 

The project input is a .txt file for the full text of the book, a .txt file containing all the keywords, and a directory containing all the .txt articles.

* Make sure that the title of the book .txt should be separated by underscores. For example, "The Jungle" by Upton Sinclair should be saved as `"the_jungle.txt"`.
    * Put this file in the `input/texts/` directory. This directory can support multiple book.txt files!

* The keywords should be a .txt file that has each keyword separated by a line break, and should be named `keywords.txt`.

    * Put this file in the `input/keywords/` folder
* The articles should all be .txt files and should be in `input/articles`

Once you have inputted these files, then you should be able to refresh the server after waiting a few minutes, and you should see the text appear on the homepage. Clicking on that link will bring you to the Jekyll page of the full text, with your keywords highlighted and linked to the Voyant server, which analyzes your corpus of articles.












