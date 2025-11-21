from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text="Use your school email",
        widget=forms.EmailInput(attrs={'placeholder': 'your.email@school.edu'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'id': 'id_role', 'onchange': 'toggleStudentId()'})
    )
    student_id = forms.CharField(
        max_length=50, 
        required=False, 
        help_text="Your student ID number (e.g., 2024-12345)",
        widget=forms.TextInput(attrs={'placeholder': '2024-12345', 'id': 'id_student_id'})
    )
    first_name = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Juan'})
    )
    last_name = forms.CharField(
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Dela Cruz'})
    )
    age = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Age', 'min': '1', 'max': '120'})
    )
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Your address', 'rows': 3})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'student_id', 'first_name', 'last_name', 'age', 'birthday', 'address', 'profile_picture', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password fields
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password'})
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        role = self.cleaned_data.get('role')
        
        # Only require student_id if role is student
        if role == 'student' and not student_id:
            raise forms.ValidationError("Student ID is required for students.")
        
        if student_id and User.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("This student ID is already registered.")
        return student_id
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        student_id = cleaned_data.get('student_id')
        
        # If role is not student, clear student_id
        if role != 'student':
            cleaned_data['student_id'] = None
        
        return cleaned_data


class StudentLoginForm(AuthenticationForm):
    username = forms.CharField(label="Email", max_length=254)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Try to find user by email first
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                # Try student_id
                try:
                    user_obj = User.objects.get(student_id=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass  # Will use username as-is
            
            # Now authenticate with the resolved username
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'})
        }


class EditProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Required only if changing password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave blank to keep current password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        current_password = cleaned_data.get('current_password')
        
        # If trying to change password
        if new_password or confirm_password:
            if not current_password:
                raise forms.ValidationError("Current password is required to set a new password.")
            
            if not self.instance.check_password(current_password):
                raise forms.ValidationError("Current password is incorrect.")
            
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match.")
        
        return cleaned_data
