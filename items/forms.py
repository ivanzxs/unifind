from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('ID', 'ID Card'),
        ('Gadget', 'Gadget/Electronics'),
        ('Book', 'Book/Notebook'),
        ('Clothing', 'Clothing/Accessories'),
        ('Keys', 'Keys'),
        ('Wallet', 'Wallet/Purse'),
        ('Others', 'Others'),
    ]
    
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=True)
    
    class Meta:
        model = Item
        fields = ['category', 'name', 'description', 'image', 'location_text', 
                  'location_lat', 'location_lng', 'verification_question', 'is_anonymous']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Black Headphones, Blue Wallet, Math Textbook'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide detailed description...'}),
            'location_text': forms.TextInput(attrs={'placeholder': 'e.g., Library Entrance, Room 301'}),
            'location_lat': forms.HiddenInput(),
            'location_lng': forms.HiddenInput(),
            'verification_question': forms.TextInput(attrs={'placeholder': 'e.g., What color is it? What\'s written on it?'}),
        }
        labels = {
            'category': 'Category',
            'name': 'Item Name',
            'description': 'Description',
            'image': 'Upload Photo',
            'location_text': 'Location',
            'verification_question': 'Verification Question',
            'is_anonymous': 'Post Anonymously',
        }
    
    def __init__(self, *args, **kwargs):
        item_type = kwargs.pop('item_type', None)
        super().__init__(*args, **kwargs)
        
        # Remove asterisks from required fields
        for field_name, field in self.fields.items():
            field.label_suffix = ''
        
        # Make coordinates not required (they're optional)
        self.fields['location_lat'].required = False
        self.fields['location_lng'].required = False
        
        # Verification question only required for found items
        if item_type == 'found':
            self.fields['verification_question'].required = True
            self.fields['verification_question'].help_text = 'This will be asked to claimants to verify ownership'
        else:
            self.fields['verification_question'].required = False
            self.fields['verification_question'].widget = forms.HiddenInput()
    
    def clean_location_lat(self):
        lat = self.cleaned_data.get('location_lat')
        if lat and (lat < -90 or lat > 90):
            return None  # Invalid latitude, ignore it
        return lat
    
    def clean_location_lng(self):
        lng = self.cleaned_data.get('location_lng')
        if lng and (lng < -180 or lng > 180):
            return None  # Invalid longitude, ignore it
        return lng


class LostItemForm(ItemForm):
    def __init__(self, *args, **kwargs):
        kwargs['item_type'] = 'lost'
        super().__init__(*args, **kwargs)


class FoundItemForm(ItemForm):
    def __init__(self, *args, **kwargs):
        kwargs['item_type'] = 'found'
        super().__init__(*args, **kwargs)


class EditItemForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('ID', 'ID Card'),
        ('Gadget', 'Gadget/Electronics'),
        ('Book', 'Book/Notebook'),
        ('Clothing', 'Clothing/Accessories'),
        ('Keys', 'Keys'),
        ('Wallet', 'Wallet/Purse'),
        ('Others', 'Others'),
    ]
    
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=True)
    
    class Meta:
        model = Item
        fields = ['category', 'name', 'description', 'image', 'location_text', 
                  'location_lat', 'location_lng', 'claim_proof', 'claimed_by_username']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Black Headphones, Blue Wallet, Math Textbook'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide detailed description...'}),
            'location_text': forms.TextInput(attrs={'placeholder': 'e.g., Library Entrance, Room 301'}),
            'location_lat': forms.HiddenInput(),
            'location_lng': forms.HiddenInput(),
            'claim_proof': forms.FileInput(attrs={'accept': 'image/*'}),
            'claimed_by_username': forms.TextInput(attrs={'placeholder': 'Enter username of person who returned/claimed'}),
        }
        labels = {
            'category': 'Category',
            'name': 'Item Name',
            'description': 'Description',
            'image': 'Upload Photo',
            'location_text': 'Location',
            'claim_proof': 'Proof of Return/Claim',
            'claimed_by_username': 'Returned/Claimed By (Username)',
        }
        help_texts = {
            'claim_proof': 'Upload proof (e.g., photo of handover, screenshot). Required if providing username.',
            'claimed_by_username': 'Enter the username of the person who returned/claimed this item. Both of you will earn reputation points!',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location_lat'].required = False
        self.fields['location_lng'].required = False
        self.fields['claim_proof'].required = False
        self.fields['claimed_by_username'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        claim_proof = cleaned_data.get('claim_proof')
        claimed_by_username = cleaned_data.get('claimed_by_username')
        
        # If username is provided, proof is required
        if claimed_by_username and not claim_proof and not self.instance.claim_proof:
            raise forms.ValidationError('Proof of claim is required when providing a username.')
        
        # If username is provided, validate it exists
        if claimed_by_username:
            from users.models import User
            try:
                User.objects.get(username=claimed_by_username)
            except User.DoesNotExist:
                raise forms.ValidationError(f'User with username "{claimed_by_username}" does not exist.')
        
        return cleaned_data
    
    def save(self, commit=True):
        item = super().save(commit=False)
        claimed_by_username = self.cleaned_data.get('claimed_by_username')
        
        # Update status to claimed if proof is uploaded
        if self.cleaned_data.get('claim_proof') or item.claim_proof:
            item.status = 'claimed'
            
            # Award reputation points if username is provided and this is the first time
            if claimed_by_username and claimed_by_username != item.claimed_by_username:
                from users.models import User
                from messaging.models import ItemReturn
                
                try:
                    other_user = User.objects.get(username=claimed_by_username)
                    
                    # Check if not already awarded for this item
                    if not hasattr(item, 'return_record'):
                        # Award points
                        RETURN_POINTS = 10
                        item.user.reputation_points += RETURN_POINTS
                        other_user.reputation_points += RETURN_POINTS
                        item.user.save()
                        other_user.save()
                        
                        # Create return record
                        if commit:
                            item.save()
                            ItemReturn.objects.create(
                                item=item,
                                owner=item.user,
                                returner=other_user
                            )
                            return item
                except User.DoesNotExist:
                    pass
        
        if commit:
            item.save()
        return item
