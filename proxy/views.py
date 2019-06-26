from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import Context, Template, loader
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import os.path
from django.http import Http404

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
            return HttpResponse(template.render(context))
        else:
            return render(request, template_path)
    else:
        raise Http404("no static site matches the given query.")


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
