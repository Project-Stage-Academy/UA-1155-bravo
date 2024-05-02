from django.shortcuts import get_object_or_404
from users.permissions import IsInvestorCompanySelected, IsInvestorRole
from rest_framework import viewsets, status
from rest_framework.response import Response
from investors.models import Investor
from investors.serializers import InvestorSerializer
from users.models import UserInvestor
from rest_framework.permissions import IsAdminUser, IsAuthenticated


class InvestorViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling investor objects.

    Inherits:
        viewsets.ModelViewSet: Base class for viewsets handling model objects.

    Attributes:
        queryset (QuerySet): Queryset containing all investor objects.
        serializer_class (Serializer): Serializer class for investor objects.

    """
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action == 'retrieve':
            permission_classes = [IsInvestorCompanySelected]
        elif self.action == 'create':
            permission_classes = [IsInvestorRole]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsInvestorCompanySelected]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        if request.user.user_info.company_id != kwargs['pk']:
            return Response({'error': 'You have no permission to view this investor'}, status=status.HTTP_400_BAD_REQUEST)
        investor = get_object_or_404(self.queryset, pk=kwargs['pk'])
        serializer = self.serializer_class(investor)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if request.user.user_info.company_id != kwargs['pk']:
            return Response({'error': 'You have no permission to update investor'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
         Handle create requests to create a startup for a user.

         Args:
             request (Request): The HTTP request object.
             *args: Additional positional arguments.
             **kwargs: Additional keyword arguments.

         Returns:
             Response: Response object with serialized data and appropriate status code.

        """
        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            investor = serializer.save()
            UserInvestor.objects.create(customuser=request.user, investor=investor, investor_role_id=1)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if request.user.user_info.company_id != kwargs['pk']:
            return Response({'error': 'You have no permission to delete investor'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
