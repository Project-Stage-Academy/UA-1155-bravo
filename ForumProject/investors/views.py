from rest_framework.response import Response
from rest_framework import viewsets, status
from users.models import UserInvestor
from .serializers import InvestorSerializer
from .models import Investor
from django.db.migrations import serializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from investors.models import Investor
from investors.serializers import InvestorSerializer
from users.models import UserInvestor


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
    # permission_classes = [InvestorPermission, ]
  
    
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

