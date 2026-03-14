from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Project
from .serializers import ProjectSerializer
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiExample
from drf_spectacular.types import OpenApiTypes

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer.CreateProject,
    permission_classes = [AllowAny]

    @extend_schema(
        request=ProjectSerializer.CreateProject,
        responses={201: ProjectSerializer.ProjectList},
    )    
    def create(self, request):
        serializer = ProjectSerializer.CreateProject(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save(creator=request.user)
        return Response(ProjectSerializer.ProjectList(project).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description='Title of the project',
                required=True,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample(
                        'Example 1',
                        value="Project Little-Fishes",
                        summary="A project about why little fishes seem to have shorter life spans, and how that impacts nutrient cycles in the ocean."
                    ),
                ],
            ),
        ],
    )
    def detail(self):
        serializer = ProjectSerializer.ProjectDetail
        serializer.is_valid()
        serializer.save()
        return Response(ProjectSerializer.ProjectDetail, status=status.HTTP_200_OK)
        
