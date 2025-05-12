import markdown2
import random
from django.shortcuts import render, redirect

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)

    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })

    html_content = markdown2.markdown(content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })


def search(request):
    query = request.GET.get("q")
    entries = util.list_entries()

    if query is None:
        return redirect("index")

    for entry in entries:
        if entry.lower() == query.lower():
            return redirect('entry', title=entry)

    results = [entry for entry in entries if query.lower() in entry.lower()]

    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })


def newpage(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        entries = util.list_entries()
        if title.lower() in (entry.lower() for entry in entries):
            return render(request, "encyclopedia/error.html", {
                "message": "An entry with this title already exists."
            })

        util.save_entry(title, content)

        return redirect("entry", title=title)
    else:
        return render(request, "encyclopedia/newpage.html")


def editpage(request, title):
    if request.method == "POST":
        new_content = request.POST.get("content")

        util.save_entry(title, new_content)

        return redirect("entry", title=title)

    else:
        content = util.get_entry(title)

        if content is None:
            return render(request, "encyclopedia/error.html", {
                "message": "Entry not found."
            })

        return render(request, "encyclopedia/editpage.html", {
            "title": title,
            "content": content
        })


def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect("entry", title=random_entry)
