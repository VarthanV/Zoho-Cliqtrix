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
from wikipedia.exceptions import DisambiguationError, PageError
from .models import Country

owm = '22f3801dd0c2afc5dfb7c7956dfa9be0'
newsApi = 'e65f4c84411344d39cfd1c1a405a8c82'
ua = UserAgent()
agent = str(ua.chrome)


def convert_temp(kelvin):

    celsius = kelvin-273
    return celsius


class StockView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        code = request.GET.get('code')
        response = requests.get(
            f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={code}&apikey=E5VH3S3NZOHR3WRJ.')
        data = json.loads(response.text)
        item = data["Global Quote"]

        return Response({
            'code': code,
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
        try:
            page = wikipedia.page(modname)
            return Response({
                'status': 200,
                "title": page.title,
                'content': page.summary,
                'image': str(page.images[random.randrange(0, len(page.images)-1)]),
                'detailurl': f'https://en.wikipedia.org/wiki/{name}'
            })
        except DisambiguationError or PageError as e:
            print(e)
            return Response({
                'status': 404
            })


class WeatherView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        base_url = "http://api.openweathermap.org/data/2.5/weather?"

        complete_url = base_url + "appid=" + \
            owm + "&q=" + request.GET.get('name')

        response = requests.get(complete_url)

        x = response.json()
        if x["cod"] != "404":

            y = x["main"]
            current_temperature = y["temp"]
            current_pressure = y["pressure"]

            current_humidity = y["humidity"]

            z = x["weather"]

   
            weather_description = z[0]["description"]
            return Response({
                'temp':round(convert_temp(current_temperature),2),
                'pressure':current_pressure,
                'humidity':current_humidity,
                'weather':weather_description
            })


class PNRCheckingView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        pass


class NewsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, country):
        key = '76b1467e0abc4b5996e309418c6fbd89'
        url = f'https://newsapi.org/v2/top-headlines?country={country}&category={request.GET.get("category")}&apiKey={key}'
        response = requests.get(url)
        response = response.json()
        print(response)
        articles = response['articles']
        if len(articles) == 0:
            return Response({"status": 404})

        return Response({
            'status': 200,
            'articles': [
                {
                    'title': article['title'],
                    'description':article['description'],
                    'url':article['url'],
                    'imgUrl':article['urlToImage'],
                    'content': article['content']
                }

                for article in articles]})
