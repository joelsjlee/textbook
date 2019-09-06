# text/book

[![N|Solid](https://avatars3.githubusercontent.com/u/20544498?s=200&v=4)](https://github.com/upenndigitalscholarship/)

This tool allows you to analyze a companion corpus within the context of a specific document, using Jekyll, Django, Docker, and Voyant Tools.

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

Next, create a non-root user named `textbook`. The best way to do this will depend on your server configuration, but instructions for Ubuntu 18.04 can be found [here](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04#step-2-%E2%80%94-creating-a-new-user). 

Once you've created the `textbook` user, you'll need to grant it permission to three folders with the following command:

```
chown -R textbook ed input static_pages
```

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


#### About the project

text/book was created by the Penn Libraries Digital Scholarship team, in collaboration with the Price Lab for Digital Humanities. It was created as part of a project concieved by Sibel Sayılı-Hurley and Claudia Lynn to create an online teaching edition of Thomas Brussig's *Am kürzeren Ende der Sonnenallee* overlaying personal and public accounts of events in East Germany during the period of 1945-1990. The resulting edition will move between fictional, non-fictional, public, and private perspectives to convey a rich and multi-layered understanding of life in the GDR. 

As we considered existing tools that might help in the construction of this edition, we realized we could build a more general-purpose platform for teaching editions interlinked with textual corpora and visualization tools. text/book is our first attempt at creating such a platform.

To create text/book we relied on the work of many other scholars and software developers. To render an attractive, minimal edition of a given text, we use [Jekyll](https://jekyllrb.com/) and [Ed](https://github.com/minicomp/ed). To visualize text corpora, we use [Voyant Server](https://github.com/sgsinclair/VoyantServer). To manage acess control and offer a basic web UI, we use [Django](https://www.djangoproject.com/), with tooling from [Cookiecutter Django](https://github.com/pydanny/cookiecutter-django). And to glue the parts together, we use [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/).

New code for this project was written by [Scott Enderle](https://github.com/senderle), [Joel Lee](https://github.com/joelslee), [Vicente Guallpa](https://github.com/Vicenteguallpa), and [Siyu Zheng](https://github.com/senderle/text_jekyll/graphs/contributors).
 
