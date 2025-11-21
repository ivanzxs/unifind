def unread_messages_count(request):
    """Add unread messages count to all templates"""
    if request.user.is_authenticated:
        from .models import Message
        unread_count = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        return {'unread_messages_count': unread_count}
    return {'unread_messages_count': 0}


def unread_notifications_count(request):
    """Add unread notifications count to all templates"""
    if request.user.is_authenticated:
        from notifications.models import Notification
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}
