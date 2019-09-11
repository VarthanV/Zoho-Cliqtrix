from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import get_jobs
import wikipedia
import random
import pyowm
from wikipedia.exceptions import DisambiguationError, PageError
from .models import Bookmark
import re
from apiclient.discovery import build
owm = '22f3801dd0c2afc5dfb7c7956dfa9be0'
newsApi = 'e65f4c84411344d39cfd1c1a405a8c82'
ua = UserAgent()
agent = str(ua.random)


def check_name(title):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if re.match(regex, title):
        item = title.split('/')
        return item[-1].replace('-', ' ')
    else:
        return title


class ConvertView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, from_code):
        to = request.GET.get('to')
        key = 'MGXCG9ZZLET2BTYQ'
        # "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=" + from + "&to_currency=" + to + "&apikey=" + apiKey;
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_code}&to_currency={to}&apikey={key}'
        response = requests.get(url)
        if response.status_code == 200:
            return Response(

                {
                    "status": 200,
                    "data": response.json()

                })
        else:
            return Response({"status": 404})


class PixView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, term):
        key = '12208529-4c52328be6cfa6e47e390cdaf'
        # 'https://pixabay.com/api/?key={key}&q={term}&image_type=photo&pretty=true';
        url = f'https://pixabay.com/api/?key={key}&q={term}&image_type=photo&pretty=true&page=1&per_page=10'
        response = requests.get(url).json()
        return Response(response)


class DomainView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, domain):
        headers = {
            'Authorization': 'sso-key 3mM44UaCMkPo4p_VqQC796SGSRNAXsMVZ8vos:Cr4PmgV1Y1vqMU4oZ5Zrxd'}
        # https://api.ote-godaddy.com/v1/domains/available?domain={domain}&checkType=FAST&forTransfer=false';
        url = f'https://api.ote-godaddy.com/v1/domains/available?domain={domain}&checkType=FAST&forTransfer=false'
        response = requests.get(url, headers=headers)
        return Response(response.json())


class StockView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, code):
        response = requests.get(
            f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={code}&apikey=E5VH3S3NZOHR3WRJ.')

        return Response(response.json())


class ZoneView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, code):
        key = "71OD11E2E8ZG"
        # "http://api.timezonedb.com/v2.1/list-time-zone?key={key}&format=json&country={code}&fields=zoneName;
        url = f'http://api.timezonedb.com/v2.1/list-time-zone?key={key}&format=json&country={code}&fields=zoneName'
        response = requests.get(url)
        return Response(response.json())


class TimeView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        key = "71OD11E2E8ZG"
        zone = request.GET.get('zone')
        # "http://api.timezonedb.com/v2.1/get-time-zone?key={key}&format=json&by=zone&zone={zone}&fields=formatted;
        url = f'http://api.timezonedb.com/v2.1/get-time-zone?key={key}&format=json&by=zone&zone={zone}&fields=formatted'
        response = requests.get(url)
        return Response(response.json())


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
                    {"name": a.get_text(), 'price': b.get_text(), 'imgurl': c['src'], 'id': d["href"].split("/")[3], 'rating': e.get_text()[0]})
        return Response(bucket)


class MediumView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        name = request.GET.get("name")
        url = f"https://medium.com/search?q={name}"
        res = requests.get(url, headers={'User-Agent': str(ua.random)})
        html = BeautifulSoup(res.text, "html.parser")
        posts = html.findAll("div", {"class": "postArticle"})
        posts_list = []
        for index, post in enumerate(posts):
            post_map = {}
            title = post.findChildren("h3", recursive=True)
            if len(title) == 0:
                continue
            else:
                post_map.update({"title": title[0].find(text=True)})
            img = post.findChildren(
                "img", {"class": "progressiveMedia-image"}, recursive=True)
            if len(img) > 0:
                post_map.update({"img": img[0].attrs.get("data-src")})
            else:
                post_map.update({"img": ""})
            likes = post.findChildren("button", {
                                      "class": "button button--chromeless u-baseColor--buttonNormal js-multirecommendCountButton u-disablePointerEvents"}, recursive=True)
            if len(likes) > 0:
                post_map.update({"likes": likes[0].contents[0]})
            else:
                post_map.update({"likes": 0})
            url = post.findChildren(
                "a", {"class": "button button--smaller button--chromeless u-baseColor--buttonNormal"}, recursive=True)
            if len(url) > 0:
                post_map.update(
                    {"url": url[0].attrs.get("href").split("?")[0]})
                posts_list.append(post_map)
            else:
                continue
        return Response(posts_list)


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
                'image': str(page.images[0]),
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
            return Response(x)
        else:
            return Response()


class PNRCheckingView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        pass


class NewsView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, country):
        key = '76b1467e0abc4b5996e309418c6fbd89'
        # https://newsapi.org/v2/top-headlines?country={con} &category={cat}&apiKey={key};
        cat = request.GET.get('cat').replace('%20', '')
        url = f'https://newsapi.org/v2/top-headlines?country={country}&category={cat}&apiKey={key}'
        response = requests.get(url)
        return Response(response.json())


class BookmarkGetView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        print(request.POST.get('email'))
        bookmarks = Bookmark.objects.filter(email=request.POST.get('email'))

        return Response(
            {'status': '200',
             'bookmarks': [
                 {
                     'pk': bookmark.pk,
                     'title': bookmark.title,
                     'url': bookmark.url
                 }
                 for bookmark in bookmarks]}
        )


class BookmarkCreateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = dict(request.POST)
        email = data['email'][0]
        title = data['title'][0]
        url = data['url'][0]
        bookmark = Bookmark()
        bookmark.email = email

        bookmark.title = check_name(title)
        bookmark.url = url
        bookmark.save()
        return Response({'status': 200})


class BookmarkDeleteView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, pk):
        bookmark = Bookmark.objects.get(pk=pk)
        bookmark.delete()
        return Response({"status": 200})


def get_tube_results(query):
    # https://www.youtube.com/watch?v=sLtki8Ezz7c -watch url
    # https://www.youtube.com/playlist?list=PLC3y8-rFHvwgg3vaYJgHGnModB54rxOk3 - Playslit

    DEVELOPER_KEY = "AIzaSyDlkZhifaMdKs2zEEPcq7EUL_tMxvd605w"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                           developerKey=DEVELOPER_KEY)
    search_keyword = youtube_object.search().list(q=f'{query} videos', part="id, snippet",
                                                  maxResults=10).execute()

    results = search_keyword.get("items", [])
    print(results[0])
    videos = []
    if len(results) > 0:
        for item in results:
            if item['id']['kind'] == 'youtube#playlist':
                url = f'https://www.youtube.com/playlist?list={item["id"]["playlistId"]}'
            if item['id']['kind'] == 'youtube#video':
                url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"

            data = {
                'url': url,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'imgurl': item['snippet']['thumbnails']['medium']['url']

            }

            videos.append(data)

    return videos


class CourseBotView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        youtube_key = 'AIzaSyDlkZhifaMdKs2zEEPcq7EUL_tMxvd605w'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Authorization": "Basic RWdzUVBBQ243Ulh2OXlqczBtVEUxN21Ec2F5bmR2djh4Y0poMlE0TDpsdjNwUFFUNkw3eU4yZVdhRTBmVVNWOE9oREN0c0NZUFhjM2RGaE9YOXNUcjNBRTJYT09EMDJZdEduckhCOHBIZEtkUXBtZ3kyWTZLUmkwcmdUcGk0ZFUxT2pxQ1RoVXVZaWxEZEpoVjFlRzFGN2V2dGpRYk5MdHY0dFBtd3FKRw==",
            "Content-Type": "application/json;charset=utf-8"
        }
        search = request.GET.get('q')
        udemy_url = f'https://www.udemy.com/api-2.0/courses/?page=1&page_size=10&search={search}'
        response = requests.get(udemy_url, headers=headers)
        resp = response.json()
        if resp.get('count') > 10:
            courses = resp.get('results')[0:10]
            course = []
            for item in courses:
                data = {
                    "title": item['title'],
                    "price": item['price'],
                    'url': f'https://udemy.com{item["url"]}',
                    'img': item['image_240x135']
                }
                course.append(data)

        return Response({
            "udemy": course,
            "youtube": get_tube_results(search)
        })


class JobView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
       pass
