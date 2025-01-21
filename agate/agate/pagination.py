from rest_framework.pagination import CursorPagination


class MyCursorPagination(CursorPagination):
    # records to be shown per page
    page_size = 100
    # Ordering the records
    ordering = 'created_at'
