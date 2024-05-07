from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from .models import ProjectLog
from .serializers import ProjectLogSerializer

from users.permissions import (IsStartupRole)


@api_view(['GET'])
@permission_classes([IsStartupRole])
def view_logs(request, pk):
    '''
    Retrieve the logs for a specific project, ensuring the user has the correct role.

    This function retrieves the `ProjectLog` entries for a specified project, ensuring that the requesting 
    user has a startup role and that the project belongs to their startup. It returns a list of project logs 
    if the project is valid and accessible.

    Parameters:
        request (HttpRequest): The HTTP request object.
        pk (int): The ID of the project whose logs are to be retrieved.

    Returns:
        Response: An HTTP response containing the serialized list of project logs.

    Raises:
        Http404: If the project with the given ID does not exist.

    Error Handling:
        - If no logs are found for the specified project, the function returns an HTTP 400 status with an error message 
          indicating that the project does not belong to the startup or was not created.

    Notes:
        - The function requires that the user has the `IsStartupRole` permission.
        - If the logs are successfully retrieved, the function returns an HTTP 200 status with the serialized data.
    '''
    startup_id = request.user.user_info.company_id
    project_logs = ProjectLog.objects.filter(project_birth_id=pk, startup_id=startup_id)

    if not project_logs:
        return Response(
            {"error": "Project was not created or does not belong to you"},
            status=status.HTTP_400_BAD_REQUEST
            )
    serializer = ProjectLogSerializer(project_logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)