from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import wikipedia
import random
import pyowm
from .models import Country
owm = pyowm.OWM('22f3801dd0c2afc5dfb7c7956dfa9be0')
newsApi = 'e65f4c84411344d39cfd1c1a405a8c82'
ua = UserAgent()
agent = str(ua.chrome)


class StockView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        code = request.GET.get('code')
        response = requests.get(
            f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={code}&apikey=E5VH3S3NZOHR3WRJ.')
        data = json.loads(response.text)
        item = data["Global Quote"]
       
        return Response({
            'code':code,
            'price': str(item['05. price']),
            'low': str(item["04. low"]),
            'high': str(item['03. high']),
            "volume": str(item['06. volume']),
            'previousclose': str(item['08. previous close']),
            'change': str(item['09. change']),
            'changepercent': str(item['10. change percent']),
            'open': str(item['02. open'])



        })


class AmazonView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        name = request.GET.get('name')
        modname = str(name).replace('%20', '+')

        bucket = list()

        while len(bucket) == 0:
            response = requests.get(
                f"https://www.amazon.in/s?k={modname}&ref=nb_sb_noss_2",  headers={'User-Agent': agent})
            soup = BeautifulSoup(response.text, 'lxml')
            for a, b, c, d, e in zip(soup.findAll('span', {'class': 'a-size-medium a-color-base a-text-normal'}), soup.findAll('span', {'class': 'a-price-whole'}), soup.findAll('img', {'class': 's-image'}), soup.findAll('a', {'class': 'a-link-normal a-text-normal'}), soup.findAll('span', {'class': 'a-icon-alt'})):
                # print(f"Name : {a.get_text()} Price :{b.get_text()}  Image url {c['src']}")
                bucket.append(
                    {"name": a.get_text(), 'price': b.get_text(), 'imgurl': c['src'], 'detailUrl': f"https://amazon.in/{d['href']}", 'rating': e.get_text()[0]})

        print(bucket)
        return Response(bucket)


class WikipediaView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        name = request.GET.get('name')
        modname = str(name).replace('%20', '')
        page = wikipedia.page(name)
        return Response({
            "title": page.title,
            'content': page.content,
            'image': page.images[random.randrange(0, len(page.images)-1)]
        })


class WeatherView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        climate = ''
        url = ''
        name = request.GET.get('name')
        observation = owm.weather_at_place(name)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')
        response = requests.get(
            f'https://www.google.com/search?q=temperature+{name}&oq=temperature&aqs=chrome..69i57j69i59l2j0l3.4036j0j0&sourceid=chrome&ie=UTF-8', headers={'User-Agent': agent})
        soup = BeautifulSoup(response.text, 'lxml')
        climate += soup.find(id='wob_dc').get_text()
        if 'cloudy'.title() in climate.title():
            print("Cloudy")
        elif 'clear'.title() in climate.title():
            print('clear')
        elif 'sunny'.title() in climate.title():
            print("Sunny")

        return Response({
            'min': temp['temp_min'],
            'max': temp['temp_max'],
            'temp': temp['temp'],
            'climate': climate
        })


class PNRCheckingView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        pass


class NewsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, country):
        key='76b1467e0abc4b5996e309418c6fbd89'
        url=f'https://newsapi.org/v2/top-headlines?country={country}&category={request.GET.get("category")}&apiKey={key}'
        response = requests.get(url)
        response = response.json()
        print(response)
        articles = response['articles']

        return Response([
            {
                'title': article['title'],
                'description':article['description'],
                'url':article['url'],
                'imgUrl':article['urlToImage'],
                'content': article['content']
            }

            for article in articles])
