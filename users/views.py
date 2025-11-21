from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm, StudentLoginForm, EditProfileForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:landing')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
            return redirect('dashboard:landing')
        else:
            # Show form errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:landing')
    
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('dashboard:landing')
    else:
        form = StudentLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('dashboard:landing')


@login_required
def profile_view(request):
    from items.models import Item
    from .forms import ProfilePictureForm
    
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfilePictureForm(instance=request.user)
    
    # Get user's items
    my_lost_items = Item.objects.filter(user=request.user, type='lost').order_by('-created_at')
    my_found_items = Item.objects.filter(user=request.user, type='found').order_by('-created_at')
    
    context = {
        'my_lost_items': my_lost_items,
        'my_found_items': my_found_items,
        'form': form,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Handle password change if provided
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                user.set_password(new_password)
            
            user.save()
            
            # Re-login if password was changed
            if new_password:
                login(request, user)
                messages.success(request, 'Profile and password updated successfully!')
            else:
                messages.success(request, 'Profile updated successfully!')
            
            return redirect('users:profile')
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def public_profile_view(request, user_id):
    from items.models import Item
    
    profile_user = get_object_or_404(User, id=user_id)
    
    # Get user's items (only non-anonymous)
    user_lost_items = Item.objects.filter(user=profile_user, type='lost', is_anonymous=False).order_by('-created_at')
    user_found_items = Item.objects.filter(user=profile_user, type='found', is_anonymous=False).order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'user_lost_items': user_lost_items,
        'user_found_items': user_found_items,
    }
    
    return render(request, 'users/public_profile.html', context)
