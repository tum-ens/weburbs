from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def upload(request, project_name):
    if 'file' not in request.FILES:
        return HttpResponse('File is missing', status=400)

    uploaded_file = request.FILES['file']
    with open(f'uploads/{uploaded_file.name}', 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    return HttpResponse('fine')