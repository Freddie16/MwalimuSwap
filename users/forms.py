from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from swaps.models import County, SubCounty, Ward
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, HTML

# Define subject choices based on Kenyan CBC
SUBJECT_CHOICES = {
    'PRE_PRIMARY': [
        ('Language Activities', 'Language Activities'),
        ('Mathematical Activities', 'Mathematical Activities'),
        ('Environmental Activities', 'Environmental Activities'),
        ('Psychomotor and Creative Activities', 'Psychomotor and Creative Activities'),
        ('Religious Education Activities', 'Religious Education Activities'),
    ],
    'LOWER_PRIMARY': [
        ('Literacy', 'Literacy'),
        ('Kiswahili Language Activities', 'Kiswahili Language Activities'),
        ('Kenya Sign Language', 'Kenya Sign Language (for learners who are deaf)'),
        ('English Language Activities', 'English Language Activities'),
        ('Indigenous Language Activities', 'Indigenous Language Activities'),
        ('Mathematical Activities', 'Mathematical Activities'),
        ('Environmental Activities', 'Environmental Activities'),
        ('Hygiene and Nutrition Activities', 'Hygiene and Nutrition Activities'),
        ('Religious Education Activities', 'Religious Education Activities'),
        ('Movement and Creative Activities', 'Movement and Creative Activities'),
    ],
    'UPPER_PRIMARY': [
        ('English', 'English'),
        ('Kiswahili', 'Kiswahili'),
        ('Kenya Sign Language', 'Kenya Sign Language (for learners who are deaf)'),
        ('Home Science', 'Home Science'),
        ('Agriculture', 'Agriculture'),
        ('Science and Technology', 'Science and Technology'),
        ('Mathematics', 'Mathematics'),
        ('Religious Education (CRE)', 'Christian Religious Education (CRE)'),
        ('Religious Education (IRE)', 'Islamic Religious Education (IRE)'),
        ('Religious Education (HRE)', 'Hindu Religious Education (HRE)'),
        ('Creative Arts', 'Creative Arts'),
        ('Physical and Health Education', 'Physical and Health Education'),
        ('Social Studies', 'Social Studies'),
        ('Foreign Languages (Arabic)', 'Arabic (Optional)'),
        ('Foreign Languages (French)', 'French (Optional)'),
        ('Foreign Languages (German)', 'German (Optional)'),
        ('Foreign Languages (Mandarin)', 'Mandarin (Optional)'),
    ],
    'JUNIOR_SECONDARY': [
        # Core Subjects
        ('English', 'English'),
        ('Kiswahili', 'Kiswahili'),
        ('Kenya Sign Language', 'Kenya Sign Language (for learners who are deaf)'),
        ('Mathematics', 'Mathematics'),
        ('Integrated Science', 'Integrated Science'),
        ('Health Education', 'Health Education'),
        ('Pre-Technical and Pre-Career Education', 'Pre-Technical and Pre-Career Education'),
        ('Social Studies', 'Social Studies'),
        ('Religious Education (CRE)', 'Christian Religious Education (CRE)'),
        ('Religious Education (IRE)', 'Islamic Religious Education (IRE)'),
        ('Religious Education (HRE)', 'Hindu Religious Education (HRE)'),
        ('Business Studies', 'Business Studies'),
        ('Agriculture', 'Agriculture'),
        ('Life Skills Education', 'Life Skills Education'),
        ('Sports and Physical Education', 'Sports and Physical Education'),
        # Optional Subjects
        ('Visual Arts', 'Visual Arts (Optional)'),
        ('Performing Arts', 'Performing Arts (Optional)'),
        ('Home Science', 'Home Science (Optional)'),
        ('Computer Science', 'Computer Science (Optional)'),
        ('Foreign Languages (German)', 'German (Optional)'),
        ('Foreign Languages (French)', 'French (Optional)'),
        ('Foreign Languages (Mandarin)', 'Mandarin (Optional)'),
        ('Foreign Languages (Arabic)', 'Arabic (Optional)'),
        ('Indigenous Languages', 'Indigenous Languages (Optional)'),
    ],
    'SENIOR_SECONDARY': [
        # Arts and Sports Science Pathway
        ('Legal and Ethical Issues in Arts', 'Legal and Ethical Issues in Arts (Arts Track)'),
        ('Communication Skills', 'Communication Skills (Arts Track)'),
        ('Performing Arts (Music)', 'Music (Performing Arts)'),
        ('Performing Arts (Dance)', 'Dance (Performing Arts)'),
        ('Performing Arts (Theatre and Elocution)', 'Theatre and Elocution (Performing Arts)'),
        ('Visual and Applied Arts (Fine Art)', 'Fine Art (Visual and Applied Arts)'),
        ('Visual and Applied Arts (Applied Art)', 'Applied Art (Visual and Applied Arts)'),
        ('Visual and Applied Arts (Time Based Media)', 'Time Based Media (Visual and Applied Arts)'),
        ('Visual and Applied Arts (Crafts)', 'Crafts (Visual and Applied Arts)'),
        ('Human Physiology, Anatomy and Nutrition', 'Human Physiology, Anatomy and Nutrition (Sports Science Track)'),
        ('Sports Ethics', 'Sports Ethics (Sports Science Track)'),
        ('Ball Games', 'Ball Games (Sports Science, Optional)'),
        ('Athletics', 'Athletics (Sports Science, Optional)'),
        ('Indoor Games', 'Indoor Games (Sports Science, Optional)'),
        ('Gymnastics', 'Gymnastics (Sports Science, Optional)'),
        ('Water Sports', 'Water Sports (Sports Science, Optional)'),
        ('Boxing', 'Boxing (Sports Science, Optional)'),
        ('Martial Arts', 'Martial Arts (Sports Science, Optional)'),
        ('Outdoor Pursuits', 'Outdoor Pursuits (Sports Science, Optional)'),
        ('Advanced Physical Education', 'Advanced Physical Education (Sports Science, Optional)'),
        # Social Sciences Pathway
        ('History and Citizenship', 'History and Citizenship (Humanities)'),
        ('Geography', 'Geography (Humanities)'),
        ('Christian Religious Education', 'Christian Religious Education (Humanities)'),
        ('Islamic Religious Education', 'Islamic Religious Education (Humanities)'),
        ('Hindu Religious Education', 'Hindu Religious Education (Humanities)'),
        ('English Language', 'English Language (Languages)'),
        ('Literature in English', 'Literature in English (Languages)'),
        ('Lugha ya Kiswahili', 'Lugha ya Kiswahili (Languages)'),
        ('Fasihi ya Kiswahili', 'Fasihi ya Kiswahili (Languages)'),
        ('Kenya Sign Language', 'Kenya Sign Language (Languages)'),
        ('Indigenous Languages', 'Indigenous Languages (Languages)'),
        ('Arabic', 'Arabic (Languages)'),
        ('French', 'French (Languages)'),
        ('German', 'German (Languages)'),
        ('Mandarin', 'Mandarin (Languages)'),
        ('Business Studies', 'Business Studies (Business Studies)'),
        ('Mathematics', 'Mathematics (Business Studies)'),
        # STEM Pathway
        ('Community Service', 'Community Service (STEM)'),
        ('Physical Education', 'Physical Education (STEM)'),
        ('ICT', 'ICT (STEM)'),
        ('Agriculture', 'Agriculture (STEM, Optional)'),
        ('Computer Science', 'Computer Science (STEM, Optional)'),
        ('Foods and Nutrition', 'Foods and Nutrition (STEM, Optional)'),
        ('Home Management', 'Home Management (STEM, Optional)'),
        ('Mathematics', 'Mathematics (STEM, Optional)'),
        ('Physics', 'Physics (STEM, Optional)'),
        ('Chemistry', 'Chemistry (STEM, Optional)'),
        ('Biology', 'Biology (STEM, Optional)'),
        ('Agricultural Technology', 'Agricultural Technology (STEM, Optional)'),
        ('Geosciences Technology', 'Geosciences Technology (STEM, Optional)'),
        ('Marine and Fisheries Technology', 'Marine and Fisheries Technology (STEM, Optional)'),
        ('Aviation Technology', 'Aviation Technology (STEM, Optional)'),
        ('Garment Making and Interior Design', 'Garment Making and Interior Design (STEM, Optional)'),
        ('Leather Work', 'Leather Work (STEM, Optional)'),
        ('Culinary Arts', 'Culinary Arts (STEM, Optional)'),
        ('Hair Dressing and Beauty Therapy', 'Hair Dressing and Beauty Therapy (STEM, Optional)'),
        ('Wood Technology', 'Wood Technology (STEM, Optional)'),
        ('Electrical Technology', 'Electrical Technology (STEM, Optional)'),
        ('Metal Technology', 'Metal Technology (STEM, Optional)'),
        ('Power Mechanics', 'Power Mechanics (STEM, Optional)'),
        ('Clothing Technology', 'Clothing Technology (STEM, Optional)'),
        ('Construction Technology', 'Construction Technology (STEM, Optional)'),
        ('Media Technology', 'Media Technology (STEM, Optional)'),
        ('Electronics Technology', 'Electronics Technology (STEM, Optional)'),
        ('Welding and Fabrication', 'Welding and Fabrication (STEM, Optional)'),
        ('Mechatronic', 'Mechatronic (STEM, Optional)'),
        ('Tourism and Travel', 'Tourism and Travel (STEM, Optional)'),
        ('Air Conditioning and Refrigeration', 'Air Conditioning and Refrigeration (STEM, Optional)'),
        ('Animal Keeping', 'Animal Keeping (STEM, Optional)'),
        ('Exterior Design and Landscaping', 'Exterior Design and Landscaping (STEM, Optional)'),
        ('Building Construction', 'Building Construction (STEM, Optional)'),
        ('Photography', 'Photography (STEM, Optional)'),
        ('Graphic Designing and Animation', 'Graphic Designing and Animation (STEM, Optional)'),
        ('Food and Beverage', 'Food and Beverage (STEM, Optional)'),
        ('Motor Vehicle Mechanics', 'Motor Vehicle Mechanics (STEM, Optional)'),
        ('Carpentry and Joinery', 'Carpentry and Joinery (STEM, Optional)'),
        ('Fire Fighting', 'Fire Fighting (STEM, Optional)'),
        ('Metalwork', 'Metalwork (STEM, Optional)'),
        ('Electricity', 'Electricity (STEM, Optional)'),
        ('Land Surveying', 'Land Surveying (STEM, Optional)'),
        ('Science Laboratory Technology', 'Science Laboratory Technology (STEM, Optional)'),
        ('Printing Technology', 'Printing Technology (STEM, Optional)'),
        ('Crop Production', 'Crop Production (STEM, Optional)')
    ],
    'TERTIARY': [
        ('Education', 'Education'),
        ('Computer Science', 'Computer Science'),
        ('Engineering', 'Engineering'),
        ('Medicine', 'Medicine'),
        ('Business Administration', 'Business Administration'),
        ('Law', 'Law'),
        ('Agriculture', 'Agriculture'),
        ('Environmental Science', 'Environmental Science'),
        ('Hospitality and Tourism', 'Hospitality and Tourism'),
        ('Journalism and Mass Communication', 'Journalism and Mass Communication'),
        ('Creative Arts and Design', 'Creative Arts and Design'),
        ('Social Sciences', 'Social Sciences'),
        ('Pure Sciences', 'Pure Sciences'),
        ('Applied Sciences', 'Applied Sciences'),
        ('Vocational Training', 'Vocational Training'),
        ('Technical Training', 'Technical Training'),
        ('Other', 'Other (Please Specify)'),
    ]
}

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        help_text="Your full name (e.g., John Doe). Two names required."
    )
    phone_number = forms.CharField(
        max_length=10,
        required=True,
        help_text="10-digit phone number (e.g., 0712345678)."
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + (
            'full_name',
            'phone_number',
            'email',
        )

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and len(full_name.split()) < 2:
            raise forms.ValidationError("Please enter your full name (at least two names).")
        return full_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(phone_number) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control rounded-md'),
            Field('email', css_class='form-control rounded-md'),
            Field('full_name', css_class='form-control rounded-md'),
            Field('phone_number', css_class='form-control rounded-md'),
            Field('password', css_class='form-control rounded-md'),
            Field('password2', css_class='form-control rounded-md'),
            Submit('submit', 'Register', css_class='btn btn-primary w-full rounded-md mt-4')
        )


class CustomUserChangeForm(UserChangeForm):
    current_county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label="Select your Current County",
        required=False,
        label="Current County"
    )
    current_subcounty = forms.ModelChoiceField(
        queryset=SubCounty.objects.none(),
        empty_label="Select your Current Sub-county",
        required=False,
        label="Current Sub-county"
    )
    current_ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(),
        empty_label="Select your Current Ward",
        required=False,
        label="Current Ward"
    )
    swap_to_county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label="Select Desired Swap County",
        required=False,
        label="Desired Swap County"
    )
    swap_to_subcounty = forms.ModelChoiceField(
        queryset=SubCounty.objects.none(),
        empty_label="Select Desired Swap Sub-county",
        required=False,
        label="Desired Swap Sub-county"
    )
    swap_to_ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(),
        empty_label="Select Desired Swap Ward",
        required=False,
        label="Desired Swap Ward"
    )
    subjects = forms.MultipleChoiceField(
        choices=SUBJECT_CHOICES['SENIOR_SECONDARY'],  # Default choices, will be updated dynamically
        widget=forms.SelectMultiple(attrs={'class': 'form-control rounded-md'}),
        required=False,
        label="Subjects Taught"
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'full_name',
            'phone_number',
            'profile_picture',
            'school_type',
            'subjects',
            'current_county',
            'current_subcounty',
            'current_ward',
            'swap_to_county',
            'swap_to_subcounty',
            'swap_to_ward',
            'is_profile_complete',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set subject choices based on school_type
        if self.instance and self.instance.school_type:
            self.fields['subjects'].choices = SUBJECT_CHOICES.get(self.instance.school_type, [])
            # If subjects field has initial data (comma-separated string), convert it to a list
            if self.instance.subjects and isinstance(self.instance.subjects, str):
                self.initial['subjects'] = [s.strip() for s in self.instance.subjects.split(',')]
        else:
            # If no school_type is set, default to an empty list or a general category
            self.fields['subjects'].choices = [] # Or SUBJECT_CHOICES['SENIOR_SECONDARY'] as a fallback

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('full_name', css_class='form-group col-md-6 mb-0'),
                Column('phone_number', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('profile_picture', css_class='form-control-file rounded-md'),
            Field('school_type', css_class='form-control rounded-md'),
            Field('subjects', css_class='form-control rounded-md'),
            HTML('<h4 class="text-lg font-semibold text-gray-700 mt-6 mb-3">Current Location</h4>'),
            Row(
                Column('current_county', css_class='form-group col-md-4 mb-0'),
                Column('current_subcounty', css_class='form-group col-md-4 mb-0'),
                Column('current_ward', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            HTML('<h4 class="text-lg font-semibold text-gray-700 mt-6 mb-3">Desired Swap Location</h4>'),
            Row(
                Column('swap_to_county', css_class='form-group col-md-4 mb-0'),
                Column('swap_to_subcounty', css_class='form-group col-md-4 mb-0'),
                Column('swap_to_ward', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Field('is_profile_complete', css_class='form-check-input'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary w-full rounded-md mt-4')
        )

        # Populate initial querysets for subcounties and wards if instance exists
        if self.instance.pk:
            if self.instance.current_county:
                self.fields['current_subcounty'].queryset = self.instance.current_county.subcounties.all().order_by('name')
            if self.instance.current_subcounty:
                self.fields['current_ward'].queryset = self.instance.current_subcounty.wards.all().order_by('name')
            if self.instance.swap_to_county:
                self.fields['swap_to_subcounty'].queryset = self.instance.swap_to_county.subcounties.all().order_by('name')
            if self.instance.swap_to_subcounty:
                self.fields['swap_to_ward'].queryset = self.instance.swap_to_subcounty.wards.all().order_by('name')

    def clean_subjects(self):
        subjects = self.cleaned_data.get('subjects')
        if subjects:
            return ', '.join(subjects)  # Convert list to comma-separated string for TextField
        return ''


class ProfileStep1Form(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone_number']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., 0712345678'}),
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and len(full_name.split()) < 2:
            raise forms.ValidationError("Please enter your full name (at least two names).")
        return full_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(phone_number) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('full_name', css_class='form-control rounded-md'),
            Field('phone_number', css_class='form-control rounded-md'),
            Submit('submit', 'Next: School Details', css_class='btn btn-primary w-full rounded-md mt-4')
        )


class ProfileStep2SchoolForm(forms.ModelForm):
    school_type = forms.ChoiceField(
        choices=[('', 'Select your current school type')] + list(CustomUser.SCHOOL_TYPE_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-control rounded-md',
            'id': 'id_school_type'  # Ensure this ID matches your JavaScript
        }),
        required=True,
        label="School Type",
    )
    
    subjects = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control rounded-md',
            'id': 'id_subjects'  # Ensure this ID matches your JavaScript
        }),
        required=True,
        label="Subjects Taught"
    )

    class Meta:
        model = CustomUser
        fields = ['school_type', 'subjects']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize with default choices
        self.fields['subjects'].choices = SUBJECT_CHOICES.get(
            self.instance.school_type if self.instance and self.instance.school_type else 'SENIOR_SECONDARY',
            []
        )
        
        # Convert comma-separated subjects to list for initial data
        if self.instance and self.instance.subjects and isinstance(self.instance.subjects, str):
            self.initial['subjects'] = [s.strip() for s in self.instance.subjects.split(',')]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('school_type', css_class='form-control rounded-md'),
            Field('subjects', css_class='form-control rounded-md'),
            Submit('submit', 'Next: Current Location', css_class='btn btn-primary w-full rounded-md mt-4')
        )

    def clean_subjects(self):
        subjects = self.cleaned_data.get('subjects')
        if subjects:
            return ', '.join(subjects)  # Convert list to comma-separated string
        return ''


class ProfileStep3LocationForm(forms.ModelForm):
    current_county = forms.ModelChoiceField(
        queryset=County.objects.all(),
        empty_label="Select your Current County",
        widget=forms.Select(attrs={'id': 'id_current_county'})
    )
    current_subcounty = forms.ModelChoiceField(
        queryset=SubCounty.objects.none(),
        empty_label="Select your Current Sub-county",
        widget=forms.Select(attrs={'id': 'id_current_subcounty'})
    )
    current_ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(),
        empty_label="Select your Current Ward",
        widget=forms.Select(attrs={'id': 'id_current_ward'})
    )

    class Meta:
        model = CustomUser
        fields = ['current_county', 'current_subcounty', 'current_ward']

    def __init__(self, *args, **kwargs):
        counties = kwargs.pop('counties', None)
        super().__init__(*args, **kwargs)

        if counties is not None:
            self.fields['current_county'].queryset = counties

    # Handle subcounty queryset based on POSTed data or instance
        if 'current_county' in self.data:
            try:
                county_id = int(self.data.get('current_county'))
                self.fields['current_subcounty'].queryset = SubCounty.objects.filter(county_id=county_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['current_subcounty'].queryset = SubCounty.objects.none()
        elif self.instance and self.instance.current_county:
            self.fields['current_subcounty'].queryset = SubCounty.objects.filter(
            county=self.instance.current_county
        ).order_by('name')

        if 'current_subcounty' in self.data:
            try:
                subcounty_id = int(self.data.get('current_subcounty'))
                self.fields['current_ward'].queryset = Ward.objects.filter(subcounty_id=subcounty_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['current_ward'].queryset = Ward.objects.none()
        elif self.instance and self.instance.current_subcounty:
            self.fields['current_ward'].queryset = Ward.objects.filter(
                subcounty=self.instance.current_subcounty
        ).order_by('name')
    def clean(self):
        cleaned_data = super().clean()
        county = cleaned_data.get('current_county')
        subcounty = cleaned_data.get('current_subcounty')
        ward = cleaned_data.get('current_ward')

        if not (county and subcounty and ward):
            raise forms.ValidationError("Please select County, Sub-county, and Ward.")
        return cleaned_data
class ProfileStep4SwapToForm(forms.ModelForm):
    swap_to_county = forms.ModelChoiceField(
        queryset=County.objects.all().order_by('name'),
        empty_label="Select Desired Swap County",
        required=True,
        label="Desired Swap County",
        widget=forms.Select(attrs={'id': 'id_swap_to_county', 'class': 'form-control rounded-md'})
    )
    swap_to_subcounty = forms.ModelChoiceField(
        queryset=SubCounty.objects.none(),
        empty_label="Select Desired Swap Sub-county",
        required=True,
        label="Desired Swap Sub-county",
        widget=forms.Select(attrs={'id': 'id_swap_to_subcounty', 'class': 'form-control rounded-md'})
    )
    swap_to_ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(),
        empty_label="Select Desired Swap Ward",
        required=True,
        label="Desired Swap Ward",
        widget=forms.Select(attrs={'id': 'id_swap_to_ward', 'class': 'form-control rounded-md'})
    )

    class Meta:
        model = CustomUser
        fields = ['swap_to_county', 'swap_to_subcounty', 'swap_to_ward']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('swap_to_county', css_class='form-control rounded-md'),
            Field('swap_to_subcounty', css_class='form-control rounded-md'),
            Field('swap_to_ward', css_class='form-control rounded-md'),
            Submit('submit', 'Complete Profile', css_class='btn btn-success w-full rounded-md mt-4')
        )

        # Dynamically set querysets for dependent fields based on instance or POST data
        # This block is crucial for backend validation
        # Prioritize POST data for validation, then instance data for initial display
        
        # For swap_to_subcounty
        if 'swap_to_county' in self.data:
            try:
                county_id = int(self.data.get('swap_to_county'))
                self.fields['swap_to_subcounty'].queryset = SubCounty.objects.filter(county_id=county_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['swap_to_subcounty'].queryset = SubCounty.objects.none() # Invalid input, reset queryset
        elif self.instance.pk and self.instance.swap_to_county:
            self.fields['swap_to_subcounty'].queryset = self.instance.swap_to_county.subcounties.all().order_by('name')
        else:
            self.fields['swap_to_subcounty'].queryset = SubCounty.objects.none() # Default empty

        # For swap_to_ward
        if 'swap_to_subcounty' in self.data:
            try:
                subcounty_id = int(self.data.get('swap_to_subcounty'))
                self.fields['swap_to_ward'].queryset = Ward.objects.filter(subcounty_id=subcounty_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['swap_to_ward'].queryset = Ward.objects.none() # Invalid input, reset queryset
        elif self.instance.pk and self.instance.swap_to_subcounty:
            self.fields['swap_to_ward'].queryset = self.instance.swap_to_subcounty.wards.all().order_by('name')
        else:
            self.fields['swap_to_ward'].queryset = Ward.objects.none() # Default empty

