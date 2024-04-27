from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from users.models import UserInvestor
from .serializers import InvestorSerializer
from .models import Investor

class InvestorViewSet(viewsets.ModelViewSet):

    
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer

class PostForUserInvestor(APIView):  
    
    
    def post(self, request, *args, **kwargs):
        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            investor_id = serializer.save()
            user = request.user
            UserInvestor.objects.create(customuser=user, investor=investor_id, investor_role_id=1) 

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)