from django.urls import reverse

def get_urls(project_id, share=50):
    return {
        'FOLLOW_URL': reverse('projects:follow', kwargs={'project_id': project_id}),
        'UNFOLLOW_URL': reverse('projects:delist_project', kwargs={'project_id': project_id}),
        'SUBSCRIPTION_URL': reverse('projects:subscription', kwargs={'project_id': project_id, 'share': share}),
        'NOTIFICATION_DETAIL_URL': reverse('notifications:notification_detail'),
    }

EXPECTED_STATUS = {
    'CREATED': 201,
    'OK': 200,
    'FORBIDDEN': 403
}
