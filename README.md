# stock-crawler
crawl stocks price from Yahoo Finance

the csv includes shares eligible for short selling, in general it means shares that are more liquid. 
A full list of security can be found here:
https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx

However because the security code in the short sell list is different from that of the fill list, you would have to change the function `crawler` to adapt the stock code for the yahoo finance API.
