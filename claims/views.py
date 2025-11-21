from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from items.models import Item
from notifications.models import Notification
from .models import Claim
from .forms import ClaimForm


@login_required
def claim_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, type='found', status='unclaimed')
    
    # Prevent claiming own items
    if item.user == request.user:
        messages.error(request, 'You cannot claim your own item.')
        return redirect('items:detail', item_id=item_id)
    
    # Check if user already has a pending claim
    existing_claim = Claim.objects.filter(item=item, claimant=request.user, status='pending').first()
    if existing_claim:
        messages.info(request, 'You already have a pending claim for this item.')
        return redirect('items:detail', item_id=item_id)
    
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimant = request.user
            claim.save()
            
            # Create notification for item owner
            Notification.objects.create(
                user=item.user,
                message=f'Someone is trying to claim your found item: {item.category}. Please review the claim.'
            )
            
            messages.success(request, 'Your claim has been submitted. The finder will review your answer.')
            return redirect('items:detail', item_id=item_id)
    else:
        form = ClaimForm()
    
    return render(request, 'claims/claim_item.html', {
        'form': form,
        'item': item
    })


@login_required
def review_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    
    # Only item owner can review claims
    if claim.item.user != request.user:
        messages.error(request, 'You are not authorized to review this claim.')
        return redirect('dashboard:landing')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            claim.status = 'approved'
            claim.item.status = 'claimed'
            claim.item.save()
            claim.save()
            
            # Update claimant reputation
            claim.claimant.reputation_points += 0  # Owner gets points, not claimant
            
            # Update item owner reputation
            request.user.reputation_points += 10
            request.user.save()
            
            # Notify claimant
            Notification.objects.create(
                user=claim.claimant,
                message=f'Your claim for {claim.item.category} has been approved! You can now collect the item.'
            )
            
            messages.success(request, 'Claim approved! You earned 10 reputation points.')
            
        elif action == 'reject':
            claim.status = 'rejected'
            claim.save()
            
            # Notify claimant
            Notification.objects.create(
                user=claim.claimant,
                message=f'Your claim for {claim.item.category} was not approved. The answer may be incorrect.'
            )
            
            messages.info(request, 'Claim rejected.')
        
        return redirect('dashboard:landing')
    
    return render(request, 'claims/review_claim.html', {'claim': claim})
