import django_filters
from .models import User

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter')
    role = django_filters.CharFilter(field_name='role__name')
    status = django_filters.CharFilter(field_name='status')
    department = django_filters.CharFilter(field_name='department')
    date_range_from = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='gte')
    date_range_to = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='lte')

    class Meta:
        model = User
        fields = {
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'employee_id': ['exact', 'icontains'],
            'role': ['exact'],
            'status': ['exact'],
            'department': ['exact'],
            'last_login': ['gte', 'lte'],
            'created_at': ['gte', 'lte'],
            'updated_at': ['gte', 'lte']
        }

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            first_name__icontains=value
        ) | queryset.filter(
            last_name__icontains=value
        ) | queryset.filter(
            email__icontains=value
        ) | queryset.filter(
            phone__icontains=value
        ) | queryset.filter(
            employee_id__icontains=value
        ) 