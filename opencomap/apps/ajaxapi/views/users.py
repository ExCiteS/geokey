import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.contrib.auth.models import User

from opencomap.libs.views import render_to_json
from opencomap.libs.serializers import ObjectSerializer


@login_required
@require_http_methods(["GET"])
def query_users(request):
    if request.GET and request.GET['query']:
        q = request.GET['query']
        users = User.objects.filter(Q(username__contains=q) | Q(last_name__contains=q) | Q(first_name__contains=q))[:10]
        return render_to_json("users", ObjectSerializer().serialize(users))
    else:
        return render_to_json(
            "error",
            json.dumps("Please provide an entry for query parameter."),
            status_code=400
        )
