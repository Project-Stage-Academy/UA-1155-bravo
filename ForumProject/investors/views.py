from rest_framework import viewsets

from investors.models import Investor
from investors.serializers import InvestorSerializer
from users.permissions import InvestorPermission


class InvestorViewSet(viewsets.ModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [InvestorPermission, ]
