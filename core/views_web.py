import datetime
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from patients.models import Patient
from appointment.models import Appointment
from procedures.models import Procedure, ClinicalExamItem
from medicalrecord.models import PrescribedMedication
# استيراد النماذج المطلوبة لضمان مرونة الاستعلامات
from accounts.models import Doctor, CustomUser, Clinic

class DashboardView(LoginRequiredMixin, TemplateView):
    
    def get_template_names(self):
        user = self.request.user
        role = user.user_type
        
        # تخطي العرض المسبق للمشرف (Admin preview override)
        preview_role = self.request.GET.get('role')
        if preview_role in ['manager', 'doctor', 'receptionist', 'patient'] and (user.is_superuser or user.user_type in ['admin', 'manager']):
            role = preview_role
            
        if role in ['manager', 'admin'] or user.is_superuser:
            return ['core/dashboard_manager.html']
        elif role == 'doctor':
            return ['core/dashboard_doctor.html']
        elif role == 'receptionist':
            return ['core/dashboard_receptionist.html']
        elif role == 'patient':
            return ['core/dashboard_patient.html']
        else:
            return ['core/dashboard_manager.html']
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # تحديد الدور النشط حالياً للعرض
        role = user.user_type
        preview_role = self.request.GET.get('role')
        if preview_role in ['manager', 'doctor', 'receptionist', 'patient'] and (user.is_superuser or user.user_type in ['admin', 'manager']):
            role = preview_role
            
        context['current_role'] = role
        context['is_admin_or_manager'] = user.is_superuser or user.user_type in ['admin', 'manager']
        
        # استخراج الحروف الأولى لاسم المستخدم لعرضها في الهيدر
        context['user_initials'] = f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else user.username[0]}"
        if not context['user_initials']:
            context['user_initials'] = "م"
            
        # تحديد استراتيجية تجميع البيانات بحسب الصلاحية
        if role in ['manager', 'admin'] or user.is_superuser:
            self._compile_manager_data(context)
        elif role == 'doctor':
            self._compile_doctor_data(context)
        elif role == 'receptionist':
            self._compile_receptionist_data(context)
        elif role == 'patient':
            self._compile_patient_data(context)
            
        return context

    def _compile_manager_data(self, context):
        # التحقق من وجود العيادة للحساب الحالي، مع إرجاع أول عيادة كخيار احتياطي للمسؤولين
        clinic = self.request.user.clinic
        if not clinic:
            clinic = Clinic.objects.first()

        # 1. إجمالي المرضى النشطين من قاعدة البيانات للعيادة المحددة
        context['total_patients'] = Patient.objects.filter(clinic=clinic, is_archived=False).count() if clinic else 0
        
        # 2. إجمالي الإيرادات الفعلية (الإجراءات المكتملة فقط)
        if clinic:
            completed_procedures = Procedure.objects.filter(clinical_exam__patient__clinic=clinic, status='completed')
        else:
            completed_procedures = Procedure.objects.none()
            
        total_rev = completed_procedures.aggregate(sum_cost=Sum('cost'))['sum_cost'] or 0
        context['total_revenue'] = float(total_rev)
        
        # 3. توزيع الفواتير والعمليات
        if clinic:
            context['pending_procedures_count'] = Procedure.objects.filter(clinical_exam__patient__clinic=clinic, status='pending').count()
            context['completed_procedures_count'] = completed_procedures.count()
            context['cancelled_procedures_count'] = Procedure.objects.filter(clinical_exam__patient__clinic=clinic, status='cancelled').count()
        else:
            context['pending_procedures_count'] = 0
            context['completed_procedures_count'] = 0
            context['cancelled_procedures_count'] = 0
            
        # حساب النسب المئوية الفعلية لتوزيع الفواتير (أشرطة التحميل)
        total_procs = context['completed_procedures_count'] + context['pending_procedures_count'] + context['cancelled_procedures_count']
        if total_procs > 0:
            context['completed_pct'] = (context['completed_procedures_count'] / total_procs) * 100
            context['pending_pct'] = (context['pending_procedures_count'] / total_procs) * 100
            context['cancelled_pct'] = (context['cancelled_procedures_count'] / total_procs) * 100
        else:
            context['completed_pct'] = 0
            context['pending_pct'] = 0
            context['cancelled_pct'] = 0
        
        # 4. حساب حصص الأطباء الفعلية بناءً على مستخدمي الأطباء الفعليين (بمرونة عالية)
        doctor_shares = []
        if clinic:
            # نستعلم عن مستخدمي الأطباء أولاً لضمان ظهورهم حتى لو لم يكتمل ملف الطبيب الفرعي في لوحة التحكم
            doctor_users = CustomUser.objects.filter(clinic=clinic, user_type='doctor', is_archived=False)
            
            for doc_user in doctor_users:
                # محاولة جلب ملف الطبيب (Doctor) المرتبط بالمستخدم
                doc_profile = None
                if hasattr(doc_user, 'doctor_profile'):
                    try:
                        doc_profile = doc_user.doctor_profile.first()
                    except AttributeError:
                        doc_profile = doc_user.doctor_profile
                elif hasattr(doc_user, 'doctor'):
                    doc_profile = doc_user.doctor
                
                doc_share_pct = float(doc_profile.revenue_share) if (doc_profile and doc_profile.revenue_share) else 0.0
                specialization = (doc_profile.specialization if doc_profile else None) or 'طب الأسنان العام'
                
                # حساب الإيرادات المرتبطة بهذا الطبيب
                if doc_profile:
                    doc_procedures = Procedure.objects.filter(clinical_exam__doctor=doc_profile, status='completed')
                else:
                    doc_procedures = Procedure.objects.filter(clinical_exam__doctor__user=doc_user, status='completed')
                    
                doc_rev = doc_procedures.aggregate(sum_cost=Sum('cost'))['sum_cost'] or 0
                doc_earnings = float(doc_rev) * (doc_share_pct / 100.0)
                
                doctor_shares.append({
                    'doctor_name': f"د. {doc_user.get_full_name() or doc_user.username}",
                    'specialization': specialization,
                    'revenue': float(doc_rev),
                    'share_percent': doc_share_pct,
                    'earnings': doc_earnings,
                    'initials': f"{doc_user.first_name[0] if doc_user.first_name else ''}{doc_user.last_name[0] if doc_user.last_name else 'ط'}"
                })
            
        context['doctor_shares'] = doctor_shares
        context['monthly_growth'] = []
        
    def _compile_doctor_data(self, context):
        user = self.request.user
        doctor = Doctor.objects.filter(user=user, user__clinic=user.clinic).first()
        
        context['appointments_today'] = Appointment.objects.none()
        context['appointments_today_count'] = 0
        context['procedures_completed_today'] = 0
        context['high_risk_patients'] = Patient.objects.none()
        
        if doctor:
            today_appointments = Appointment.objects.filter(doctor=doctor, date=datetime.date.today()).select_related('patient')
            context['appointments_today'] = today_appointments
            context['appointments_today_count'] = today_appointments.count()
            
            completed_today = Procedure.objects.filter(clinical_exam__doctor=doctor, created_at__date=datetime.date.today(), status='completed')
            context['procedures_completed_today'] = completed_today.count()
            
            high_risk_patients = Patient.objects.filter(
                clinic=user.clinic
            ).filter(
                Q(patient_diseases__isnull=False) | Q(patient_allergies__isnull=False)
            ).distinct()[:5]
            context['high_risk_patients'] = high_risk_patients
            
    def _compile_receptionist_data(self, context):
        today_appointments = Appointment.objects.filter(clinic=self.request.user.clinic, date=datetime.date.today()).select_related('patient', 'doctor__user').order_by('time')
        context['queue_today'] = today_appointments
        context['queue_today_count'] = today_appointments.count()
        
        pending_payments = Procedure.objects.filter(clinical_exam__patient__clinic=self.request.user.clinic, status='pending').select_related('clinical_exam__patient', 'clinical_exam__doctor__user')[:5]
        context['pending_payments'] = pending_payments
        
    def _compile_patient_data(self, context):
        user = self.request.user
        patient = Patient.objects.filter(email=user.email, clinic=user.clinic).first()
        
        context['upcoming_appointments'] = Appointment.objects.none()
        context['my_treatments'] = ClinicalExamItem.objects.none()
        context['my_prescriptions'] = PrescribedMedication.objects.none()
        
        if patient:
            upcoming = Appointment.objects.filter(patient=patient, date__gte=datetime.date.today()).select_related('doctor__user')
            context['upcoming_appointments'] = upcoming
            
            treatments = ClinicalExamItem.objects.filter(clinical_exam__patient=patient).select_related('procedure', 'toothcode')
            context['my_treatments'] = treatments
            
            prescriptions = PrescribedMedication.objects.filter(clinical_exam__patient=patient).select_related('medication', 'prescribed_by__user')
            context['my_prescriptions'] = prescriptions


class SearchView(LoginRequiredMixin, ListView):
    template_name = 'core/search_results.html'
    context_object_name = 'patients'
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Patient.objects.none()
        
        return Patient.objects.filter(clinic=self.request.user.clinic).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query) |
            Q(address__icontains=query)
        ).filter(is_archived=False)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['search_query'] = query
        
        matched_patients = self.get_queryset()
        if matched_patients.exists():
            context['appointments'] = Appointment.objects.filter(
                clinic=self.request.user.clinic,
                patient__in=matched_patients
            ).select_related('patient', 'doctor__user').order_by('-date', '-time')
        else:
            context['appointments'] = Appointment.objects.none()
            
        return context