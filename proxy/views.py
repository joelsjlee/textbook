from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.template import Context, Template, loader
from titlecase import titlecase
from django.core.management import call_command
import os.path
import zipfile

# Create your views here.
@login_required
def proxy(request, static_path):
    if not (request.user.is_staff or request.user.is_student):
        return redirect("/")
    # print('static path: ' + static_path)
    template_path = 'proxy/' + static_path
    # print('template_path: ' + template_path)
    # print(os.listdir('proxy/templates/proxy'))
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
    if not request.user.is_staff:
        return redirect("/")
    if request.method == "POST":
        ok_to_process = True
        textbooks = request.FILES.getlist("textbook_file")
        article_zips = request.FILES.getlist("article_file")
        keywords = request.POST.getlist("keyword")
        # check if form has at least one file or keyword
        if (not textbooks) and (not article_zips) and (not keywords[0]):
            messages.error(request, "At least one file must be uploaded")
            ok_to_process = False
        # check for faulty textbook files
        err = err_check_textbooks(textbooks)
        if err:
            err = "Failed to upload files, the following textbooks have incorrect file types: " + err
            messages.error(request, err)
            messages.info(request, "Only textbooks of .txt type are accepted")
            ok_to_process = False
        # check for faulty article zip file and article files
        err = err_check_articles(article_zips)
        if err:
            err = "Faile to upload files, the following articles have incorrect file types: " + err
            messages.error(request, err)
            messages.info(request, "Article zipfile must contain only articles of type .txt")
            ok_to_process = False
        # process everything is it is all ok
        if (ok_to_process):
            # process textbooks
            success = process_textbooks(textbooks)
            if success:
                success = "Successfully uploaded textbooks: " + success
                messages.success(request, success)
            # process articles
            success = process_articles(article_zips)
            if success:
                success = "Successfully uploaded article zipfile: " + success
                messages.success(request, success)
            # handle keywords
            keywords_processed = process_keywords(keywords)
            if keywords_processed:
                messages.success(request, "Keywords Uploaded: " + keywords_processed)
            messages.info(request, "Please wait 30 seconds for files to be processed")
    return render(request, "pages/file_upload.html")


# cheack for faulty textbook files
def err_check_textbooks(textbooks):
    err = ""
    for textbook in textbooks:
        if not textbook.name.endswith(".txt"):
            err += textbook.name + ", "
    if err:
        err = err[:-2]
    return err


# check for fault article zip file and faulty contents
def err_check_articles(article_zips):
    err = ""
    if article_zips:
        article_zip = article_zips[0]
        if not article_zip.name.endswith(".zip"):
            err += article_zip.name + ", "
        else:
            article_name_list = zipfile.ZipFile(article_zip).namelist()
            for article_name in article_name_list:
                if (not article_name.endswith(".txt")) or (article_name.count("/") > 1):
                    err += article_name + ", "
    if err:
        err = err[:-2]
    return err


# save each textbook file
def process_textbooks(textbooks):
    success = ""
    textbook_dir = FileSystemStorage(location="/app/proxy/media/texts")
    for textbook in textbooks:
        success += textbook.name + ", "
        textbook_dir.delete(textbook.name)
        textbook_dir.save(textbook.name, textbook)
    if success:
        success = success[:-2]
    return success


# save each article in zip file
def process_articles(articles):
    success = ""
    article_dir = FileSystemStorage(location="/app/proxy/media/articles")
    if articles:
        article_zipfile = zipfile.ZipFile(articles[0])
        article_name_list = article_zipfile.namelist()
        for article_name in article_name_list:
            article_file = article_zipfile.open(article_name)
            name_parts = article_name.split("/")
            new_name = name_parts[len(name_parts) - 1]
            article_dir.delete(new_name)
            article_dir.save(new_name, article_file)
        success += articles[0].name
    return success


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
            keyword = keyword.strip()
            keywords_processed += keyword + ", "
            keyword += "\n"
            keywords_file.write(keyword)
        keywords_file.close()
        keywords_processed = keywords_processed[0:len(keywords_processed) - 2]
    if keywords_processed:
        keywords_processed = keywords_processed[:-2]
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
