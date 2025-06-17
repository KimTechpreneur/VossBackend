import django_filters
from .models import User
from django.db.models import Q

class UserFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter')
    role = django_filters.CharFilter(field_name='role__name')
    status = django_filters.CharFilter(field_name='status')
    department = django_filters.CharFilter(field_name='department__name')
    unit = django_filters.CharFilter(field_name='unit__id')
    date_range_from = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='gte')
    date_range_to = django_filters.DateTimeFilter(field_name='last_login', lookup_expr='lte')
    last_login = django_filters.DateFromToRangeFilter()

    class Meta:
        model = User
        fields = ['role', 'status', 'department', 'unit', 'last_login']

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)
        # You can add more complex filtering logic here if needed
        # For example, filtering by multiple statuses:
        # self.filters['status'].lookup_expr = 'in'

    @property
    def qs(self):
        parent_qs = super().qs
        search = self.data.get('search', None)

        if search:
            return parent_qs.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(employee_id__icontains=search)
            )

        return parent_qs

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value) |
            Q(email__icontains=value) |
            Q(phone__icontains=value) |
            Q(employee_id__icontains=value)
        ) 