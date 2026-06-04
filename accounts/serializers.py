from rest_framework import serializers
from .models import (
    CustomUser, UserProfile,
    Role, UserRole,
    Doctor
)
from django.contrib.auth.password_validation import validate_password



class UserProfileNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'gender', 'birth_date', 'address', 'image']
    
    def validate_gender(self, value):
        allowed = ['ذكر', 'أنثى', 'male', 'female']
        if value.strip().lower() not in [v.lower() for v in allowed]:
            raise serializers.ValidationError(
                "الجنس يجب أن يكون أحد القيم التالية فقط: 'ذكر', 'أنثى', 'male', 'female'."
            )
        return value.strip()


class DoctorNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['specialization', 'license_number', 'revenue_share']


class UnifiedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    profile = UserProfileNestedSerializer()
    doctor_profile = DoctorNestedSerializer(required=False)
    
    user_type = serializers.ChoiceField(choices=[
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
        ('assistant', 'Assistant'),
        ('manager', 'Manager'),
        ('doctor', 'Doctor')
    ])

    class Meta:
        model = CustomUser
        fields = [
                    'id',
                    'username', 
                    'email', 
                    'first_name',
                    'last_name',
                    'user_type', 
                    'password', 
                    'password2', 
                    'profile', 
                    'doctor_profile'
                    ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "كلمتا المرور غير متطابقتين."})

        if attrs.get('user_type') == 'doctor' and 'doctor_profile' not in self.initial_data:
            raise serializers.ValidationError({"DoctorProfile": "بيانات الطبيب مطلوبة لنوع المستخدم 'doctor'."})
        return attrs

    def validate(self, data):
        # اجمع الاسم الأول والأخير بعد إزالة الفراغات من الطرفين
        full_name = f"{data.get('first_name', '').strip()} {data.get('last_name', '').strip()}"
        words = full_name.split()

        # تحقق من أن الاسم يتكون من 4 كلمات على الأقل
        if len(words) < 4:
            raise serializers.ValidationError("الاسم الكامل يجب أن يتكون من أربع كلمات على الأقل (الاسم الأول + الاسم الأخير).")

        return data
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        doctor_data = validated_data.pop('doctor_profile', None)
        password = validated_data.pop('password')
        validated_data.pop('password2')

        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, **profile_data)

        if validated_data['user_type'] == 'doctor' and doctor_data:
            Doctor.objects.create(user=user, **doctor_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        doctor_data = validated_data.pop('doctor_profile', {})

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.user_type = validated_data.get('user_type', instance.user_type)

        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])

        instance.save()

        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        if instance.user_type == 'doctor' and hasattr(instance, 'doctor_profile'):
            doctor = instance.doctor_profile
            for attr, value in doctor_data.items():
                setattr(doctor, attr, value)
            doctor.save()

        return instance
    
class DoctorProfileSerializer(serializers.ModelSerializer):
    """لعرض بيانات الطبيب + المستخدم + البروفايل"""
    profile = UserProfileNestedSerializer(source='user.profile')
    
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username')
    user_type = serializers.CharField(source='user.user_type')

    class Meta:
        model = Doctor
        fields = [
            'id',
            'specialization',
            'license_number',
            'revenue_share',
            'username',
            'email',
            'first_name',
            'last_name',
            'user_type',
            'profile'
        ]
