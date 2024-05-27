from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, JsonResponse, HttpRequest

from requests.auth import HTTPBasicAuth
import requests
import os
import utils
import datetime

stock_daily_data_db, client = utils.get_db_handle()
ticker_symbols_db = client["ticker_symbols_db"]

my_premium_api_key = os.environ.get('my-alphavantage-api-premium-key')


''' Get Tickers file from NASDAQ '''
all_active_tickers_collection = ticker_symbols_db["all_active_tickers"]


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "api/home.html")


def search_daily_view(request: HttpRequest) -> HttpResponse:
    parameters = {}
    if request.method == "POST":
        return HttpResponseNotAllowed(['GET'])
    elif request.method == "GET":
        if "ticker" in request.GET:
            parameters["ticker"] = request.GET['ticker']
        else:
            parameters["err_msg"] = "Looks like you did not look up a ticker symbol to get here."

        return render(request, "api/search.html", parameters)


def api_search_daily(request: HttpRequest, ticker: str) -> HttpResponse:
    '''
    This function trys to find historical stock price history for the given ticker
    If the ticker is valid and didn't encounter problem:
        returns JsonResponse - {Symbol, MetaData, api_function, time_series}
    else:
        returns HttpResponseServerError of appropriate message

    '''
    print(f"Called api for ticker {ticker}==============================")

    if not is_valid_ticker(ticker):
        print(f"{ticker} does not exist on NYSE or NASDAQ")
        return HttpResponseServerError(f"Ticker {ticker} does not exist on NYSE or NASDAQ")

    this_stock_collection = stock_daily_data_db[ticker]
    if this_stock_collection.count_documents({}) != 0:
        # fetch the info in collection and send back as json response
        print(f"found {ticker} in db==============================")

        document = this_stock_collection.find_one()

        # update data as needed
        last_update = document["Meta Data"]["3. Last Refreshed"]
        curr_time = datetime.datetime.now()

        if last_update != curr_time.strftime("%Y-%m-%d"):
            alpha_response = fetch_from_alpha(ticker)
            if "Error Message" in alpha_response:
                return HttpResponseServerError(alpha_response["Error Message"])

            # enable this if dont want to have outdated info
            # elif "Information" in alpha_response:
            #     return HttpResponseServerError("Over Alpha API limit")
            if "Information" not in alpha_response:
                # Alpha Vantage limit hit
                print("no problem fetching and update db")
                this_stock_collection.delete_one({"symbol": ticker})
                this_stock_collection.insert_one(alpha_response)
            print(f"updated++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(this_stock_collection.find_one()[
                  "Meta Data"]["3. Last Refreshed"])
            print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        document = this_stock_collection.find_one()
        del document["_id"]
        return JsonResponse(document)

    else:
        # fresh search, need to clone to db
        alpha_response = fetch_from_alpha(ticker)
        if "Error Message" in alpha_response:
            print(f"Error in Alpha response: {alpha_response}")
            return HttpResponseServerError(alpha_response["Error Message"])
        elif "Information" in alpha_response:
            print(f"Over Alpha API limit: {alpha_response}")
            return HttpResponseServerError("Over Alpha API limit")
        # Try to save response into db
        try:
            # Collection : [Symbol, Meta, api_function, time_series]
            print("Saving response into db====================================")
            # print(alpha_response["_id"])

            this_stock_collection.insert_one(alpha_response)
            del alpha_response["_id"]
            return JsonResponse(alpha_response)

        except Exception as e:
            print("Insertion Error*****************************************")
            print(f"Failed to insert due to: {e}")
            print("********************************************************")
            return HttpResponseServerError(f"Internal error while try to save data")


def fetch_from_alpha(ticker: str) -> dict:
    '''
    this function tries to fetch daily info about ticker from Alpha Vantage
    returns:
        if ticker is valid:
            dict - that represents json response received from Alpha Vantage for 'ticker'
        if ticker is not valid or Alpha Vantage server down
            returns a dict in the format of {"Error Message": reason it failed}
    '''

    api_url = 'https://www.alphavantage.co/query'
    parameters = {
        # 'function': 'TIME_SERIES_DAILY',
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': ticker,
        'outputsize': 'full',  # Optional parameter compact/full
        'datatype': 'json',    # Optional parameter
        'apikey': my_premium_api_key,
    }

    response = requests.get(url=api_url, params=parameters)
    print(f"in alpha fetch: {response.url}")

    if response.status_code != 200:
        # API end point returns status code 200 despite having invalid parameter into API calls,
        # so whenever the status_code != 200 means their server is down
        print("Alpha server down!====================================")
        print(response.json())
        print("======================================================")

        return {"Error Message": "Failed to retrieve data because Alpha Server down!"}

    json_response = response.json()

    if "Error Message" in json_response:
        # API parameters are wrong, meaning the ticker symbol is wrong
        error_msg = json_response["Error Message"]
        print("API ERROR!====================================")
        print(json_response["Error Message"])
        print("==============================================")
        return json_response
    if "Information" in json_response:
        print("API info ERROR!===============================")
        print(json_response["Information"])
        print("==============================================")
        return json_response

    # Successfully called the API
    json_response['symbol'] = parameters['symbol']
    json_response['api_function'] = parameters['function']
    return json_response


def api_is_valid_ticker(request: HttpRequest, ticker: str) -> bool:
    data = {
        'response': is_valid_ticker(ticker)
    }
    print("api_is_valid_ticker=================================")
    print(data)
    print("====================================================")
    return JsonResponse(data)


def is_valid_ticker(ticker: str) -> bool:
    """
    check if the ticker is an active ticker using the list of all active ticker in db
    returns true if it is an active ticker, false if otherwise
    """
    # TODO: grab active data online

    ticker_in_db = all_active_tickers_collection.find_one({'symbol': ticker})
    return ticker_in_db != None


'''
#TODO
grab company fundamental data
grab fed data 
implement multiple API provider for more data lookup (need to adjust to each API)
Stock price doesn't consider stock split

FAR INTO FUTURE:
    Neutral Network to predict data using stock price and eco data
    Train LLM to digest earnings report, and FOMC release
'''

'''
#DONE
Scarp data from API
Store API into local mongodb
API call failure handle
Display Data on screen (prefer to be a graph)
Options for display data (daily, 1 month, range)
Adjust the range selection based on time not trade days
update db to newest data
separate api call better
'''
