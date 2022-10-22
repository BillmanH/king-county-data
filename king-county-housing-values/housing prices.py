# %%
# Get housing price info.
import re
import pandas as pd
import urllib
from bs4 import BeautifulSoup as bs
import yaml
import requests
import os


# %%
# Loading the config file
params = yaml.safe_load(open('config.yaml'))


# %%
with open(os.path('data',params['parcel_numbers']) as f:
    lines = f.read().splitlines()

URL_ParcelNumberQuery = r"https://blue.kingcounty.com/Assessor/eRealProperty/Dashboard.aspx?ParcelNbr={}"
# https://blue.kingcounty.com/Assessor/eRealProperty/Dashboard.aspx?ParcelNbr=9478110220
# Iterating over a list of parcel numbers
# this is if you just copy and pasted the list from:
# http://info.kingcounty.gov/Assessor/eRealProperty/default.aspx

# %%

r = requests.get(url.format(parcel))
soup = bs(r.text, 'html.parser')


def get_list_of_parcels(lines, url):

    for parcel in lines:
        print(parcel, end=":")
        page = urllib.request.urlopen(url.format(parcel))
        myhtml = page.read().decode('utf-8')
        soup = bs(myhtml)
        tables = soup.find_all('table')
        if len(tables) == 8:
            condo_table = pd.read_html(str(tables), header=0)[6]
            # some wierd thing with the secial characters in the HTML:
            condo_table.Parcel = condo_table.Parcel.apply(
                lambda x: "".join([letter for letter in x if letter in "1234567890"]))
            condo_table.index = condo_table.Parcel
            print(condo_table)
        else:
            tmpDF = pd.read_html(str(tables[-1]), header=0)[0]
            tmpDF.index = tmpDF['Valued Year']
            tdc = tmpDF['Taxable Total ($)'].to_dict()
            for item in tdc:
                condo_table.loc[parcel, item] = tdc[item]
            print(condo_table.ix[parcel, 'Taxpayer Name'])

    return condo_table


df = get_list_of_parcels(lines, URL_ParcelNumberQuery)


# %%
# flip it for working with the time as index:
condo_table2 = condo_table.copy()
condo_table2.index = condo_table2['Unit Number']
# just the dates as columns:
condo_table2 = condo_table2[[col for col in condo_table2.columns
                             if str(col).isdigit()]].T.sort_index(ascending=False)


# then Save it to excel:
writer = pd.ExcelWriter(
    r'C:\Users\Bill\Desktop\Housing Prices\condo_table.xlsx')
condo_table[condo_table.columns[:4]].to_excel(
    writer, 'condo_table', encoding='utf-8')
condo_table2.to_excel(writer, 'change in price over year', encoding='utf-8')
writer.save()


# however if you want know the building's parcel numbers
# when I build this into my website, I'll use this function.
# you can just enter it here:
parcel = '0255600000'


def get_unit_parcels_owneres(parcel):
    page = urllib.urlopen(url.format(parcel))
    myhtml = page.read().decode('utf-8')
    soup = bs(myhtml)
    tables = soup.find_all('table')
    condo_table = pd.read_html(str(tables), header=0)[6]
    return condo_table

# this part not yet completed :)
