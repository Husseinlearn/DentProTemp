import django_filters
from .models import Patient

class PatientFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.CharFilter(lookup_expr='iexact')
    date_of_birth = django_filters.DateFilter()

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'phone', 'email', 'gender', 'date_of_birth']
    # order_by = django_filters.OrderingFilter(
    #     fields=(
    #         ('first_name', 'first_name'),
    #         ('last_name', 'last_name'),
    #         ('date_of_birth', 'date_of_birth'),
    #         ('created_at', 'created_at'),
    #     ),
    #     field_labels={
    #         'first_name': 'First Name',
    #         'last_name': 'Last Name',
    #         'date_of_birth': 'Date of Birth',
    #         'created_at': 'Created At',
    #     },
    #     default='created_at'
    # )