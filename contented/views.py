from django.shortcuts import render


def home_page(request):
    my_projects = ["my_test_project", "my_other_project"]
    return render(request, "home.html", {"project_ids": my_projects})


def project_page(request):
    return render(request, "project.html")
