from rest_framework.filters import SearchFilter
from django_filters import FilterSet
from django_filters import rest_framework as filters

from boards.models import Board


class CustomSearchFilter(SearchFilter):
    """
    Assignee : 기연

    title or content or title+content 검색을 위한 필터입니다.
    """

    def get_search_fields(self, view, request):
        search_by = request.query_params.get('search_by', "title,content")

        if search_by == "title":
            return ['title']
        elif search_by == "content":
            return ['content']
        return super().get_search_fields(view, request)


class BoardFilter(FilterSet):
    """
    Assignee : 기연

    feed_type과 hashtag 검색을 위한 필터입니다.
    """

    type = filters.CharFilter(field_name="feed_type", lookup_expr='exact')
    hashtag = filters.CharFilter(field_name="hashtags", lookup_expr='exact', method='custom_search_filter')

    class Meta:
        model = Board
        fields = ['type', 'hashtag']
    

    def custom_search_filter(self, queryset, name, value):
        # print(self.request.user)
        if value:
            return queryset.filter(hashtags__exact=value) # 해시태그를 입력했을 경우
        else:
            return queryset.all() # 해시태그를 입력하지 않을 경우 (default:본인계정) - 수정 필요
