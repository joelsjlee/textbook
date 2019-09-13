from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.template import Context, Template, loader
from titlecase import titlecase
from django.core.management import call_command
from django.views.decorators.cache import never_cache
import os.path
import zipfile


##############################################################
# VIEWS
##############################################################
# View for textbooks and other non-Django files
@never_cache
@login_required
def proxy(request, static_path):
    # Prevent unauthorized users from accessing other pages
    if not (request.user.is_staff or request.user.is_student):
        return redirect("/")
    template_path = 'proxy/' + static_path
    if not os.path.isfile('proxy/templates/' + template_path):
        raise Http404("no static site matches the given query.")
    # Handle paths to textbooks
    if template_path.endswith(".html"):
        template = get_template(template_path)
        context = Context()
        try:
            return HttpResponse(template.render(context))
        except ValueError:
            call_command('collectstatic', verbosity=0, interactive=False)
            return HttpResponse(template.render(context))
    else:
        return render(request, template_path)


# View for home page
def home(request):
    template_name = "pages/home.html"
    text_info_list = get_text_info_list("../app/proxy/templates/proxy/texts")
    return render(request, template_name, {"text_info_list": text_info_list})


# View for file upload
@login_required
def file_upload(request):
    # prevent non-staff from accessing upload page
    if not request.user.is_staff:
        return redirect("/")
    if request.method == "POST":
        textbooks = request.FILES.getlist("textbook_file")
        article_zips = request.FILES.getlist("article_file")
        keywords = request.POST.getlist("keyword")
        # Process files if it is all error free
        if not error_check_files(request, textbooks, article_zips, keywords):
            process_files(request, textbooks, article_zips, keywords)
    return render(request, "pages/file_upload.html")


##############################################################
# HELPER FUNCTIONS FOR TEXTBOOK VIEW
##############################################################
# Generate template for Django context
def get_template(template_path):
    html_page = loader.render_to_string(template_path)
    head, body = get_head_body(html_page)
    head = edit_header_styling(head)
    html_page = head + body
    return Template(html_page)


# Get head and body of string HTML page
def get_head_body(html_page):
    head_ending_index = html_page.find("</head>")
    head = html_page[:head_ending_index]
    body = html_page[head_ending_index:]
    return head, body


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


##############################################################
# HELPER FUNCTIONS FOR HOME VIEW
##############################################################
# Get the textbook info for display
def get_text_info_list(textbook_dir):
    text_info_list = []
    if os.path.isdir(textbook_dir):
        for text_filename in os.listdir(textbook_dir):
            text_info = []  # holds [{raw file name}, {formatted file name}]
            text_info.append(text_filename)
            text_info.append(format_text_name(text_filename))
            text_info_list.append(text_info)
    return text_info_list


# Format the text filename
def format_text_name(text_filename):
    text_filename = text_filename.replace("_", " ")
    text_filename = text_filename.replace("-", " ")
    return titlecase(text_filename)


##############################################################
# HELPER FUNCTIONS FOR FILE UPLOAD VIEW
##############################################################
# Check files for errors, returns True if they are any
def error_check_files(request, textbooks, article_zips, keywords):
    # Check for blank form
    if (not textbooks) and (not article_zips) and (not keywords[0]):
        messages.error(request, "At least one file must be uploaded")
        return True
    # Check for errors in textbook files
    err = err_check_textbooks(textbooks)
    if err:
        messages.error(request, err)
        messages.info(request, "Only textbooks of .txt type are accepted")
        return True
    # Check for errors in articles
    err = err_check_articles(article_zips)
    if err:
        messages.error(request, err)
        messages.info(request, "Article zipfile must contain only articles of type .txt")
        return True
    return False


# Cheack for faulty textbook files
def err_check_textbooks(textbooks):
    err = ""
    for textbook in textbooks:
        if not textbook.name.endswith(".txt"):
            err += textbook.name + ", "
    if err:
        err = err[:-2]
        err = "Failed to upload files, the following textbooks have incorrect file types: " + err
    return err


# Check for fault article zip file and faulty contents
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
        err = "Failed to upload files, the following articles have incorrect file types: " + err
    return err


def process_files(request, textbooks, article_zips, keywords):
    # process textbooks
    success = process_textbooks(textbooks)
    if success:
        messages.success(request, success)
    # process articles
    success = process_articles(article_zips)
    if success:
        messages.success(request, success)
    # handle keywords
    keywords_processed = process_keywords(keywords)
    if keywords_processed:
        messages.success(request, "Keywords Uploaded: " + keywords_processed)
    messages.info(request, "Please wait 5 seconds for files to be processed")
    return


# Save each textbook file
def process_textbooks(textbooks):
    success = ""
    textbook_dir = FileSystemStorage(location="/app/proxy/media/texts")
    for textbook in textbooks:
        success += textbook.name + ", "
        textbook_dir.delete(textbook.name)
        textbook_dir.save(textbook.name, textbook)
    if success:
        success = success[:-2]
        success = "Successfully uploaded textbooks: " + success
    return success


# Save each article in zip file
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
    if success:
        success = "Successfully uploaded article zipfile: " + success
    return success


# Get all keywords and put them in keywords.txt files and save it
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


# Check if keywords list is empty
def keywords_is_empty(keywords):
    is_empty = True
    for keyword in keywords:
        if len(keyword) > 0:
            is_empty = False
    return is_empty
