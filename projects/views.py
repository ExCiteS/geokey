from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.decorators import handle_exceptions

from .models import Project
from .serializers import ProjectUpdateSerializer


class ProjectAdminDetail(TemplateView):
    model = Project
    template_name = 'projects/project_view.html'


class ProjectApiDetail(APIView):
    @handle_exceptions
    def put(self, request, project_id, format=None):
        project = Project.objects.as_admin(request.user, project_id)
        serializer = ProjectUpdateSerializer(project, data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions
    def delete(self, request, project_id, format=None):
        project = Project.objects.as_admin(request.user, project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
