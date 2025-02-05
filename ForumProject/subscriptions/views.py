from django.core.paginator import EmptyPage

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from startups.filters import StartupFilter
from startups.models import Startup
from startups.serializers import StartupSerializer
from users.models import UserInvestor
from users.permissions import IsInvestorCompanySelected, IsInvestorRole
from .filters import MySubscriptionFilter
from .models import SubscribeInvestorStartup
from .serializers import SubscribeInvestorStartupSerializer


class CustomPagination(pagination.PageNumberPagination):
    """
    Custom pagination class for the list of startups.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """
        Custom pagination to handle invalid page numbers.
        """
        try:
            return super().paginate_queryset(queryset, request, view=view)
        except Exception as e:
            return self.handle_invalid_page_number(str(e))

    def handle_invalid_page_number(self, error_message):
        """
        Handle scenarios where the page number is invalid.
        """
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    def get_page(self, *args, **kwargs):
        try:
            return super().get_page(*args, **kwargs)
        except EmptyPage:
            return self.handle_invalid_page_number("Page does not exist.")

class AddSubscription(viewsets.ModelViewSet):
    """
    View for adding a subscription.
    """
    serializer_class = SubscribeInvestorStartupSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = StartupFilter
    permission_classes = [IsInvestorRole, IsInvestorCompanySelected]

    def get_queryset(self):
        """
        Get the queryset for startups.

        Returns:
            Queryset: All startups.
        """
        return Startup.objects.all()

    def filter_queryset(self, queryset):
        """
        Filter the queryset and handle any invalid filter input.
        """
        try:
            queryset = super().filter_queryset(queryset)
        except Exception as e:
            return self.handle_invalid_filters(str(e))
        return queryset

    def handle_invalid_filters(self, error_message):
        """
        Handle scenarios where filters have invalid input or encounter errors.
        """
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        List all startups with pagination.

        Returns:
            Response: Paginated list of startups.
        """
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() == 0:
            return Response({'error': 'No startups found with the given filters.'}, status=status.HTTP_404_NOT_FOUND)

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

class SubscriptionMixin:
    """
    Mixin class containing methods related to user's subscriptions.
    """

    def get_user_investor(self):
        """
        Get the user's investor profile.

        Returns:
            UserInvestor or None: Investor profile if exists, None otherwise.
        """
        user = self.request.user
        try:
            user_investor = UserInvestor.objects.get(customuser=user)
            return user_investor.investor
        except UserInvestor.DoesNotExist:
            return None

    def get_subscriptions_by_investor(self, user_investor):
        """
        Get subscriptions related to the given investor profile.

        Args:
            user_investor (UserInvestor): User's investor profile.

        Returns:
            Queryset: Subscriptions related to the user's investor profile.
        """
        return SubscribeInvestorStartup.objects.filter(investor=user_investor)

class SubscriptionViewsets(viewsets.ModelViewSet, SubscriptionMixin):
    """
    View for retrieving, and deleting a unique subscription.
    """
    serializer_class = SubscribeInvestorStartupSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = MySubscriptionFilter
    search_fields = ['^startup__startup_name', '^startup__startup_industry', '=startup__startup_country']
    permission_classes = [IsInvestorRole, IsInvestorCompanySelected]

    def get_queryset(self):
        """
        Get the queryset for user's subscriptions.

        Returns:
            Queryset: Subscriptions related to the user's investor profile.
        """
        user_investor = self.get_user_investor()
        if user_investor:
            return self.get_subscriptions_by_investor(user_investor)
        else:
            return SubscribeInvestorStartup.objects.none()

    def get_subscription_with_startup_details(self, pk):
        """
        Retrieve a subscription by its ID with startup details.

        Args:
            pk: Primary key of the subscription.

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

    @action(detail=True, methods=['get'])
    def subscription_by_id(self, request, pk=None):
        """
        Retrieve a subscription by its ID with startup details.

        Returns:
            Response: Subscription details with startup details.
        """
        return self.get_subscription_with_startup_details(pk)

    def list(self, request, *args, **kwargs):
        """
        List all subscriptions with startup details.

        Returns:
            Response: List of subscriptions with startup details.
        """
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.count() == 0:
            return Response({'error': 'No startups found with the given filters.'}, status=status.HTTP_404_NOT_FOUND)
        response_data = []
        for subscription in queryset:
            if subscription.startup_id is not None:
                startup = subscription.startup
                startup_serializer = StartupSerializer(startup)
                subscription_data = self.get_serializer(subscription).data
                subscription_data['startup'] = startup_serializer.data
                response_data.append(subscription_data)
        return Response(response_data)

    def delete(self, request, pk=None, format=None):
        """
        Delete a subscription by its ID.

        Returns:
            Response: Success message if subscription is deleted.
        """
        try:
            subscription = self.get_object()
            user_investor = UserInvestor.objects.get(customuser=request.user)
            if subscription.investor == user_investor.investor:
                subscription.delete()
                return Response({'message': 'Unsubscribed successfully.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Subscription does not belong to the current user'}, status=status.HTTP_403_FORBIDDEN)
        except SubscribeInvestorStartup.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=status.HTTP_404_NOT_FOUND)
        except AttributeError:
            return Response({'error': 'Subscription ID is missing'}, status=status.HTTP_400_BAD_REQUEST)
        except UserInvestor.DoesNotExist:
            return Response({'error': 'User is not associated with an investor'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
