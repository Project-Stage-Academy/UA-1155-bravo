from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from .models import InvestorProject
from .serializers import InvestorProjectSerializer

from users.permissions import (IsInvestorRole, IsInvestorCompanySelected, IsStartupCompanySelected)

@api_view(['POST'])
@permission_classes([IsInvestorRole, IsInvestorCompanySelected])
def follow(request, project_id):
    """
    Shortlist a project for an investor with a share of zero.

    This function creates a new `InvestorProject` instance with a share of zero for a given investor and project. 
    It checks if the project is already shortlisted by the investor, and if so, returns an error response.

    Parameters:
        request (HttpRequest): The HTTP request containing the investor and project details.
        project_id (int): The ID of the project to be followed.

    Returns:
        Response: A response indicating whether the project was successfully shortlisted or an error occurred.

    Raises:
        serializers.ValidationError: If the project is already followed by the investor.

    Notes:
        - If the project is already followed, the function returns an HTTP 400 response with an error message.
        - If successful, it returns an HTTP 201 response with a message indicating that the project is shortlisted.
    """
    
    investor_id = request.user.user_info.company_id

    # Check if an InvestorProject with the given project_id and investor_id already exists
    if InvestorProject.objects.filter(project_id=project_id, investor_id=investor_id).exists():
        return Response({"error": "Project is already followed by this investor"},
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new InvestorProject with share=0
    investor_project = InvestorProject(
        project_id=project_id,
        investor_id=investor_id,
        share=0
    )
    investor_project.save()

    return Response({"message": "Project shortlisted with zero share"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsInvestorRole, IsInvestorCompanySelected])
def subscription(request, project_id, share):
    """
    Subscribe an investor to a project with a given share.
    If a record already exists, update the share value.

    This function either creates a new `InvestorProject` instance or updates the share value 
    if the investor is already subscribed to the project. It validates that the share is 
    between 0 and 100 before proceeding.

    Parameters:
        request (HttpRequest): The HTTP request containing the subscription details.
        project_id (int): The ID of the project to subscribe to.
        share (int): The percentage share for the subscription.

    Returns:
        Response: A response indicating whether the subscription was successful or if an error occurred.

    Raises:
        serializers.ValidationError: If the share value is not between 0 and 100.

    Notes:
        - If the share is not within the valid range, an HTTP 400 response is returned.
        - If the investor is already subscribed, the share value is updated and an HTTP 200 response is returned.
        - If no record exists, a new subscription is created, and an HTTP 201 response is returned.
    """

    if share < 0 or share > 100:
        return Response(
            {"error": "Share must be greater between zero and 100"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    investor_id = request.user.user_info.company_id

    # Check if an InvestorProject with the given project_id and investor_id already exists
    try:
        investor_project = InvestorProject.objects.get(project_id=project_id, investor_id=investor_id)
        
        investor_project.share = share
        investor_project.save()

        return Response(
            {"message": f"Project share updated to {share}."}, status=status.HTTP_200_OK)

    # If no record exists, create a new one
    except InvestorProject.DoesNotExist:
        investor_project = InvestorProject(
            project_id=project_id,
            investor_id=investor_id,
            share=share
        )
        investor_project.save()

        return Response(
            {"message": f"Project subscribed with share {share}."},
            status=status.HTTP_201_CREATED
        )

@api_view(['POST'])
@permission_classes([IsInvestorRole, IsInvestorCompanySelected])
def delist_project(request, project_id):
    """
    Delist a project for a specific investor.

    This function removes an `InvestorProject` instance for a specific investor and project, effectively delisting the project 
    for the investor. It fetches the `InvestorProject` record and deletes it, returning a success message.

    Parameters:
        request (HttpRequest): The HTTP request indicating the project to be delisted.
        project_id (int): The ID of the project to delist.

    Returns:
        Response: A response indicating the successful delisting of the project.

    Raises:
        Http404: If the specified `InvestorProject` does not exist.

    Notes:
        - If successful, the function returns an HTTP 200 response with a success message.
    """
    investor_id = request.user.user_info.company_id
    investor_project = get_object_or_404(InvestorProject, project_id=project_id, investor_id=investor_id)
    investor_project.delete()

    return Response({"message": "Project delisted for the investor"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsInvestorCompanySelected | IsStartupCompanySelected])
def view_followed_projects(request):
    """
    Retrieve a list of projects followed by an investor or created by a startup and followed by investors.

    This function fetches a list of `InvestorProject` instances based on the user's role. 
    If the user is an investor, it retrieves projects followed by that investor. 
    If the user represents a startup, it retrieves projects followed by investors that belong to that startup.

    Parameters:
        request (HttpRequest): The HTTP request to fetch the followed projects.

    Returns:
        Response: A response containing the serialized list of followed projects.

    Notes:
        - If the user is an investor, the function retrieves projects that the investor follows.
        - If the user represents a startup, it retrieves projects created by the startup that are followed by investors.
        - The response contains serialized data for the list of followed projects and returns an HTTP 200 status upon success.
    """
    
    user = request.user
    if user.user_info.role == 'investor':
        # Filter any Project(s) that the Investor follows
        followed_projects = InvestorProject.objects.filter(investor__id=user.user_info.company_id)
    else:
        # Find projects created by the startup and followed by an investor
        startup_id = user.user_info.company_id
        followed_projects = InvestorProject.objects.filter(project__startup=startup_id)

    # Serialize the data and return the list
    serializer = InvestorProjectSerializer(followed_projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
