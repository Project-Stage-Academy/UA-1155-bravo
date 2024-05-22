from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Project, InvestorProject
from .serializers import InvestorProjectSerializer


@api_view(['GET'])
def project_investor_shares(request, project_id):
    """
    View to get all investors and their shares for a specific project,
    along with the total share.
    """
    project = get_object_or_404(Project, pk=project_id)
    investor_projects = InvestorProject.objects.filter(project=project)

    # Calculate total funding
    total_funding = InvestorProject.get_total_funding(project_id)

    # Serialize individual investor shares
    investor_projects_serialized = InvestorProjectSerializer(investor_projects, many=True).data

    # Prepare response data
    data = {
        'project': project.name,
        'investors': investor_projects_serialized,
        'total_share': total_funding
    }

    return Response(data)
