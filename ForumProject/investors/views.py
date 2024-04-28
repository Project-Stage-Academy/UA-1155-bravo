from django.db.migrations import serializer
from rest_framework import viewsets, status
from rest_framework.response import Response

from investors.models import Investor
from investors.serializers import InvestorSerializer
from users.models import UserInvestor
from users.permissions import InvestorPermission


class InvestorViewSet(viewsets.ModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    # permission_classes = [InvestorPermission, ]

    def create(self, request, *args, **kwargs):
        serializer = InvestorSerializer(data=request.data)
        if serializer.is_valid():
            investor = serializer.save()
            UserInvestor.objects.create(customuser=request.user, investor=investor, investor_role_id=1)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
