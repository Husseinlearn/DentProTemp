from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


# Create your models here.

# --------------------------------------------------------------------
# Custom :  بيانات المستخدم الاساسية ويدعم إضافة خصائص إضافية
# --------------------------------------------------------------------
class CustomUser(AbstractUser):
    """مستخدم مخصص لدعم التوسعة والأدوار"""
    USER_TYPE_CHOICES = [
    ('admin', 'Admin'),
    ('doctor', 'Doctor'),
    ('receptionist', 'Receptionist'),
    ('assistant', 'Assistant'),
    ('manager', 'Manager'),
]

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES,null=True,)
    # is_verified = models.BooleanField(default=False) # This field is for email verification and will be added later.
    is_archived = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.get_full_name() or self.username
    

# --------------------------------------------------------------------
# Role : نموذج الأدوار (مثل: مدير، طبيب، موظف استقبال...)
# --------------------------------------------------------------------
class Role(models.Model):
    """نموذج الأدوار (مثل: مدير، طبيب، موظف استقبال...)"""
    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        DENTIST = 'dentist', _('Dentist')
        RECEPTIONIST = 'receptionist', _('Receptionist')
        ASSISTANT = 'assistant', _('Assistant')
        MANAGER = 'manager', _('Manager')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=RoleChoices.choices, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_name_display()

# --------------------------------------------------------------------
# UserRole: علاقة المستخدم بالأدوار
# --------------------------------------------------------------------
class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

# --------------------------------------------------------------------
# UserProfile: معلومات إضافية للمستخدم
# --------------------------------------------------------------------
class UserProfile(models.Model):
    # class GenderChoices(models.TextChoices):
    #     MALE = 'male', _('Male')
    #     FEMALE = 'female', _('Female')
    #     # choices=GenderChoices.choices,
    #     # default=GenderChoices.MALE,
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    birth_date = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Profile"

# --------------------------------------------------------------------
# Doctor: الجدول الخاص بالأطباء
# --------------------------------------------------------------------
class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    revenue_share = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # نسبة المشاركة من الإيرادات
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization or 'No Specialization'}"
    def get_full_name(self):
        return self.user.get_full_name()