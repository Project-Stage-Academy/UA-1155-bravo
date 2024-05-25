"""
Utility for generating URLs related to project management.

This module provides a function for generating URLs for various project-related actions,
such as following or unsubscribing from a project.

Functions:
    get_urls: Generates URLs for project-related actions.
"""

from django.urls import reverse


def get_urls(project_id, share=50):
    """
        Generate URLs for project-related actions.

        Args:
            project_id (int): The ID of the project.
            share (int, optional): The share percentage for subscription URL. Defaults to 50.

        Returns:
            dict: A dictionary containing URLs for different project-related actions.
                Keys:
                - 'FOLLOW_URL': URL for following a project.
                - 'UNFOLLOW_URL': URL for unfollowing a project.
                - 'SUBSCRIPTION_URL': URL for subscription to a project.
                - 'NOTIFICATION_DETAIL_URL': URL for notification detail.

        """
    return {
        'FOLLOW_URL': reverse('projects:follow', kwargs={'project_id': project_id}),
        'UNFOLLOW_URL': reverse('projects:delist_project',
                                kwargs={'project_id': project_id}),
        'SUBSCRIPTION_URL': reverse('projects:subscription',
                                    kwargs={'project_id': project_id, 'share': share}),
        'NOTIFICATION_DETAIL_URL': reverse('notifications:notification_detail'),
    }


EXPECTED_STATUS = {
    'CREATED': 201,
    'OK': 200,
    'FORBIDDEN': 403
}
