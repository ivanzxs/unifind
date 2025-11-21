from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q, Max, Count, Case, When, IntegerField
from .models import Message, ItemReturn
from items.models import Item
from users.models import User


@login_required
def inbox(request):
    # For regular users, redirect directly to conversation with admin
    if not request.user.is_staff:
        # Find an admin user (first staff user)
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            # Redirect to conversation with admin
            return redirect('messaging:conversation', user_id=admin_user.id)
        else:
            # No admin exists, show empty conversation
            return render(request, 'messages/conversation.html', {
                'other_user': None,
                'messages': [],
            })
    
    # For admin users, show inbox with all conversations
    conversations = []
    
    # Get all users the current user has messaged with
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
    
    # Sort by last message time (handle case where conversations might be empty)
    if conversations:
        conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else x['user'].date_joined, reverse=True)
    
    return render(request, 'messages/inbox.html', {'conversations': conversations})


@login_required
def conversation(request, user_id):
    # For regular users, ensure they can only view admin conversation
    if not request.user.is_staff:
        # Find admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user and user_id != admin_user.id:
            # Redirect to admin conversation
            return redirect('messaging:conversation', user_id=admin_user.id)
        elif not admin_user:
            # No admin exists, show empty conversation
            return render(request, 'messages/conversation.html', {
                'other_user': None,
                'messages': [],
                'conversation_item': None,
            })
    
    other_user = get_object_or_404(User, id=user_id)
    
    # Get all messages between these two users
    message_list = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related('item', 'sender', 'receiver').order_by('created_at')
    
    # Mark messages as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Handle new message
    if request.method == 'POST':
        content = request.POST.get('content', '')
        images = request.FILES.getlist('image')  # Get all images
        
        if (content or images) and other_user:
            # If multiple images, create a message for each image
            if images:
                for image in images:
                    Message.objects.create(
                        sender=request.user,
                        receiver=other_user,
                        content=content if image == images[0] else '',  # Add content only to first message
                        image=image
                    )
            # If only text (no images), create single message
            elif content:
                Message.objects.create(
                    sender=request.user,
                    receiver=other_user,
                    content=content
                )
            
            return redirect('messaging:conversation', user_id=user_id)
    
    # Get the item if this conversation is about an item (get the latest one)
    conversation_item = None
    for msg in reversed(message_list):
        if msg.item:
            conversation_item = msg.item
            break
    
    return render(request, 'messages/conversation.html', {
        'other_user': other_user,
        'messages': message_list,
        'conversation_item': conversation_item,
    })


@login_required
def send_message(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # Can't message yourself
    if item.user == request.user:
        django_messages.error(request, 'You cannot message yourself.')
        return redirect('items:detail', item_id=item_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=item.user,
                item=item,
                content=content
            )
            django_messages.success(request, 'Message sent successfully!')
            return redirect('messaging:conversation', user_id=item.user.id)
    
    return render(request, 'messages/send_message.html', {
        'item': item,
    })


@login_required
def mark_item_returned(request, item_id, user_id):
    """Mark an item as returned and award reputation points"""
    item = get_object_or_404(Item, id=item_id)
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if already returned
    if hasattr(item, 'return_record'):
        django_messages.warning(request, 'This item has already been marked as returned.')
        return redirect('messaging:conversation', user_id=user_id)
    
    # Determine who is the owner and who is the returner
    if item.user == request.user:
        # Current user is the owner, other user is the returner
        owner = request.user
        returner = other_user
    else:
        # Other user is the owner, current user is the returner
        owner = other_user
        returner = request.user
    
    # Create return record
    ItemReturn.objects.create(
        item=item,
        owner=owner,
        returner=returner
    )
    
    # Update item status to claimed
    item.status = 'claimed'
    item.save()
    
    # Award reputation points
    RETURN_POINTS = 10
    owner.reputation_points += RETURN_POINTS
    returner.reputation_points += RETURN_POINTS
    owner.save()
    returner.save()
    
    django_messages.success(
        request, 
        f'Item marked as returned! Both you and {other_user.username} earned {RETURN_POINTS} reputation points! 🎉'
    )
    
    return redirect('messaging:conversation', user_id=user_id)
