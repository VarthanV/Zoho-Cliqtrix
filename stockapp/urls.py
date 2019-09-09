from django.urls import path 
from . import views
urlpatterns = [
    path('stock/',views.StockView.as_view()),
    path('amazon/',views.AmazonView.as_view()),
    path("medium/",views.MediumView.as_view()),
    path('wiki/',views.WikipediaView.as_view()),
    path('weather/',views.WeatherView.as_view()),
    path('news/<str:country>/',views.NewsView.as_view()),
    path('convert/<str:from_code>/',views.ConvertView.as_view())

  
 
]
