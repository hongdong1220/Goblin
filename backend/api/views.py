from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError, JsonResponse, HttpRequest

from requests.auth import HTTPBasicAuth
import requests
import os
import utils
import datetime

stock_daily_data_db, client = utils.get_db_handle()
ticker_symbols_db = client["ticker_symbols_db"]

myapikey = os.environ.get('my_alphavantage_api_key')
auth = HTTPBasicAuth('apikey', myapikey)

'''
    Get Tickers file from NASDAQ

'''

nasdaq_tickers_csv_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&exchange=NASDAQ&download=true"
nyse_tickers_csv_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&exchange=NYSE&download=true"

'''
    Google Chart
    IBM:
        1D: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:1d,interval:300,extended:true,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        5D: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:5d,interval:1800,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        1M: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:1M,interval:86400,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        6M: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:6M,interval:86400,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        YTD: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:YTD,interval:86400,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        1Y: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:1Y,interval:86400,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        5Y: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:5Y,interval:604800,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
        Max: https://www.google.com/async/finance_wholepage_chart?ei=S_83ZtucOJrP0PEPrJaD6As&opi=89978449&yv=3&cs=1&async=mid_list:%2Fm%2F07zlw9w,period:40Y,interval:604800,extended:false,lang:,_id:fw-_S_83ZtucOJrP0PEPrJaD6As_49,_pms:s,_fmt:pc
    SPY:
        1D: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:1d,interval:300,extended:true,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        5D: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:5d,interval:1800,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        1M: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:1M,interval:86400,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        6M: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:6M,interval:86400,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        YTD: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:YTD,interval:86400,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        1Y: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:1Y,interval:86400,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        5Y: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:5Y,interval:604800,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
        Max: https://www.google.com/async/finance_wholepage_chart?ei=UAQ4Zr72MKH80PEP_aiZuAM&opi=89978449&sca_esv=2c6693827cfe3781&yv=3&cs=1&async=mid_list:%2Fg%2F1q62h0x10,period:40Y,interval:604800,extended:false,lang:,_id:fw-_UAQ4Zr72MKH80PEP_aiZuAM_49,_pms:s,_fmt:pc
'''


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "api/home.html")


def search_daily_view(request: HttpRequest):
    if request.method == "POST":
        return render(request, "api/search.html",
                      {
                          'ticker': request.POST['ticker'],
                      })
    else:
        return render(request, "api/search.html")


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
            return HttpResponseServerError(alpha_response["Error Message"])

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
            dict - that represents json response received from Alpha Vantage for 'tiker'
        if ticker is not valid or Alpha Vantage server down
            returns a dict in the format of {"Error Message": reason it failed}
    '''

    # #Demo Param
    # parameters = {
    #     # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo
    #     'function': 'TIME_SERIES_DAILY',
    #     'symbol': 'IBM',
    #     'apikey': 'demo'           # Using the auth variable to include the API key
    # }

    api_url = 'https://www.alphavantage.co/query'
    parameters = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'outputsize': 'full',  # Optional parameter compact/full
        'datatype': 'json',    # Optional parameter
        'apikey': auth
    }

    response = requests.get(url=api_url, params=parameters)

    if response.status_code != 200:
        # API end point returns status code 200 despite having invalid parameter into API calls,
        # so whenever the status_code != 200 means their server is down
        print("Alpha server down!====================================")
        return {"Error Message": "Failed to retrieve data because Alpha Server down!"}

    json_response = response.json()

    if "Error Message" in json_response:
        # API parameters are wrong, meaning the ticker symbol is wrong
        error_msg = json_response["Error Message"]
        print("API ERROR!====================================")
        print(json_response["Error Message"])
        print("==============================================")
        return json_response

    # Successfully called the API
    json_response['symbol'] = parameters['symbol']
    json_response['api_function'] = parameters['function']
    return json_response


def is_valid_ticker(ticker: str) -> bool:
    """
    check if the ticker is in NYSE or NASDAQ
    returns true if it exist on NYSE or NASDAQ, false if otherwise
    """

    # try to look for it in db,
    #     if yes
    #         return true,
    #     else
    #         update db (download from web and parse it) then check
    nyse_collection = ticker_symbols_db["NYSE"]
    nasdaq_collection = ticker_symbols_db["NASDAQ"]

    in_nyse = nyse_collection.find_one({'Symbol': ticker})
    in_nasdaq = nasdaq_collection.find_one({'Symbol': ticker})

    return in_nyse or in_nasdaq


'''
#TODO
separate api call better
grab company fundamental data
grab fed data 
implement multiple API provider for more data lookup (need to adjust to each API)
maybe make table span multiple pages
Stock price doesn't consider stock split
implement front-end into using react

FAR INTO FUTURE: Train LLM using data
'''

'''
#DONE
Scarp data from API
Store API into local mongodb
API call failure handle
Display Data on screeen (perfer to be a graph)
Options for display data (daily, 1 month, range)
Adjust the range selection based on time not trade days
update db to newest data

'''
