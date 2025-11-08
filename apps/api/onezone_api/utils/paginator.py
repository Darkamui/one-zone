from rest_framework.pagination import CursorPagination


class CustomPaginator(CursorPagination):
    """
    Custom cursor-based pagination for efficient querying of large datasets

    Cursor pagination is preferred over offset pagination for:
    - Better performance on large datasets
    - Consistent results when data changes
    - Prevention of duplicate/skipped records
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'  # Default ordering
    cursor_query_param = 'cursor'

    def get_ordering(self, request, queryset, view):
        """
        Allow dynamic ordering via query parameter
        """
        ordering_param = request.query_params.get('ordering')
        if ordering_param:
            # Validate ordering field is allowed
            if hasattr(view, 'ordering_fields') and ordering_param.lstrip('-') in view.ordering_fields:
                return (ordering_param,)

        # Fall back to view's ordering or default
        if hasattr(view, 'ordering'):
            return view.ordering

        return (self.ordering,)
