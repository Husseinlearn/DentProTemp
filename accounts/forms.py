from django import forms
from .models import CustomUser, Doctor, UserProfile, Clinic

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['user', 'specialization', 'license_number', 'revenue_share']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'revenue_share': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class EmployeeCreateForm(forms.Form):
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@dentpro.com'})
    )
    username = forms.CharField(
        label="اسم المستخدم",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'})
    )
    first_name = forms.CharField(
        label="الاسم الأول",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول والثاني والجد'})
    )
    last_name = forms.CharField(
        label="الاسم الأخير",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العائلة'})
    )
    user_type = forms.ChoiceField(
        label="نوع الموظف",
        choices=[
            ('doctor', 'طبيب'),
            ('receptionist', 'موظف استقبال'),
            ('assistant', 'مساعد طبيب'),
            ('manager', 'مدير'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleDoctorFields(this.value)'})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    phone = forms.CharField(
        label="رقم الهاتف",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05xxxxxxxx'})
    )
    gender = forms.ChoiceField(
        label="الجنس",
        choices=[
            ('male', 'ذكر'),
            ('female', 'أنثى'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    birth_date = forms.DateField(
        label="تاريخ الميلاد",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    address = forms.CharField(
        label="العنوان",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Doctor specific fields
    specialization = forms.CharField(
        label="التخصص الطبي",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: تقويم أسنان'})
    )
    license_number = forms.CharField(
        label="رقم ترخيص مزاولة المهنة",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    revenue_share = forms.DecimalField(
        label="نسبة المشاركة من الإيرادات (%)",
        required=False,
        max_digits=5,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل بالفعل.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("اسم المستخدم هذا مستخدم بالفعل.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        user_type = cleaned_data.get('user_type')

        if password != password_confirm:
            self.add_error('password_confirm', "كلمتا المرور غير متطابقتين.")

        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')
        full_name = f"{first_name.strip()} {last_name.strip()}"
        if len(full_name.split()) < 4:
            self.add_error('first_name', "الاسم الكامل يجب أن يتكون من أربع كلمات على الأقل (الاسم الأول + اسم الأب والجد + الاسم الأخير).")

        if user_type == 'doctor':
            license_number = cleaned_data.get('license_number')
            if not license_number:
                self.add_error('license_number', "رقم الترخيص مطلوب للأطباء.")
        return cleaned_data


class EmployeeUpdateForm(forms.Form):
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label="الاسم الأول",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="الاسم الأخير",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    user_type = forms.ChoiceField(
        label="نوع الموظف",
        choices=[
            ('doctor', 'طبيب'),
            ('receptionist', 'موظف استقبال'),
            ('assistant', 'مساعد طبيب'),
            ('manager', 'مدير'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleDoctorFields(this.value)'})
    )
    
    phone = forms.CharField(
        label="رقم الهاتف",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        label="الجنس",
        choices=[
            ('male', 'ذكر'),
            ('female', 'أنثى'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    birth_date = forms.DateField(
        label="تاريخ الميلاد",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    address = forms.CharField(
        label="العنوان",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    specialization = forms.CharField(
        label="التخصص الطبي",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    license_number = forms.CharField(
        label="رقم ترخيص مزاولة المهنة",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    revenue_share = forms.DecimalField(
        label="نسبة المشاركة من الإيرادات (%)",
        required=False,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    password = forms.CharField(
        label="كلمة المرور الجديدة (اختياري)",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'اتركها فارغة لعدم التغيير'})
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.user_instance.pk).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل لمستخدم آخر.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')
        full_name = f"{first_name.strip()} {last_name.strip()}"
        if len(full_name.split()) < 4:
            self.add_error('first_name', "الاسم الكامل يجب أن يتكون من أربع كلمات على الأقل (الاسم الأول + اسم الأب والجد + الاسم الأخير).")

        if user_type == 'doctor':
            license_number = cleaned_data.get('license_number')
            if not license_number:
                self.add_error('license_number', "رقم الترخيص مطلوب للأطباء.")
        return cleaned_data


class UserProfileForm(forms.Form):
    first_name = forms.CharField(
        label="الاسم الأول",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label="الاسم الأخير",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="البريد الإلكتروني",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label="رقم الهاتف",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        label="الجنس",
        choices=[
            ('male', 'ذكر'),
            ('female', 'أنثى'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    birth_date = forms.DateField(
        label="تاريخ الميلاد",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    address = forms.CharField(
        label="العنوان",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    password = forms.CharField(
        label="كلمة المرور الجديدة (اختياري)",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'اتركها فارغة لعدم التغيير'})
    )
    password_confirm = forms.CharField(
        label="تأكيد كلمة المرور الجديدة",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.user_instance.pk).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل لمستخدم آخر.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password or password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "كلمتا المرور غير متطابقتين.")
                
        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')
        full_name = f"{first_name.strip()} {last_name.strip()}"
        if len(full_name.split()) < 4:
            self.add_error('first_name', "الاسم الكامل يجب أن يتكون من أربع كلمات على الأقل (الاسم الأول + اسم الأب والجد + الاسم الأخير).")
            
        return cleaned_data


class ClinicRegisterForm(forms.Form):
    clinic_name = forms.CharField(
        label="اسم العيادة",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: عيادة الأمل لطب الأسنان'})
    )
    clinic_email = forms.EmailField(
        label="البريد الإلكتروني للعيادة (اختياري)",
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'clinic@example.com'})
    )
    clinic_phone = forms.CharField(
        label="رقم هاتف العيادة (اختياري)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '05xxxxxxxx'})
    )
    manager_first_name = forms.CharField(
        label="الاسم الأول والثاني والجد للمدير",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول + الأب والجد'})
    )
    manager_last_name = forms.CharField(
        label="الاسم الأخير للمدير (اسم العائلة)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'العائلة'})
    )
    manager_email = forms.EmailField(
        label="البريد الإلكتروني للمدير (لتسجيل الدخول)",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'manager@example.com'})
    )
    password = forms.CharField(
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    password_confirm = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

    def clean_manager_email(self):
        email = self.cleaned_data.get('manager_email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("هذا البريد الإلكتروني مسجل بالفعل لمستخدم آخر.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            self.add_error('password_confirm', "كلمتا المرور غير متطابقتين.")

        first_name = cleaned_data.get('manager_first_name', '')
        last_name = cleaned_data.get('manager_last_name', '')
        full_name = f"{first_name.strip()} {last_name.strip()}"
        if len(full_name.split()) < 4:
            self.add_error('manager_first_name', "الاسم الكامل للمدير يجب أن يتكون من أربع كلمات على الأقل.")

        return cleaned_data


class ClinicSettingsForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ['name', 'phone', 'email', 'address', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
