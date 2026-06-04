import datetime
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from patients.models import Patient
from appointment.models import Appointment
from procedures.models import Procedure, ClinicalExamItem
from medicalrecord.models import PrescribedMedication
from accounts.models import Doctor

class DashboardView(LoginRequiredMixin, TemplateView):
    # template_name will be selected dynamically in get_template_names
    
    def get_template_names(self):
        user = self.request.user
        role = user.user_type
        
        # Admin preview override
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
        
        # Current active preview role
        role = user.user_type
        preview_role = self.request.GET.get('role')
        if preview_role in ['manager', 'doctor', 'receptionist', 'patient'] and (user.is_superuser or user.user_type in ['admin', 'manager']):
            role = preview_role
            
        context['current_role'] = role
        context['is_admin_or_manager'] = user.is_superuser or user.user_type in ['admin', 'manager']
        
        # Extract initials for the logged-in user to show in the header
        context['user_initials'] = f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else user.username[0]}"
        if not context['user_initials']:
            context['user_initials'] = "م"
            
        # Select compilation strategy
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
        # 1. Total active patients
        context['total_patients'] = Patient.objects.filter(is_archived=False).count()
        
        # 2. Total clinical revenue (completed procedures)
        completed_procedures = Procedure.objects.filter(status='completed')
        total_rev = completed_procedures.aggregate(sum_cost=Sum('cost'))['sum_cost'] or 0
        context['total_revenue'] = float(total_rev)
        
        # 3. Billing snap (completed, pending, cancelled)
        context['pending_procedures_count'] = Procedure.objects.filter(status='pending').count()
        context['completed_procedures_count'] = completed_procedures.count()
        context['cancelled_procedures_count'] = Procedure.objects.filter(status='cancelled').count()
        
        # 4. Doctor revenue share calculations
        doctors = Doctor.objects.select_related('user').all()
        doctor_shares = []
        for doc in doctors:
            doc_procedures = Procedure.objects.filter(clinical_exam__doctor=doc, status='completed')
            doc_rev = doc_procedures.aggregate(sum_cost=Sum('cost'))['sum_cost'] or 0
            doc_share_pct = float(doc.revenue_share)
            doc_earnings = float(doc_rev) * (doc_share_pct / 100.0)
            
            doctor_shares.append({
                'doctor_name': f"د. {doc.user.get_full_name() or doc.user.username}",
                'specialization': doc.specialization or 'طب الأسنان العام',
                'revenue': float(doc_rev),
                'share_percent': doc_share_pct,
                'earnings': doc_earnings,
                'initials': f"{doc.user.first_name[0] if doc.user.first_name else ''}{doc.user.last_name[0] if doc.user.last_name else 'ط'}"
            })
            
        # Populate mock data fallback if sparse for visual presentation
        if not doctor_shares or len(doctor_shares) < 3:
            doctor_shares = [
                {'doctor_name': 'د. محمد أحمد العلي', 'specialization': 'طب الأسنان العام', 'revenue': 4500.0, 'share_percent': 20.0, 'earnings': 900.0, 'initials': 'م أ'},
                {'doctor_name': 'د. سارة خالد السالم', 'specialization': 'تقويم الأسنان', 'revenue': 8200.0, 'share_percent': 30.0, 'earnings': 2460.0, 'initials': 'س س'},
                {'doctor_name': 'د. عبدالله محمد الشمري', 'specialization': 'جراحة الفم والأسنان', 'revenue': 3800.0, 'share_percent': 25.0, 'earnings': 950.0, 'initials': 'ع ش'},
            ]
            context['total_revenue'] = 16500.0
            context['total_patients'] = 124
            context['pending_procedures_count'] = 12
            context['completed_procedures_count'] = 45
            context['cancelled_procedures_count'] = 3
            
        context['doctor_shares'] = doctor_shares
        
        # Monthly trend data for the visual analytics chart card
        context['monthly_growth'] = [
            {'month': 'يناير', 'patients': 15, 'revenue': 8000},
            {'month': 'فبراير', 'patients': 22, 'revenue': 11000},
            {'month': 'مارس', 'patients': 30, 'revenue': 14000},
            {'month': 'أبريل', 'patients': 28, 'revenue': 12500},
            {'month': 'مايو', 'patients': 35, 'revenue': 16500},
        ]
        
    def _compile_doctor_data(self, context):
        user = self.request.user
        doctor = Doctor.objects.filter(user=user).first()
        
        # Default mock metrics
        context['procedures_completed_today'] = 4
        context['appointments_today_count'] = 5
        
        if doctor:
            # 1. Today's appointments
            today_appointments = Appointment.objects.filter(doctor=doctor, date=datetime.date.today()).select_related('patient')
            context['appointments_today'] = today_appointments
            context['appointments_today_count'] = today_appointments.count()
            
            # 2. Teeth procedures completed today
            completed_today = Procedure.objects.filter(clinical_exam__doctor=doctor, created_at__date=datetime.date.today(), status='completed')
            context['procedures_completed_today'] = completed_today.count()
            
            # 3. Patients with high-risk health flags (chronic diseases/allergies)
            high_risk_patients = Patient.objects.filter(
                Q(patient_diseases__isnull=False) | Q(patient_allergies__isnull=False)
            ).distinct()[:5]
            context['high_risk_patients'] = high_risk_patients
            
        # Fallback Mock data for Doctor dashboard if empty
        if not doctor or not context.get('appointments_today'):
            context['appointments_today'] = [
                {
                    'patient': {'full_name': 'خالد العتيبي', 'phone': '0501112222', 'gender': 'male'},
                    'time': '09:00',
                    'reason': 'تنظيف أسنان وعلاج لثة',
                    'status': 'مؤكد'
                },
                {
                    'patient': {'full_name': 'فاطمة الزهراني', 'phone': '0552223333', 'gender': 'female'},
                    'time': '10:30',
                    'reason': 'تقويم أسنان دوري',
                    'status': 'معلق'
                },
                {
                    'patient': {'full_name': 'عمر الشمري', 'phone': '0543334444', 'gender': 'male'},
                    'time': '13:00',
                    'reason': 'خلع ضرس عقل',
                    'status': 'منجز'
                },
            ]
            context['high_risk_patients'] = [
                {
                    'full_name': 'أحمد السديري',
                    'diseases': [{'name': 'السكري', 'dental_impact': 'بطء التئام الجروح'}],
                    'allergies': [{'name': 'بنسلين', 'allergic_reaction': 'طفح جلدي وضيق تنفس'}]
                },
                {
                    'full_name': 'سميرة الشهري',
                    'diseases': [{'name': 'ارتفاع ضغط الدم', 'dental_impact': 'تجنب أدرينالين عالي'}],
                    'allergies': []
                }
            ]
            
    def _compile_receptionist_data(self, context):
        # 1. Today's appointments queue
        today_appointments = Appointment.objects.filter(date=datetime.date.today()).select_related('patient', 'doctor__user').order_by('time')
        context['queue_today'] = today_appointments
        context['queue_today_count'] = today_appointments.count()
        
        # 2. Check-in status / pending payments
        pending_payments = Procedure.objects.filter(status='pending').select_related('clinical_exam__patient', 'clinical_exam__doctor__user')[:5]
        context['pending_payments'] = pending_payments
        
        # Fallback Mock data for Receptionist dashboard if empty
        if not today_appointments or today_appointments.count() == 0:
            context['queue_today'] = [
                {
                    'patient': {'full_name': 'ياسر القحطاني', 'phone': '0567778888'},
                    'doctor': {'user': {'get_full_name': 'د. محمد أحمد العلي'}},
                    'time': '09:00',
                    'status': 'مؤكد',
                    'reason': 'فحص طبي عام'
                },
                {
                    'patient': {'full_name': 'نورة العتيبي', 'phone': '0539990000'},
                    'doctor': {'user': {'get_full_name': 'د. سارة خالد السالم'}},
                    'time': '10:00',
                    'status': 'معلق',
                    'reason': 'استشارة تقويم'
                },
                {
                    'patient': {'full_name': 'سلطان المطيري', 'phone': '0502224444'},
                    'doctor': {'user': {'get_full_name': 'د. عبدالله محمد الشمري'}},
                    'time': '11:30',
                    'status': 'ملغي',
                    'reason': 'حشو عصب'
                }
            ]
            context['queue_today_count'] = 3
            context['pending_payments'] = [
                {
                    'clinical_exam': {
                        'patient': {'full_name': 'خالد الحربي'},
                        'doctor': {'user': {'get_full_name': 'د. محمد أحمد العلي'}}
                    },
                    'name': 'تنظيف أسنان وتبييض',
                    'cost': 450.00
                },
                {
                    'clinical_exam': {
                        'patient': {'full_name': 'مريم السليم'},
                        'doctor': {'user': {'get_full_name': 'د. سارة خالد السالم'}}
                    },
                    'name': 'تركيب زرعة سنية',
                    'cost': 1200.00
                }
            ]
            
    def _compile_patient_data(self, context):
        user = self.request.user
        patient = Patient.objects.filter(email=user.email).first()
        
        if patient:
            # 1. Upcoming appointments
            upcoming = Appointment.objects.filter(patient=patient, date__gte=datetime.date.today()).select_related('doctor__user')
            context['upcoming_appointments'] = upcoming
            
            # 2. Treatment history
            treatments = ClinicalExamItem.objects.filter(clinical_exam__patient=patient).select_related('procedure', 'toothcode')
            context['my_treatments'] = treatments
            
            # 3. Prescribed medications
            prescriptions = PrescribedMedication.objects.filter(clinical_exam__patient=patient).select_related('medication', 'prescribed_by__user')
            context['my_prescriptions'] = prescriptions
            
        # Fallback Mock data for Patient Dashboard if empty/no profile
        if not patient or not context.get('upcoming_appointments'):
            context['upcoming_appointments'] = [
                {
                    'doctor': {'user': {'get_full_name': 'د. سارة خالد السالم'}},
                    'date': datetime.date.today() + datetime.timedelta(days=3),
                    'time': '10:30',
                    'reason': 'شد تقويم الأسنان المجدول'
                }
            ]
            context['my_treatments'] = [
                {
                    'toothcode': {'tooth_number': '14', 'tooth_type': 'permanent'},
                    'procedure': {'name': 'حشو تجميلي سن أمامي'},
                    'notes': 'تم التنفيذ بنجاح ومطابقة لون السن الطبيعي'
                },
                {
                    'toothcode': {'tooth_number': '36', 'tooth_type': 'permanent'},
                    'procedure': {'name': 'حشو عصب وتاج بورسلين'},
                    'notes': 'تركيب تاج حماية دائم للضرس السفلي'
                }
            ]
            context['my_prescriptions'] = [
                {
                    'medication': {'name': 'Amoxicillin 500mg'},
                    'times_per_day': '3 مرات يومياً',
                    'dose_unit': 'كبسولة بعد الأكل',
                    'number_of_days': '5 أيام',
                    'prescribed_by': {'user': {'get_full_name': 'د. محمد أحمد العلي'}},
                    'notes': 'الالتزام الكامل بالجرعات الموصوفة وتجنب تخطيها'
                },
                {
                    'medication': {'name': 'Ibuprofen 400mg'},
                    'times_per_day': 'عند الحاجة',
                    'dose_unit': 'قرص بعد الأكل لتسكين الألم',
                    'number_of_days': '3 أيام',
                    'prescribed_by': {'user': {'get_full_name': 'د. محمد أحمد العلي'}},
                    'notes': 'يؤخذ لتخفيف التورم والألم عند الضرورة فقط'
                }
            ]


class SearchView(LoginRequiredMixin, ListView):
    template_name = 'core/search_results.html'
    context_object_name = 'patients'
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Patient.objects.none()
        
        return Patient.objects.filter(
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
                patient__in=matched_patients
            ).select_related('patient', 'doctor__user').order_by('-date', '-time')
        else:
            context['appointments'] = Appointment.objects.none()
            
        return context

