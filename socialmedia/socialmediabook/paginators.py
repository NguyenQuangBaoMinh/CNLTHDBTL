from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

class SmallResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20

class CustomPaginationMixin:

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_pages': self.page.paginator.num_pages,
            'total_items': self.page.paginator.count,
            'current_page': self.page.number,
            'results': data
        })

# Ánh xạ pagination cho các model
MODEL_PAGINATION_MAP = {
    'Post': StandardResultsSetPagination,
    'Event': LargeResultsSetPagination,
    'Survey': SmallResultsSetPagination,
    'UserProfile': StandardResultsSetPagination
}

def get_pagination_class(model_name):

    return MODEL_PAGINATION_MAP.get(model_name, StandardResultsSetPagination)