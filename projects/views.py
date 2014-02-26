from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from core.decorators import handle_exceptions

from .models import Project
from .forms import ProjectCreateForm
from .serializers import ProjectUpdateSerializer


class ProjectAdminCreateView(LoginRequiredMixin, CreateView):
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def form_valid(self, form):
        data = form.cleaned_data
        project = Project.create(
            data.get('name'),
            data.get('description'),
            data.get('isprivate'),
            self.request.user
        )
        return redirect('admin:project_detail', project_id=project.id)


class ProjectAdminDetailView(TemplateView):
    model = Project
    template_name = 'projects/project_view.html'

    def get_context_data(self, project_id=None):
        user = self.request.user
        project = Project.objects.get(user, pk=project_id)
        return {
            'project': project,
            'admin': project.is_admin(user)
        }


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
