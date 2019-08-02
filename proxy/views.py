from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import Context, Template, loader
from titlecase import titlecase
from django.core.management import call_command
import os.path
import zipfile

# Create your views here.
@login_required
def proxy(request, static_path):
    print('static path: ' + static_path)
    template_path = 'proxy/' + static_path
    print('template_path: ' + template_path)
    print(os.listdir('proxy/templates/proxy'))
    if os.path.isfile('proxy/templates/' + template_path):
        if template_path.endswith(".html"):
            html_page = loader.render_to_string(template_path)
            header, body = get_header_body(html_page)
            header = edit_header_styling(header)
            html_page = header + body
            template = Template(html_page)
            context = Context()
            try:
                return HttpResponse(template.render(context))
            except ValueError:
                call_command('collectstatic', verbosity=0, interactive=False)
                return HttpResponse(template.render(context))
        else:
            return render(request, template_path)
    else:
        raise Http404("no static site matches the given query.")


# view for home
def home(request):
    path = "pages/home.html"
    return render(request, path, {'text_info_list': get_text_info_list()})


# view for upload
@login_required
def file_upload(request):
    if request.method == "POST":
        keywords = request.POST.getlist("keyword")
        if (not request.FILES.keys()) and (not keywords[0]):
            messages.error(request, "At least one file must be uploaded")
        else:
            # handle textbooks
            textbooks = request.FILES.getlist("textbook_file")
            success, err = process_textbooks(textbooks)
            if success:
                success = "Textbooks successfully uploaded: " + success
                messages.success(request, success)
            if err:
                fail = "Textbooks failed to upload: " + err
                messages.error(request, fail)
            # handle articles
            articles = request.FILES.getlist("article_file")
            success, err = process_articles(articles)
            if success:
                success = "Article zipfile successfully uploaded: " + success
                messages.success(request, success)
            if err:
                fail = "Article zipfile failed to upload: " + err
                messages.error(request, fail)
            # handle keywords
            keywords_processed = process_keywords(keywords)
            if keywords_processed:
                messages.success(request, "Keywords Uploaded: " + keywords_processed)
    return render(request, "pages/file_upload.html")


def process_textbooks(textbooks):
    success, err = "", ""
    textbook_dir = FileSystemStorage(location="/app/proxy/media/texts")
    for textbook in textbooks:
        if (textbook.name.endswith(".txt")):
            success += textbook.name + ", "
            textbook_dir.delete(textbook.name)
            textbook_dir.save(textbook.name, textbook)
        else:
            err += textbook.name + ", "
    if success:
        success = success[:-2]
    if err:
        err = err[:-2]
    return success, err


def process_articles(articles):
    success, err = "", ""
    article_dir = FileSystemStorage(location="/app/proxy/media/articles")
    if articles:
        article_zip = articles[0]
        if article_zip.name.endswith(".zip"):
            article_zipfile = zipfile.ZipFile(article_zip)
            name_list = article_zipfile.namelist()
            if is_valid_articles(name_list):
                for name in name_list:
                    file = article_zipfile.open(name)
                    name_parts = name.split("/")
                    new_name = name_parts[len(name_parts) - 1]
                    article_dir.delete(new_name)
                    article_dir.save(new_name, file)
                    success += article_zip.name
            else:
                err += article_zip.name
        else:
            err += article_zip.name
    if success:
        success = success[:-2]
    return success, err


# check if articles are valid
def is_valid_articles(name_list):
    for name in name_list:
        if (not name.endswith(".txt")) or (name.count("/") > 1):
            return False
    return True


# check if keywords list is empty
def keywords_is_empty(keywords):
    is_empty = True
    for keyword in keywords:
        if len(keyword) > 0:
            is_empty = False
    return is_empty


# get all keywords and put them in keywords.txt files and save it
def process_keywords(keywords):
    keywords_processed = ""
    if not keywords_is_empty(keywords):
        keywords_file = open(os.path.join("/app/proxy/media/keywords", "keywords.txt"), "w", encoding='utf-8')
        for keyword in keywords:
            keyword = keyword.strip() + "\n"
            keywords_file.write(keyword)
            keywords_processed += keyword + ", "
        keywords_file.close()
        keywords_processed = keywords_processed[0:len(keywords_processed) - 2]
    return keywords_processed


# Format the text file name
def format_text_name(text_name):
    text_name = text_name.replace("_", " ")
    text_name = text_name.replace("-", " ")
    return titlecase(text_name)


# Get the text information for display
def get_text_info_list():
    text_info_list = []
    try:
        text_dir_names = os.listdir("../app/proxy/templates/proxy/texts")
        for text_dir_name in text_dir_names:
            text_info = []  # holds [{raw file name}, {formatted file name}]
            text_info.append(text_dir_name)
            text_info.append(format_text_name(text_dir_name))
            text_info_list.append(text_info)
    except:
        pass
    return text_info_list


# Get header and body of string HTML page
def get_header_body(html_page):
    head_end_tag_index = html_page.find("</head>")
    head_section = html_page[:head_end_tag_index]
    body_section = html_page[head_end_tag_index:]
    return head_section, body_section


# Edit the styling of header
def edit_header_styling(header):
    new_header = ""
    lines = header.split("\n")
    for line in lines:
        if "<head>" in line:
            line += "\n  {% load static %}"
        if "<meta property=\"og:image\" content=\"/assets/open-graph-logo.png\"/>" in line:
            line = "    <meta property=\"og:image\" content=\"{% static \'open-graph-logo.png\' %}\"/>"
        if "<link rel=\"stylesheet\" href=\"/assets/css/style.css\"/>" in line:
            line = "  <link rel=\"stylesheet\" type=\"text/css\" href=\"{% static \'css/style.css\' %}\"/>"
        if "<link rel=\"apple-touch-icon-precomposed\" sizes=\"180x180\" href=\"/assets/apple-touch-icon-precomposed.png\"/>" in line:
            line = "  <link rel=\"apple-touch-icon-precomposed\" sizes=\"180x180\" href=\"{% static \'apple-touch-icon-precomposed.png\' %}\"/>"
        if "<link rel=\"shortcut icon\" href=\"/assets/favicon.ico\"/>" in line:
            line = "  <link rel=\"shortcut icon\" href=\"{% static \'favicon.ico\' %}\"/>"
        new_header += line + "\n"
    return new_header
