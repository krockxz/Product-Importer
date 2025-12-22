from django.http import HttpResponse


def health(request):
    """
    Simple health check endpoint used by Render and root path (/).
    """
    return HttpResponse("ok")


