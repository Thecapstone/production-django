from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class LinkHeaderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data) -> Response:
        count = self.page.paginator.count
        next_link = self.get_next_link()
        previous_link = self.get_previous_link()
        total_pages = self.page.paginator.num_pages
        page_number = self.page.number

        return Response({
            'count' : count,
            'next' : next_link,
            'previous' : previous_link,
            'total_pages' : total_pages,
            'current_page' : page_number,
            'results' : data,
        })