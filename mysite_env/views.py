import datetime
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from read_statistics.utils import get_seven_days_date, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_nums, dates = get_seven_days_date(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    # gain the hot blogs' data in seven days
    for_7_days_hot_data = cache.get('for_7_days_hot_data')
    if for_7_days_hot_data is None:
        for_7_days_hot_data = get_seven_days_hot_blogs()
        cache.set('for_7_days_hot_data', for_7_days_hot_data, 3600)


    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    context['for_7_days_hot_data'] = get_seven_days_hot_blogs()
    return render_to_response('home.html', context)


def get_seven_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gt=date). \
        values('id', 'title').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')
    return blogs
