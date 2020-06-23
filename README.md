# indeedscraper
This is a vertion of the indeed job scraper
API Reference

The API is organized around REST.The API has predictable resource-oriented URLs, accepts form-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

Authentication

The Stripe API uses API keys to authenticate requests. You can view and manage your API keys in the Stripe Dashboard.

To get an api key you must create a superuser from django terminal of one of use the available superusers in the admin panel.

you can create anew super admin by typing python manage.py createsuperuser in project base directory in a console

The username apiadmin is available with password being secrete1 

Your API keys carry many privileges, so be sure to keep them secure! Do not share your secret API keys in publicly accessible areas such as GitHub, client-side code, and so forth.

To get a new token you just have send a post request to localhost:8000/api/login?username=*your username*&password=*your password*

Authentication to the API is performed via HTTP Basic Auth. Provide your API key as the basic auth username value and password as password value

If you need to authenticate add this to your request url '-H "Authorization: Token *your token goes here* "' instead of -u sk_test_4eC39HqLyjWDarjtT1zdp7dc.

All API requests must be made over HTTPS. Calls made over plain HTTP will fail. API requests without authentication will also fail.

Get request

To get joblistings, you simply have to make a get request to your api url and include ?title=*the job title*&location=*the job location*&ext=*the domain extension of the version of indeed you want to scrape the jobs from eg if it is indeed.com the ext will be'.com', if it indeed.co.in the ext becomes '.co.in'*'

If the get request returns an empty response, a function called scraper will scrape indeed site passing the paramatters provided in the get url and return the results

There is the main spraper function thet will scrape data periodically from the indeed site to populate the database.

If a particular attribute is not available on indeed, the item will be given a value 'na'

To setup the scraper to run periodically you configure celery to work with heroku. Here is a great tutorial on how to do it https://devcenter.heroku.com/articles/celery-heroku
 
The main scraper gets its seach parameters from the database.


Adding a new location 
 
Go into the admin panel>main>Location.

Addd in a city location.The sccraper will scrape for all the jobs in that particular city

Adding a new Job

Go into the admin panel>main>Job.

Add in jobs that you want the scraper to lookout for.

Add a dormain extention

Go into the admin panel>main>Extension

Add a new indeed dormain extention 

The main scrper which is in tasks.py file will iterate throught all the instances available in the Job, Extension and Locatiion model and saves the results in the database. This process takes long no process should depend on it to execute. That is why I created the second scraper function available in views.py.

This one runs for a couple of seconds since it only scrapes data on page one of particular location instance and job instance. This second scraper only runs when there is no results of the queries provided in the database.

As more items are added to the database this second script wil run less frequently.

When setting up celery keep in mind that the task to be added in the queu will the function in tasks.py called main_scraper()

Feel free to ask any questions
