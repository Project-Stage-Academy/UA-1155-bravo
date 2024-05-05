from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, pagination
from rest_framework.decorators import action
from .models import SubscribeInvestorStartup
from .serializers import SubscribeInvestorStartupSerializer
from users.models import UserInvestor
from startups.models import Startup  
from startups.serializers import StartupSerializer
from django_filters.rest_framework import DjangoFilterBackend
from startups.filters import StartupFilter
from rest_framework import filters
from django.http import Http404

class CustomPagination(pagination.PageNumberPagination):
    """
    Custom pagination class for the list of startups.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

class AddSubscription(viewsets.ModelViewSet):
    """
    View for adding a subscription.

    """

    serializer_class = SubscribeInvestorStartupSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StartupFilter

    
    def get_queryset(self):
        """
        Get the queryset for startups.

        Returns:
            Queryset: All startups.
        """
        return Startup.objects.all()


    def list(self, request, *args, **kwargs):
        """
        List all startups with pagination.

        Returns:
            Response: Paginated list of startups.
        """
        ...
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = StartupSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = StartupSerializer(queryset, many=True)
        return Response(serializer.data)
    
    
    def create(self, request):
        """
        Create a new subscription for a startup.

        Returns:
            Response: Success message or error message if user is not associated with an investor.
        """
        startup_id = request.data.get('startup')  # assuming startup_id is passed in request data
        user_investor = UserInvestor.objects.filter(customuser=request.user).first()
        if user_investor:
            # Check if subscription already exists for this investor and startup
            existing_subscription = SubscribeInvestorStartup.objects.filter(
                investor=user_investor.investor,
                startup_id=startup_id
            ).exists()
            if existing_subscription:
                return Response({'error': 'Subscription already exists'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data={'startup': startup_id})
            serializer.is_valid(raise_exception=True)
            serializer.save(investor=user_investor.investor)
            return Response({'message': 'Subscription added successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'User is not associated with an investor'}, status=status.HTTP_400_BAD_REQUEST)

class ListMySubscription(viewsets.ReadOnlyModelViewSet):
    """
    View for listing user's subscriptions.
    """
    serializer_class = SubscribeInvestorStartupSerializer

    def get_queryset(self):
        """
        Get the queryset for user's subscriptions.

        Returns:
            Queryset: Subscriptions related to the user's investor profile.
        """
        user = self.request.user
        try:
            user_investor = UserInvestor.objects.get(customuser=user)
            investor_id = user_investor.investor_id
            return SubscribeInvestorStartup.objects.filter(investor_id=investor_id)
        except UserInvestor.DoesNotExist:
            return SubscribeInvestorStartup.objects.none()

    
    def list(self, request):
        """
        List user's subscriptions with startup details.

        Returns:
            Response: List of subscriptions with startup details.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = []
        for subscription in serializer.data:
            startup_id = subscription['startup']
            startup = Startup.objects.get(id=startup_id)
            startup_serializer = StartupSerializer(startup)
            subscription['startup'] = startup_serializer.data
            response_data.append(subscription)
        return Response(response_data)
    
# consider the possibility of choosing the investor profile that will be subscribed


class UniqueSubscription(viewsets.ModelViewSet):
    """
    View for retrieving, and deleting a unique subscription.
    """

    serializer_class = SubscribeInvestorStartupSerializer

    def get_queryset(self):
        """
        Get the queryset for user's subscriptions.

        Returns:
            Queryset: Subscriptions related to the user's investor profile.
        """
        user = self.request.user
        try:
            user_investor = UserInvestor.objects.get(customuser=user)
            investor_id = user_investor.investor_id
            return SubscribeInvestorStartup.objects.filter(investor_id=investor_id)
        except UserInvestor.DoesNotExist:
            return SubscribeInvestorStartup.objects.none()

    @action(detail=True, methods=['get'])
    def subscription_by_id(self, request, pk=None):
        """
        Retrieve a subscription by its ID with startup details.

        Returns:
            Response: Subscription details with startup details.
        """
        try:
            subscription = self.get_queryset().get(pk=pk)
            startup = subscription.startup
            startup_serializer = StartupSerializer(startup)
            subscription_data = self.get_serializer(subscription).data
            subscription_data['startup'] = startup_serializer.data
            return Response(subscription_data)
        except SubscribeInvestorStartup.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
        
    

    def delete(self, request, pk, format=None):
        """
        Delete a subscription by its ID.

        Returns:
            Response: Success message if subscription is deleted.
        """
        subscription = self.get_object()
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
  
  