from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

from rest_framework.status import (
HTTP_400_BAD_REQUEST,
HTTP_404_NOT_FOUND,
HTTP_200_OK,
HTTP_401_UNAUTHORIZED,
)
from rest_framework.response import  Response
from .serializers import JobListingSerializer
from rest_framework import viewsets, generics
from .models import JobListing, Job, Location, Extension
import requests
from bs4 import BeautifulSoup
from time import sleep
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import  Response
from rest_framework.views import exception_handler
from rest_framework import filters
from rest_framework.exceptions import APIException
# Create your views here.
class MissingTokenException(APIException):
    status_code = 400
    default_detail = 'Your request does not contain token'
    default_code = 'no_token'
class InvalidTokenException(APIException):
    status_code = 400
    default_detail = 'Your Request Contains invalid token'
    default_code = 'Invalid_token'

@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    data=request.query_params.get('username')
    print(data)
    username=request.query_params.get('username')
    print(username)
    password=request.query_params.get('password')
    print(password)
    if username is None or password is None:
        return Response({'error':'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user=authenticate(username=username,password=password)
    if not user:
        return Response({'error':'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token,_=Token.objects.get_or_create(user=user)
    return Response({'token':token.key},
                    status=HTTP_200_OK)

class JoblistingAPIView(generics.ListCreateAPIView):


    serializer_class = JobListingSerializer
    def get_queryset(self):
        token = Token.objects.get(user=self.request.user)
        print(self.request.user)

        jobs=JobListing.objects.all()
        title=self.request.query_params.get('title',None)
        location=self.request.query_params.get('location',None)
        extension=self.request.query_params.get('ext',None)

        stitle = title.split(' ')[0]

        s_extention=extension.split(' ')[0]

        slocation = location.split(' ')[0]
        sextention=extension.split(' ')
        try:
            auth_token=sextention[3].split('"')[0]
        except IndexError:
           raise MissingTokenException
        print('auth ljfdsklajflkjslkjdfkl')
        print(extension)
        print(auth_token)
        print(token)
        print(type(token))
        if auth_token != token.key:
           raise InvalidTokenException
        else:
            if title is not None and location is None:
                set=jobs.filter(search_cat__icontains=stitle)

                if not set:
                    scrape(stitle,slocation,s_extention)
                    jobs.filter(search_cat__icontains=stitle)

            elif location is not None and title is None:
                queryset=jobs.filter(search_loc__icontains=slocation)
                if not queryset:
                    scrape(stitle, slocation, s_extention)
                    queryset = jobs.filter(search_loc__icontains=slocation)

            elif title is not None and location is not None:
                queryset=jobs.filter(Q(search_cat__icontains=stitle) & Q(search_loc__icontains=slocation))
                print(queryset)

                if not queryset:
                    print('notfound')
                    scrape(stitle, slocation, s_extention)
                    queryset=jobs.filter(Q(search_cat__icontains=title) & Q(search_loc__icontains=slocation))

                    scrape(stitle,slocation,s_extention)
            else:
                queryset=jobs


            print(title)
            print(location)
            return queryset


def scrape(gjob,glocation,extension):


    job = gjob
    if glocation is None:
        place='london'
    else:
        place = glocation
    if extension is None:
        dormain_extension='com'
    else:
        dormain_extension = extension
    url = 'https://www.indeed.' + dormain_extension + '/jobs?q=' + job + '&l=' + place
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    jobcard = soup.find_all(class_='jobsearch-SerpJobCard')
    for counter, card in enumerate(jobcard):
        link = jobcard[counter].findChild().findChild()
        item_id = link.attrs['id']
        slicedlink = link.attrs['id'][3:]
        try:
            location = jobcard[counter].find(class_='sjcl').find(class_='location').text
        except AttributeError:
            location = 'na'
        try:
            title = jobcard[counter].find(class_='jobtitle').text

        except AttributeError:
            title = 'na'
        if card.find(class_='ratingsContent'):
            rating_value = jobcard[counter].find(class_='ratingsContent').text
        else:
            rating_value = 'na'
        sleep(2)
        detail_link = 'https://www.indeed.' + dormain_extension + '/viewjob?jk=' + slicedlink + '&q=' + job + 'r&l=' + location + '&tk=1eb18ae331596000&from=web&vjs=3'
        detail_content = requests.get(detail_link)
        detail_soup = BeautifulSoup(detail_content.text, 'html.parser')
        try:
            company = detail_soup.find(class_='jobsearch-InlineCompanyRating').findChild().text
        except AttributeError:
            company = 'na'

        if detail_soup.find(class_='icl-Ratings-count'):
            reviews = detail_soup.find(class_='icl-Ratings-count').text
        else:
            reviews = 'na'

        if detail_soup.find(class_='jobsearch-jobDescriptionText'):
            all_description = detail_soup.find(class_='jobsearch-jobDescriptionText')
            description = all_description.find_all('p')
            ul_description = all_description.find_all('ul')
            div_description = all_description.find_all('div')
            main_text = all_description.text
            des = []
            des2 = []
            divtext = []

            for item in div_description:

                if item.text != '':
                    divtext.append(item.text)
            for item in ul_description:
                li_description = item.find_all('li')
                for i in li_description:
                    des2.append(i.text)
            for item in description:
                des.append(item.text)
        else:
            description = 'na'
        print('rating')
        print(rating_value)
        print('reviews' + reviews)
        print('title' + title)
        print('company' + company)
        print('location' + location)
        print('des')
        print(des)
        print('des2')
        print(des2)
        print('divtext')
        print(divtext)
        print('main description')
        print(main_text)
        review_no = reviews.split(' ')
        number = review_no[0].replace(',', '')
        new_listing = JobListing()
        new_listing.title = title
        new_listing.company = company
        main_des = []
        main_des = des + des2 + divtext
        main_des.append(main_text)
        data_des = ''
        for item in main_des:
            data_des += item
        if rating_value == 'na':
            new_listing.rating_value = 0
        else:
            new_listing.rating_value = rating_value
        if number == 'na':
            new_listing.review_number = 0
        else:
            new_listing.review_number = int(number)
        new_listing.description = data_des
        new_listing.search_cat = gjob
        new_listing.search_loc = glocation
        new_listing.location = location

        jobs = JobListing.objects.all()

        if jobs.filter(Q(title__iexact=title) & Q(company__exact=company) & Q(location__exact=location)):

            print('item is available')

        else:
            new_listing.save()

def main_scraper():
    exten=Extension.objects.all()
    locations=Location.objects.all()
    jobs=Job.objects.all()
    for e in exten:
        for job_item in jobs:
            for loc_item in locations:
                job = job_item.name

                place=loc_item.name
                if e.name=='na':
                    dormain_extension='com'
                else:
                    dormain_extension=e.name

                url = 'https://www.indeed.' + dormain_extension + '/jobs?q=' + job + '&l=' + place
                page = requests.get(url)
                soup = BeautifulSoup(page.text, 'html.parser')

                pagination=soup.find(class_='pagination-list')
                try:
                    links=pagination.find_all('a',href=True)
                except AttributeError:
                    break

                real_link=['']
                for link in links:
                    real_link.append(link['href'])
                for a in real_link:
                    sleep(2)
                    url='https://www.indeed.' + dormain_extension + a
                    page = requests.get(url)
                    soup = BeautifulSoup(page.text, 'html.parser')

                    jobcard = soup.find_all(class_='jobsearch-SerpJobCard')
                    for counter, card in enumerate(jobcard):
                        link = jobcard[counter].findChild().findChild()
                        item_id = link.attrs['id']
                        slicedlink = link.attrs['id'][3:]
                        try:
                            location = jobcard[counter].find(class_='sjcl').find(class_='location').text
                        except AttributeError:
                            location='na'
                        try:
                            title=jobcard[counter].find(class_='jobtitle').text

                        except AttributeError:
                            title='na'
                        if card.find(class_='ratingsContent'):
                            rating_value = jobcard[counter].find(class_='ratingsContent').text
                        else:
                            rating_value = 'na'
                        sleep(2)
                        detail_link = 'https://www.indeed.' + dormain_extension + '/viewjob?jk=' + slicedlink + '&q=' + job + 'r&l=' + location + '&tk=1eb18ae331596000&from=web&vjs=3'
                        detail_content = requests.get(detail_link)
                        detail_soup = BeautifulSoup(detail_content.text, 'html.parser')
                        try:
                            company = detail_soup.find(class_='jobsearch-InlineCompanyRating').findChild().text
                        except AttributeError:
                            company='na'

                        if detail_soup.find(class_='icl-Ratings-count'):
                            reviews = detail_soup.find(class_='icl-Ratings-count').text
                        else:
                            reviews = 'na'

                        if detail_soup.find(class_='jobsearch-jobDescriptionText'):
                            all_description = detail_soup.find(class_='jobsearch-jobDescriptionText')
                            description = all_description.find_all('p')
                            ul_description = all_description.find_all('ul')
                            div_description = all_description.find_all('div')
                            main_text = all_description.text
                            des = []
                            des2 = []
                            divtext = []

                            for item in div_description:

                                if item.text != '':
                                    divtext.append(item.text)
                            for item in ul_description:
                                li_description = item.find_all('li')
                                for i in li_description:
                                    des2.append(i.text)
                            for item in description:
                                des.append(item.text)
                        else:
                            description = 'na'
                        print('rating')
                        print(rating_value)
                        print('reviews' + reviews)
                        print('title' + title)
                        print('company' + company)
                        print('location' + location)
                        print('des')
                        print(des)
                        print('des2')
                        print(des2)
                        print('divtext')
                        print(divtext)
                        print('main description')
                        print(main_text)
                        review_no = reviews.split(' ')
                        number = review_no[0].replace(',', '')
                        new_listing = JobListing()
                        new_listing.title = title
                        new_listing.company = company
                        main_des=[]
                        main_des=des + des2 + divtext
                        main_des.append(main_text)
                        data_des=''
                        for item in main_des:
                            data_des+=item
                        if rating_value == 'na':
                            new_listing.rating_value=0
                        else:
                            new_listing.rating_value = rating_value
                        if number == 'na':
                            new_listing.review_number=0
                        else:
                            new_listing.review_number = int(number)
                        new_listing.description = data_des
                        new_listing.search_cat=loc_item
                        new_listing.search_loc=job_item
                        new_listing.location=location

                        jobs=JobListing.objects.all()

                        if jobs.filter(Q(title__iexact=title) & Q(company__exact=company) & Q(location__exact=location)):

                            print('item is available')

                        else:
                            new_listing.save()
    return 'done'

def populate(request):
    if not request.user.is_authenticated:
        template = 'index.html'
        context = {
            'responce': 'You are have to be loogged in',
            'code': 0
        }
        return render(request, template, context)
    else:
        if request.method == 'POST':
            ds=main_scraper()
            print('dine')
            print(ds)
            template = 'index.html'
            context = {
                'respomce': 'Scraper successively called',
                "code": 0
            }
            return render(request, template, context)
        template = 'index.html'
        context = {

            "code": 0
        }
        return render(request, template, context)

