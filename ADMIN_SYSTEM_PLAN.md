# Admin-Mediated System Implementation Plan

## Overview
Converting from P2P (user-to-user) to Admin-mediated system where all transactions are controlled by admin.

## Major Changes

### 1. Database Models ✅
- [x] Add `severity` field to Item (LOW, MEDIUM, HIGH, CRITICAL)
- [x] Change default status to PENDING
- [x] Add APPROVED and REJECTED status
- [x] Add `approved_by`, `approved_at`, `rejection_reason` fields
- [x] Create `ItemMatch` model for storing matches
- [x] Create `Notification` model for user notifications

### 2. Item Posting Flow
- [ ] All new items start with status=PENDING
- [ ] User selects severity level when posting
- [ ] Items don't appear in public browse until APPROVED
- [ ] Admin sees pending items in dashboard

### 3. Auto-Matching System
- [ ] When admin approves an item, check for matches
- [ ] Match lost items with found items based on:
  - Category
  - Description similarity
  - Location proximity
  - Time posted
- [ ] Calculate match percentage
- [ ] Create ItemMatch records
- [ ] Create notifications for both users

### 4. Admin Dashboard
- [ ] Show pending items (to approve/reject)
- [ ] Show item matches
- [ ] Button to notify users about matches
- [ ] View all messages (user-to-admin)
- [ ] Approve/reject items with reason

### 5. User Dashboard Changes
- [ ] Show only APPROVED items in browse
- [ ] Show severity badges on items
- [ ] Notification section for:
  - Item approved/rejected
  - Potential matches found
  - Messages from admin

### 6. Messaging System Changes
- [ ] Remove user-to-user messaging
- [ ] All messages go to admin
- [ ] Admin can reply to users
- [ ] Message button on items → message admin about that item

### 7. Notification System
- [ ] Notification bell in navbar
- [ ] Unread count badge
- [ ] Notification list page
- [ ] Types:
  - Item approved
  - Item rejected (with reason)
  - Potential match found (with match %)
  - Item claimed
  - New message from admin

## Implementation Steps

1. ✅ Update models
2. Run migrations
3. Update forms (add severity field)
4. Create admin dashboard views
5. Create matching algorithm
6. Update messaging system
7. Create notification system
8. Update all templates
9. Test thoroughly

## Files to Modify

### Models
- ✅ `items/models.py` - Item, ItemMatch, Notification
- ✅ `users/models.py` - Already has is_staff

### Views
- `items/views.py` - Update to check status=APPROVED
- `dashboard/views.py` - Split into user/admin dashboards
- `messaging/views.py` - Change to admin-only
- NEW: `admin_dashboard/views.py`

### Templates
- All item browse/list templates - filter APPROVED only
- NEW: Admin dashboard templates
- NEW: Notification templates
- Update messaging templates

### Forms
- `items/forms.py` - Add severity field

## Next Steps
1. Run migrations
2. Create admin dashboard app
3. Implement matching algorithm
4. Update existing views/templates
