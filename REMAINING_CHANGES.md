# 📋 Remaining Changes to Implement

## ✅ COMPLETED:
1. ✅ Landing page navbar - active highlight + yellow separator line
2. ✅ Removed popup notifications (messages)
3. ✅ Removed "My Dashboard" from user sidebar
4. ✅ Removed "Post Item" from admin sidebar
5. ✅ Split Report Lost/Found for admin (like user sidebar)

## ⏳ TODO:

### 2. How It Works Section - Font Awesome Icons
- [ ] Replace emojis with Font Awesome icons
- [ ] Match sidebar icon style
- [ ] Yellow icons

### 3. Login Form - Email Only
- [ ] Remove username field
- [ ] Only email + password
- [ ] Update login form and view

### 4. Post Anonymous Checkbox
- [ ] Move to left side
- [ ] Checkbox on left
- [ ] Better alignment

### 5. Remove Asterisks from Field Names
- [ ] Remove required asterisks
- [ ] Clean field labels

### 6. Admin Dashboard Boxes - Add Shadow
- [ ] Add box-shadow to stat cards
- [ ] Better depth/elevation

### 7. Notifications - Unread Highlight
- [ ] Highlight unread notifications
- [ ] Remove highlight when viewed
- [ ] Add item image for match/approved notifications

### 8. Admin Notifications - Match Only
- [ ] Remove pending post notifications
- [ ] Only show match notifications
- [ ] Pending items visible in dashboard anyway

### 9. Item Detail - Remove Back Button
- [ ] Remove "Back to Browse" button
- [ ] Cleaner interface

### 10. Messages - Profile Pictures
- [ ] Admin sees user profile pics
- [ ] Users see generic admin icon
- [ ] Show "Admin" instead of admin username

## 📝 Implementation Notes:

### Login Form Changes:
```python
# users/forms.py
class StudentLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254)
    # Remove username, use email only
```

### Notification Highlights:
```css
.notification.unread {
    background: #fff3cd;
    border-left: 4px solid #ecb80d;
    font-weight: 600;
}
```

### Admin Dashboard Shadow:
```css
.stat-card {
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

### Message Display:
- If admin logged in: Show user profile pic + name
- If user logged in: Show admin icon + "Admin" text

## Priority Order:
1. Login form (email only)
2. How It Works icons
3. Post anonymous alignment
4. Remove asterisks
5. Admin dashboard shadows
6. Notification highlights + images
7. Admin notif filtering
8. Remove back button
9. Message profile pics

## Files to Modify:
- `templates/dashboard/index.html` - How It Works icons
- `users/forms.py` - Login form
- `templates/users/login.html` - Login template
- `templates/items/post_item.html` - Anonymous checkbox
- `items/forms.py` - Remove asterisks
- `templates/dashboard/admin_dashboard.html` - Add shadows
- `templates/dashboard/notifications.html` - Highlights + images
- `templates/dashboard/admin_notifications.html` - Filter matches only
- `templates/items/detail.html` - Remove back button
- `templates/messaging/inbox.html` - Profile pics
- `templates/messaging/thread.html` - Profile pics

## Status: 5/15 tasks complete (33%)
