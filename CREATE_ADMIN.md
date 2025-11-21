# Create Admin User

Run this command to create an admin user:

```powershell
.\.venv\Scripts\python manage.py createsuperuser
```

Enter:
- Username: admin
- Email: admin@unifind.com
- Password: (your choice)
- Student ID: ADMIN001

Then login at: http://127.0.0.1:8000/users/login/

Admin will automatically be redirected to admin dashboard at: http://127.0.0.1:8000/admin/

## Testing Flow

1. **As Regular User:**
   - Post a lost/found item
   - Select severity level
   - Item goes to "pending" status
   - User sees message: "submitted for admin approval"

2. **As Admin:**
   - Login and see admin dashboard
   - See pending items
   - Click "Approve" - item becomes visible
   - System automatically checks for matches
   - If match found (>40% similarity), shows in "Potential Matches"
   - Click "Notify Users" to send notifications

3. **As Regular User Again:**
   - Check notifications (will add UI for this next)
   - See "Potential Match Found!" notification
   - Click to view matched item

## What's Working Now

✅ Item posting requires approval
✅ Admin dashboard shows pending items
✅ Approve/reject functionality
✅ Auto-matching algorithm
✅ Notification creation
✅ Only approved items show in browse

## What's Left

- [ ] Notification UI in navbar
- [ ] Notification list page
- [ ] Show severity badges in browse
- [ ] Update messaging to admin-only
