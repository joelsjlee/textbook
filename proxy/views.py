from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import Context, Template, loader
from titlecase import titlecase
from django.core.management import call_command
import os.path

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
    if request.method == 'POST':
        files_dict = request.FILES
        files_keys = files_dict.keys()
        # its fine if there are no keywords (for now at least)
        if ("textbook_file" not in files_keys) and ("article_file" not in files_keys):
            messages.add_message(request, messages.ERROR, "At least one file must be uploaded")
        else:
            success_msg, fail_msg = process_files("", "", files_dict.getlist("textbook_file"),
                                                  FileSystemStorage(location="/app/proxy/media/texts"))
            success_msg, fail_msg = process_files(success_msg, fail_msg,
                                                  files_dict.getlist("article_file"),
                                                  FileSystemStorage(location="/app/proxy/media/articles"))
            if success_msg:
                success_msg = "The following files were succesfully uploaded: " + success_msg
                messages.success(request, success_msg)
                info_msg = "Please wait 30 seconds for your files to be processed"
                messages.info(request, info_msg)
            if fail_msg:
                fail_msg = "The following files failed to upload:\n" + fail_msg
                fail_msg_2 = "Please check for the correct file format"
                messages.error(request, fail_msg)
                messages.error(request, fail_msg_2)
            process_keywords(request.POST.getlist("keyword"))
    return render(request, 'pages/file_upload.html')


# save .txt files and update the messages accordingly
def process_files(success_msg, fail_msg, files, save_directory):
    for file in files:
        file_name = file.name
        if file_name.endswith(".txt"):
            success_msg += file_name + "  "
            save_directory.delete(file_name)
            save_directory.save(file_name, file)
        else:
            fail_msg += file_name + "  "
    return success_msg, fail_msg


# get all keywords and put them in keywords.txt files and save it
def process_keywords(keywords):
    if keywords:
        keywords_file = open(os.path.join("/app/proxy/media/keywords", "keywords.txt"), "w+")
        for keyword in keywords:
            keyword = keyword.strip() + "\n"
            keywords_file.write(keyword)
        keywords_file.close()


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
