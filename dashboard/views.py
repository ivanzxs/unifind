from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from items.models import Item
from claims.models import Claim
from notifications.models import Notification


def landing(request):
    # Redirect to admin home if user is staff
    if request.user.is_authenticated and request.user.is_staff:
        from django.shortcuts import redirect
        return redirect('dashboard:admin_home')
    
    # Show only APPROVED items on landing page
    recent_items = Item.objects.filter(status='approved').order_by('-created_at')[:6]
    search_results = None
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        from django.db.models import Q
        search_results = Item.objects.filter(
            status='approved'
        ).filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by('-created_at')
        # Only show recent items if no search
        if not search_results.exists():
            recent_items = []
        else:
            recent_items = []
    
    return render(request, 'dashboard/index.html', {
        'recent_items': recent_items, 
        'search_query': search_query,
        'search_results': search_results,
    })


@login_required
def student_dashboard(request):
    # Handle search
    search_query = request.GET.get('search')
    search_results = None
    if search_query:
        from django.db.models import Q
        search_results = Item.objects.filter(
            status='approved'
        ).filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by('-created_at')
    
    # User's items - sorted by priority (critical first)
    severity_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
    my_lost_items = sorted(
        Item.objects.filter(user=request.user, type='lost'),
        key=lambda x: (severity_order.get(x.severity, 5), -x.created_at.timestamp())
    )
    my_found_items = sorted(
        Item.objects.filter(user=request.user, type='found'),
        key=lambda x: (severity_order.get(x.severity, 5), -x.created_at.timestamp())
    )
    
    # Claims on user's found items (for review)
    claims_to_review = Claim.objects.filter(
        item__user=request.user,
        status='pending'
    ).select_related('item', 'claimant').order_by('-created_at')
    
    # User's claims
    my_claims = Claim.objects.filter(claimant=request.user).select_related('item').order_by('-created_at')
    
    # Recent notifications
    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = all_notifications.filter(is_read=False).count()
    notifications = all_notifications[:10]
    
    context = {
        'my_lost_items': my_lost_items,
        'my_found_items': my_found_items,
        'claims_to_review': claims_to_review,
        'my_claims': my_claims,
        'notifications': notifications,
        'unread_count': unread_count,
        'search_query': search_query,
        'search_results': search_results,
    }
    
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark all as read when viewing
    notifications.filter(is_read=False).update(is_read=True)
    
    # Mark specific notification as read
    if request.method == 'POST':
        notif_id = request.POST.get('notification_id')
        if notif_id:
            Notification.objects.filter(id=notif_id, user=request.user).update(is_read=True)
    
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})


@login_required
def admin_home(request):
    """Admin home page with search functionality"""
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Only staff can access
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard:landing')
    
    # Handle search
    search_query = request.GET.get('search')
    search_results = None
    if search_query:
        from django.db.models import Q
        search_results = Item.objects.filter(
            status='approved'
        ).filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by('-created_at')
    
    # Show only APPROVED items on home page
    recent_items = Item.objects.filter(status='approved').order_by('-created_at')[:6]
    
    return render(request, 'dashboard/admin_home.html', {
        'recent_items': recent_items,
        'search_query': search_query,
        'search_results': search_results,
    })


@login_required
def admin_dashboard(request):
    """Admin dashboard showing pending items and matches"""
    from django.contrib.admin.views.decorators import staff_member_required
    from django.utils.decorators import method_decorator
    from items.models import ItemMatch
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Only staff can access
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard:landing')
    
    # Handle search
    search_query = request.GET.get('search')
    search_results = None
    if search_query:
        from django.db.models import Q
        search_results = Item.objects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by('-created_at')
    
    # Get pending items - sorted by priority (critical first)
    from django.db.models import Case, When, IntegerField
    pending_items = Item.objects.filter(status='pending').annotate(
        severity_order=Case(
            When(severity='critical', then=1),
            When(severity='high', then=2),
            When(severity='medium', then=3),
            When(severity='low', then=4),
            default=5,
            output_field=IntegerField()
        )
    ).order_by('severity_order', '-created_at')
    
    # Get recent matches
    recent_matches = ItemMatch.objects.filter(notified=False).select_related('lost_item', 'found_item')[:20]
    
    # Get all approved items count
    approved_count = Item.objects.filter(status='approved').count()
    rejected_count = Item.objects.filter(status='rejected').count()
    
    # Get lost items data for the last 7 days by category
    from django.utils import timezone
    from datetime import timedelta, datetime
    from django.db.models import Count
    import json
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)  # Last 7 days including today
    
    # Use all predefined categories (always show all in legend)
    predefined_categories = ['ID', 'Gadget', 'Clothing', 'Accessories', 'Book', 'Keys', 'Wallet', 'Others']
    categories = predefined_categories
    
    # Prepare data structure for chart
    dates = [(start_date + timedelta(days=i)).strftime('%b %d') for i in range(7)]
    
    # Get lost items count per category per day (all items regardless of status)
    # Include all categories even if they have 0 counts
    category_data = {}
    for category in categories:
        daily_counts = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            # Convert date to datetime at start of day in timezone
            day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            # Count all lost items (approved, pending, etc.) posted by users
            count = Item.objects.filter(
                type='lost',
                category=category,
                status='approved',
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            daily_counts.append(count)
        category_data[category] = daily_counts
    
    context = {
        'pending_items': pending_items,
        'recent_matches': recent_matches,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_count': pending_items.count(),
        'chart_dates': json.dumps(dates),
        'chart_categories': json.dumps(categories),
        'chart_data': json.dumps(category_data),
        'search_query': search_query,
        'search_results': search_results,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def approve_item(request, item_id):
    """Admin approves an item and checks for matches"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.utils import timezone
    
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:landing')
    
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        item.status = 'approved'
        item.approved_by = request.user
        item.approved_at = timezone.now()
        item.save()
        
        # Notify user
        Notification.objects.create(
            user=item.user,
            type='item_approved',
            title='Item Approved!',
            message=f'Your {item.get_type_display()} item "{item.name or item.description[:30]}" has been approved and is now visible.',
            item=item,
            link_url=f'/items/{item.id}/'
        )
        
        # Check for matches
        find_matches_for_item(item)
        
        messages.success(request, f'Item approved! Checking for matches...')
        return redirect('dashboard:admin_dashboard')
    
    return redirect('dashboard:admin_dashboard')


@login_required
def reject_item(request, item_id):
    """Admin rejects an item"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:landing')
    
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Does not meet requirements')
        item.status = 'rejected'
        item.rejection_reason = reason
        item.save()
        
        # Notify user
        Notification.objects.create(
            user=item.user,
            type='item_rejected',
            title='Item Rejected',
            message=f'Your {item.get_type_display()} item was rejected. Reason: {reason}',
            item=item
        )
        
        messages.success(request, 'Item rejected and user notified.')
        return redirect('dashboard:admin_dashboard')
    
    return redirect('dashboard:admin_dashboard')


def find_matches_for_item(item):
    """Find potential matches for an approved item"""
    from items.models import ItemMatch
    from difflib import SequenceMatcher
    
    if item.type == 'lost':
        # Find matching found items
        potential_matches = Item.objects.filter(
            type='found',
            status='approved',
            category=item.category
        ).exclude(id=item.id)
    else:
        # Find matching lost items
        potential_matches = Item.objects.filter(
            type='lost',
            status='approved',
            category=item.category
        ).exclude(id=item.id)
    
    for match in potential_matches:
        # Calculate match percentage based on description similarity
        similarity = SequenceMatcher(None, 
                                    item.description.lower(), 
                                    match.description.lower()).ratio()
        
        # Boost score if names match
        if item.name and match.name:
            name_similarity = SequenceMatcher(None, 
                                            item.name.lower(), 
                                            match.name.lower()).ratio()
            similarity = (similarity + name_similarity) / 2
        
        match_percentage = int(similarity * 100)
        
        # Only create match if > 40% similar
        if match_percentage >= 40:
            if item.type == 'lost':
                ItemMatch.objects.get_or_create(
                    lost_item=item,
                    found_item=match,
                    defaults={'match_percentage': match_percentage}
                )
            else:
                ItemMatch.objects.get_or_create(
                    lost_item=match,
                    found_item=item,
                    defaults={'match_percentage': match_percentage}
                )


@login_required
def notify_match(request, match_id):
    """Admin notifies users about a match"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from items.models import ItemMatch
    
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:landing')
    
    match = get_object_or_404(ItemMatch, id=match_id)
    
    if request.method == 'POST':
        # Notify lost item owner
        Notification.objects.create(
            user=match.lost_item.user,
            type='match_found',
            title=f'Potential Match Found! ({match.match_percentage}% match)',
            message=f'A found item matching your lost {match.lost_item.category} has been reported. Check it out!',
            item=match.found_item,
            match=match,
            link_url=f'/items/{match.found_item.id}/'
        )
        
        # Notify found item owner
        Notification.objects.create(
            user=match.found_item.user,
            type='match_found',
            title=f'Potential Match Found! ({match.match_percentage}% match)',
            message=f'Someone reported a lost {match.lost_item.category} that matches your found item. Check it out!',
            item=match.lost_item,
            match=match,
            link_url=f'/items/{match.lost_item.id}/'
        )
        
        # Mark as notified
        match.notified = True
        match.save()
        
        messages.success(request, f'Both users notified about the {match.match_percentage}% match!')
        return redirect('dashboard:admin_dashboard')
    
    return redirect('dashboard:admin_dashboard')


@login_required
def admin_browse_items(request):
    """Admin can browse ALL items (including pending/rejected)"""
    from django.shortcuts import redirect
    from django.contrib import messages
    
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:landing')
    
    # Show ALL items for admin
    items = Item.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        items = items.filter(status=status)
    
    # Filter by type
    item_type = request.GET.get('type')
    if item_type in ['lost', 'found']:
        items = items.filter(type=item_type)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Search
    search = request.GET.get('search')
    if search:
        from django.db.models import Q
        items = items.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(category__icontains=search)
        )
    
    context = {
        'items': items,
        'is_admin': True,
    }
    
    return render(request, 'dashboard/admin_browse.html', context)


@login_required
def admin_messages(request):
    """Admin views all messages"""
    from messaging.models import Message
    from django.db.models import Q
    from users.models import User
    
    if not request.user.is_staff:
        from django.shortcuts import redirect
        from django.contrib import messages as msg
        msg.error(request, 'Access denied.')
        return redirect('dashboard:landing')
    
    # Get all conversations (similar to user inbox)
    conversations = []
    
    # Get all users the admin has messaged with
    user_ids = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values_list('sender', 'receiver')
    
    other_user_ids = set()
    for sender_id, receiver_id in user_ids:
        if sender_id != request.user.id:
            other_user_ids.add(sender_id)
        if receiver_id != request.user.id:
            other_user_ids.add(receiver_id)
    
    for user_id in other_user_ids:
        other_user = User.objects.get(id=user_id)
        
        # Get last message in conversation
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=other_user) |
            Q(sender=other_user, receiver=request.user)
        ).order_by('-created_at').first()
        
        # Count unread messages from this user
        unread_count = Message.objects.filter(
            sender=other_user,
            receiver=request.user,
            is_read=False
        ).count()
        
        conversations.append({
            'user': other_user,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message'].created_at, reverse=True)
    
    return render(request, 'dashboard/admin_messages.html', {'conversations': conversations})


def about_us(request):
    """About Us page"""
    return render(request, 'dashboard/about_us.html')


@login_required  
def admin_notifications(request):
    """Admin views all notifications - match notifications only"""
    if not request.user.is_staff:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Access denied.')
        return redirect('dashboard:landing')
    
    # Get only match notifications (not pending posts)
    all_notifications = Notification.objects.filter(
        type='match_found'
    ).select_related('user', 'item', 'match').order_by('-created_at')[:100]
    
    context = {
        'notifications': all_notifications,
    }
    
    return render(request, 'dashboard/admin_notifications.html', context)
