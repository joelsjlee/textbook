# Text Book

[![N|Solid](https://avatars3.githubusercontent.com/u/20544498?s=200&v=4)](https://github.com/upenndigitalscholarship/)

This tool allows you to analyze news articles within the context of a book, using Jekyll, Django, Docker, and Voyant Tools.

### Installation

Clone the repo into your local folder:

```
git clone https://github.com/joelslee/textbook
```
This project was built through Docker, and there are some additional configuration settings that must be set by the user. This can be done using the `envs_generator.py` script in the root directory. Run the command with your domain name:

```
python envs_generator YOUR_DOMAIN_NAME
```

Note that for this project and how it was built, the url generated will add "-voyant" to the end of the domain name inputted. For example inputting `jl.pennds.org` would give me another domain name which is already available and running, `jl-voyant.pennds.org`. This is currently our way of configuring the voyant part of the tool.

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

All of the inputs should be put into a folder at the root directory called `input`, in their respective folders, `articles, keywords` and `texts`.

* Make sure that the title of the book .txt should be separated by underscores. For example, "The Jungle" by Upton Sinclair should be saved as `"the_jungle.txt"`.
    * Put this file in the `input/texts/` directory. This directory can support multiple book.txt files!

* The keywords should be a .txt file that has each keyword separated by a line break, and should be named `keywords.txt`.

    * Put this file in the `input/keywords/` folder
* The articles should all be .txt files and should be in `input/articles`

Once you have inputted these files, then you should be able to refresh the server after waiting a few minutes, and you should see the text appear on the homepage. Clicking on that link will bring you to the Jekyll page of the full text, with your keywords highlighted and linked to the Voyant server, which analyzes your corpus of articles.

### Other Things and Local Deployment

For local deployment, you will need to change the python script `voyant_gen/voyant_gen.py` on line 56 and change it to say

```
url_template = 192.168.99.100:4000/?input=http://192.168.99.100:4000/corpora/{}
```

Now run the build command using the `local.yml`

```
sudo docker-compose -f local.yml build
```

and then the up command:

```
sudo docker-compose -f local.yml up
```

Now the server should run locally and be accessible first through http://192.168.99.100:3000 to access the django authentication page, and the voyant
server should be running on http://192.168.99.100:4000.
