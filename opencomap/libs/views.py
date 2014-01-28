import json
from django.http import HttpResponse

def render_to_json(key, response, status_code=200):
	return HttpResponse('{"' + key + '": ' + response + '}', status=status_code, content_type="application/json")

def render_to_success(response):
	return render_to_json("success", json.dumps(response))

def render_to_error(status_code, error):
	return render_to_json("error", json.dumps(error.message), status_code=status_code)