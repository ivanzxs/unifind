from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Item
from .forms import LostItemForm, FoundItemForm, EditItemForm


@login_required
def post_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.type = 'lost'
            
            # Auto-assign severity based on category
            if item.category in ['Gadget', 'Keys']:
                item.severity = 'critical'
            elif item.category in ['Wallet', 'ID']:
                item.severity = 'high'
            elif item.category in ['Book', 'Clothing']:
                item.severity = 'medium'
            else:
                item.severity = 'low'
            
            # Admin posts are auto-approved, others are pending
            if request.user.is_staff:
                item.status = 'approved'
            else:
                item.status = 'pending'
            
            item.save()
            
            if request.user.is_staff:
                messages.success(request, 'Your lost item has been posted successfully!')
            else:
                messages.success(request, 'Your lost item has been submitted for admin approval. You will be notified once it is reviewed.')
            
            return redirect('dashboard:admin_home' if request.user.is_staff else 'dashboard:landing')
        else:
            # Show errors if form is invalid
            print("FORM ERRORS:", form.errors)  # Debug: print errors to console
            messages.error(request, f'Please correct the errors below. Errors: {form.errors}')
    else:
        form = LostItemForm()
    
    return render(request, 'items/post_item.html', {
        'form': form,
        'item_type': 'lost',
        'title': 'Report Lost Item'
    })


@login_required
def post_found_item(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.type = 'found'
            
            # Auto-assign severity based on category
            if item.category in ['Gadget', 'Keys']:
                item.severity = 'critical'
            elif item.category in ['Wallet', 'ID']:
                item.severity = 'high'
            elif item.category in ['Book', 'Clothing']:
                item.severity = 'medium'
            else:
                item.severity = 'low'
            
            # Admin posts are auto-approved, others are pending
            if request.user.is_staff:
                item.status = 'approved'
            else:
                item.status = 'pending'
            
            item.save()
            
            if request.user.is_staff:
                messages.success(request, 'Your found item has been posted successfully!')
            else:
                messages.success(request, 'Your found item has been submitted for admin approval. You will be notified once it is reviewed.')
            
            return redirect('dashboard:admin_home' if request.user.is_staff else 'dashboard:landing')
        else:
            # Show errors if form is invalid
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FoundItemForm()
    
    return render(request, 'items/post_item.html', {
        'form': form,
        'item_type': 'found',
        'title': 'Report Found Item'
    })


def browse_items(request):
    # Show only APPROVED items
    items = Item.objects.filter(status='approved').order_by('-created_at')
    
    # Filter by type
    item_type = request.GET.get('type')
    if item_type in ['lost', 'found']:
        items = items.filter(type=item_type)
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Search - search in both name and description fields
    search = request.GET.get('search')
    if search:
        items = items.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    return render(request, 'items/browse.html', {'items': items})


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'items/detail.html', {'item': item})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # Only owner can edit
    if item.user != request.user:
        messages.error(request, 'You are not authorized to edit this item.')
        return redirect('items:detail', item_id=item_id)
    
    if request.method == 'POST':
        form = EditItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            old_username = item.claimed_by_username
            saved_item = form.save()
            
            # Check if reputation points were awarded
            if saved_item.claimed_by_username and saved_item.claimed_by_username != old_username:
                messages.success(
                    request, 
                    f'Item updated successfully! Both you and {saved_item.claimed_by_username} earned 10 reputation points! 🎉'
                )
            else:
                messages.success(request, 'Item updated successfully!')
            return redirect('items:detail', item_id=item_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditItemForm(instance=item)
    
    return render(request, 'items/edit_item.html', {
        'form': form,
        'item': item
    })


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    # Only owner or admin can delete
    if item.user != request.user and not request.user.is_staff:
        messages.error(request, 'You are not authorized to delete this item.')
        return redirect('items:detail', item_id=item_id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully.')
        # Redirect based on user type
        if request.user.is_staff:
            # Admin - redirect back to where they came from or admin browse
            from django.http import HttpResponseRedirect
            referer = request.META.get('HTTP_REFERER', '')
            if 'admin/browse' in referer:
                return redirect('dashboard:admin_browse')
            elif 'admin/home' in referer:
                return redirect('dashboard:admin_home')
            else:
                return redirect('dashboard:admin_browse')
        else:
            return redirect('users:profile')
    
    return redirect('items:detail', item_id=item_id)


@login_required
def mark_as_claimed(request, item_id):
    """Admin marks item as claimed"""
    item = get_object_or_404(Item, id=item_id)
    
    # Only admin can mark as claimed
    if not request.user.is_staff:
        messages.error(request, 'Only admins can mark items as claimed.')
        return redirect('items:detail', item_id=item_id)
    
    # Only approved items can be marked as claimed
    if item.status != 'approved':
        messages.error(request, 'Only approved items can be marked as claimed.')
        return redirect('items:detail', item_id=item_id)
    
    if request.method == 'POST':
        item.status = 'claimed'
        item.save()
        messages.success(request, 'Item marked as claimed successfully.')
        return redirect('items:detail', item_id=item_id)
    
    return redirect('items:detail', item_id=item_id)
