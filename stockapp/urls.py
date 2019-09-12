from django.urls import path 
from . import views
urlpatterns = [
    path('stock/<str:code>/',views.StockView.as_view()),
    path('amazon/',views.AmazonView.as_view()),
    path("medium/",views.MediumView.as_view()),
    path('wiki/',views.WikipediaView.as_view()),
    path('weather/',views.WeatherView.as_view()),
    path('news/<str:country>/',views.NewsView.as_view()),
    path('convert/<str:from_code>/',views.ConvertView.as_view()),
    path('domain/<str:domain>/',views.DomainView.as_view()),
    path('pix/<str:term>/',views.PixView.as_view()),
    path('zone/<str:code>/',views.ZoneView.as_view()),
    path('time/',views.TimeView.as_view()),
    path('getbook/',views.BookmarkGetView.as_view()),
    path('newbook/',views.BookmarkCreateView.as_view()),
    path('delbook/<int:pk>/',views.BookmarkDeleteView.as_view()),
    #path('test/',views.TestView.as_view())
    path('course/',views.CourseBotView.as_view()),
    path('job/',views.JobView.as_view()),
    path('tube/',views.TubeView.as_view())

  
 
]
