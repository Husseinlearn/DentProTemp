import uuid
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, FormView, DeleteView, View, UpdateView
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import CustomUser, Doctor, UserProfile, Clinic
from .forms import (
    EmployeeCreateForm, EmployeeUpdateForm, UserProfileForm,
    ClinicRegisterForm, ClinicSettingsForm
)

class DoctorListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/doctor_list.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return CustomUser.objects.filter(
            clinic=self.request.user.clinic,
            user_type__in=['doctor', 'receptionist', 'assistant', 'manager', 'admin'],
            is_archived=False
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.request.user.clinic
        
        # الإحصائيات الحقيقية المفلترة بحسب العيادة الحالية فقط
        doctors_db = CustomUser.objects.filter(clinic=clinic, user_type='doctor', is_archived=False)
        receptionists_db = CustomUser.objects.filter(clinic=clinic, user_type='receptionist', is_archived=False)
        assistants_db = CustomUser.objects.filter(clinic=clinic, user_type='assistant', is_archived=False)
        managers_db = CustomUser.objects.filter(clinic=clinic, user_type='manager', is_archived=False)
        
        context['doctors_count'] = doctors_db.count()
        context['receptionists_count'] = receptionists_db.count()
        context['assistants_count'] = assistants_db.count()
        context['total_team_count'] = (
            doctors_db.count() + 
            receptionists_db.count() + 
            assistants_db.count() + 
            managers_db.count()
        )
        
        # بناء قائمة الموظفين الحقيقيين المسجلين في العيادة
        enriched_staff = []
        for user in self.get_queryset():
            phone = getattr(user, 'profile', None).phone if (hasattr(user, 'profile') and user.profile) else "غير محدد"
            joined_date = user.date_joined.strftime('%d-%m-%Y') if user.date_joined else "15-01-2022"
            
            specialty = ""
            if user.user_type == 'doctor':
                doc_profile = None
                if hasattr(user, 'doctor_profile'):
                    try:
                        doc_profile = user.doctor_profile.first()
                    except AttributeError:
                        doc_profile = user.doctor_profile
                elif hasattr(user, 'doctor'):
                    doc_profile = user.doctor
                
                specialty = doc_profile.specialization if doc_profile else "طب الأسنان العام"
            elif user.user_type == 'receptionist':
                specialty = "موظف استقبال"
            elif user.user_type == 'assistant':
                specialty = "مساعد طبيب"
            elif user.user_type == 'manager':
                specialty = "مدير العيادة"
            elif user.user_type == 'admin':
                specialty = "مسؤول النظام"
                
            initials = f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else user.username[0]}"
            if not initials:
                initials = "ع"
                
            is_active = user.is_active
            
            # إحصائيات حقيقية مبدئية (يمكنك تطويرها لاحقاً لربطها بجدول الحالات والمواعيد)
            patients_count = 0
            appointments_count = 0
            
            enriched_staff.append({
                'id': user.pk,
                'pk': user.pk,
                'full_name': user.get_full_name() or user.username,
                'user_type': user.user_type,
                'user_type_display': 'طبيب' if user.user_type == 'doctor' else 'موظف استقبال' if user.user_type == 'receptionist' else 'مساعد' if user.user_type == 'assistant' else 'مدير' if user.user_type == 'manager' else 'مسؤول',
                'specialty': specialty,
                'phone': phone,
                'email': user.email,
                'joined_date': joined_date,
                'is_active': is_active,
                'initials': initials,
                'patients_count': patients_count,
                'appointments_count': appointments_count,
            })
            
        # إرسال القائمة الحقيقية مباشرة بدون أي استبدال ببيانات وهمية
        context['staff_list'] = enriched_staff
            
        return context

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/doctor_detail.html'
    context_object_name = 'staff'
    pk_url_kwarg = 'pk'

    def get_queryset(self):
        return CustomUser.objects.filter(clinic=self.request.user.clinic)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user'] = user
        context['profile'] = getattr(user, 'profile', None)
        
        doc_profile = user.doctor_profile.first() if hasattr(user, 'doctor_profile') else None
        context['doctor_profile'] = doc_profile
        context['doctor'] = doc_profile if doc_profile else user
        return context

class DoctorCreateView(LoginRequiredMixin, FormView):
    template_name = 'accounts/doctor_form.html'
    form_class = EmployeeCreateForm
    success_url = reverse_lazy('accounts_web:doctor-list')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        # إنشاء المستخدم
        user = CustomUser.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data['email'],
            first_name=cleaned_data['first_name'],
            last_name=cleaned_data['last_name'],
            user_type=cleaned_data['user_type'],
            clinic=self.request.user.clinic
        )
        user.set_password(cleaned_data['password'])
        user.save()
        
        # إنشاء الملف الشخصي
        UserProfile.objects.create(
            user=user,
            phone=cleaned_data['phone'],
            gender=cleaned_data['gender'],
            birth_date=cleaned_data.get('birth_date'),
            address=cleaned_data.get('address')
        )
        
        # إنشاء ملف طبيب مخصص إذا كان نوع الحساب طبيباً
        if cleaned_data['user_type'] == 'doctor':
            Doctor.objects.create(
                user=user,
                specialization=cleaned_data.get('specialization'),
                license_number=cleaned_data.get('license_number'),
                revenue_share=cleaned_data.get('revenue_share') or 0.00
            )
            
        messages.success(self.request, "تم تسجيل الموظف بنجاح في النظام.")
        return super().form_valid(form)

class DoctorUpdateView(LoginRequiredMixin, FormView):
    template_name = 'accounts/doctor_form.html'
    form_class = EmployeeUpdateForm
    success_url = reverse_lazy('accounts_web:doctor-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.user_obj = CustomUser.objects.get(pk=self.kwargs['pk'], clinic=self.request.user.clinic)
        kwargs['user_instance'] = self.user_obj
        
        initial = {
            'email': self.user_obj.email,
            'first_name': self.user_obj.first_name,
            'last_name': self.user_obj.last_name,
            'user_type': self.user_obj.user_type,
        }
        
        profile = getattr(self.user_obj, 'profile', None)
        if profile:
            initial.update({
                'phone': profile.phone,
                'gender': profile.gender,
                'birth_date': profile.birth_date,
                'address': profile.address,
            })
            
        doc_profile = self.user_obj.doctor_profile.first() if hasattr(self.user_obj, 'doctor_profile') else None
        if doc_profile:
            initial.update({
                'specialization': doc_profile.specialization,
                'license_number': doc_profile.license_number,
                'revenue_share': doc_profile.revenue_share,
            })
            
        kwargs['initial'] = initial
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.user_obj
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user = self.user_obj
        
        user.email = cleaned_data['email']
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.user_type = cleaned_data['user_type']
        if cleaned_data.get('password'):
            user.set_password(cleaned_data['password'])
        user.save()
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = cleaned_data['phone']
        profile.gender = cleaned_data['gender']
        profile.birth_date = cleaned_data.get('birth_date')
        profile.address = cleaned_data.get('address')
        profile.save()
        
        if cleaned_data['user_type'] == 'doctor':
            doc_profile, created = Doctor.objects.get_or_create(user=user)
            doc_profile.specialization = cleaned_data.get('specialization')
            doc_profile.license_number = cleaned_data.get('license_number')
            doc_profile.revenue_share = cleaned_data.get('revenue_share') or 0.00
            doc_profile.save()
        else:
            if hasattr(user, 'doctor_profile'):
                user.doctor_profile.all().delete()
                
        messages.success(self.request, "تم تحديث بيانات الموظف بنجاح.")
        return redirect('accounts_web:doctor-list')

class DoctorDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/doctor_confirm_delete.html'
    success_url = reverse_lazy('accounts_web:doctor-list')

    def get_queryset(self):
        return CustomUser.objects.filter(clinic=self.request.user.clinic)

    def form_valid(self, form):
        messages.success(self.request, "تم إزالة حساب الموظف بنجاح.")
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'accounts/profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('accounts_web:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_instance'] = self.request.user
        
        user = self.request.user
        initial = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        
        profile = getattr(user, 'profile', None)
        if profile:
            initial.update({
                'phone': profile.phone,
                'gender': profile.gender,
                'birth_date': profile.birth_date,
                'address': profile.address,
            })
            
        kwargs['initial'] = initial
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        doc_profile = user.doctor_profile.first() if hasattr(user, 'doctor_profile') else None
        context['doctor_profile'] = doc_profile
        return context

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user = self.request.user
        
        user.email = cleaned_data['email']
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        if cleaned_data.get('password'):
            user.set_password(cleaned_data['password'])
        user.save()
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = cleaned_data['phone']
        profile.gender = cleaned_data['gender']
        profile.birth_date = cleaned_data.get('birth_date')
        profile.address = cleaned_data.get('address')
        profile.save()
        
        messages.success(self.request, "تم تحديث ملفك الشخصي بنجاح.")
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return '/'

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts_web:login')
        
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts_web:login')


class ClinicRegisterView(FormView):
    template_name = 'accounts/clinic_register.html'
    form_class = ClinicRegisterForm
    success_url = reverse_lazy('core_web:dashboard')

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        
        clinic = Clinic.objects.create(
            name=cleaned_data['clinic_name'],
            email=cleaned_data.get('clinic_email'),
            phone=cleaned_data.get('clinic_phone')
        )

        username = cleaned_data['manager_email'].split('@')[0]
        if CustomUser.objects.filter(username=username).exists():
            username = f"{username}_{uuid.uuid4().hex[:6]}"
            
        user = CustomUser.objects.create_user(
            username=username,
            email=cleaned_data['manager_email'],
            first_name=cleaned_data['manager_first_name'],
            last_name=cleaned_data['manager_last_name'],
            user_type='manager',
            clinic=clinic
        )
        user.set_password(cleaned_data['password'])
        user.save()

        UserProfile.objects.create(
            user=user,
            phone=cleaned_data.get('clinic_phone') or "",
            gender='male'
        )

        login(self.request, user)
        messages.success(self.request, "تم تسجيل العيادة وحساب مدير العيادة بنجاح!")
        return super().form_valid(form)


class ClinicSettingsView(LoginRequiredMixin, UpdateView):
    model = Clinic
    form_class = ClinicSettingsForm
    template_name = 'accounts/clinic_settings.html'
    success_url = reverse_lazy('accounts_web:clinic-settings')

    def get_object(self, queryset=None):
        if self.request.user.is_superuser or self.request.user.user_type == 'manager':
            if self.request.user.clinic:
                return self.request.user.clinic
        from django.http import Http404
        raise Http404("غير مسموح لك بالوصول لإعدادات هذه العيادة.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        clinic = self.request.user.clinic
        if clinic:
            # Fetch all staff members belonging to the current clinic
            staff_list = CustomUser.objects.filter(
                clinic=clinic,
                user_type__in=['doctor', 'receptionist', 'assistant', 'manager', 'admin'],
                is_archived=False
            )
            
            # Enrich staff list data (similar to DoctorListView)
            enriched_staff = []
            for user in staff_list:
                phone = getattr(user, 'profile', None).phone if (hasattr(user, 'profile') and user.profile) else "غير محدد"
                joined_date = user.date_joined.strftime('%d-%m-%Y') if user.date_joined else "15-01-2022"
                
                specialty = ""
                if user.user_type == 'doctor':
                    doc_profile = None
                    if hasattr(user, 'doctor_profile'):
                        try:
                            doc_profile = user.doctor_profile.first()
                        except AttributeError:
                            doc_profile = user.doctor_profile
                    elif hasattr(user, 'doctor'):
                        doc_profile = user.doctor
                    
                    specialty = doc_profile.specialization if doc_profile else "طب الأسنان العام"
                elif user.user_type == 'receptionist':
                    specialty = "موظف استقبال"
                elif user.user_type == 'assistant':
                    specialty = "مساعد طبيب"
                elif user.user_type == 'manager':
                    specialty = "مدير العيادة"
                elif user.user_type == 'admin':
                    specialty = "مسؤول النظام"
                    
                initials = f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else user.username[0]}"
                if not initials:
                    initials = "ع"
                    
                enriched_staff.append({
                    'id': user.pk,
                    'pk': user.pk,
                    'full_name': user.get_full_name() or user.username,
                    'user_type': user.user_type,
                    'user_type_display': 'طبيب' if user.user_type == 'doctor' else 'موظف استقبال' if user.user_type == 'receptionist' else 'مساعد' if user.user_type == 'assistant' else 'مدير' if user.user_type == 'manager' else 'مسؤول',
                    'specialty': specialty,
                    'phone': phone,
                    'email': user.email,
                    'joined_date': joined_date,
                    'is_active': user.is_active,
                    'initials': initials,
                })
            context['staff_list'] = enriched_staff
        return context

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث إعدادات العيادة بنجاح.")
        return super().form_valid(form)