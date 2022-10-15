import pandas as pd
import requests
from persiantools.jdatetime import JalaliDate
import re
import logging
import threading
import pickle

# %%
def get_stock_detail(stock_id):
    try:
        # If you replace {} with a stock ID in this URL, you can access that stocks page in tsetmc.com.
        logging.captureWarnings(True)
        url = "http://www.tsetmc.com/Loader.aspx?ParTree=151311&i={}".format(stock_id)
        r = requests.get(url, timeout=1, verify=False)
        #     print(url)

        # We get stock details in stock page (text of page) hear:
        stock = {"stock_id": stock_id}
        stock["group_name"] = re.findall(r"LSecVal='([\D]*)',", r.text)[0]
        stock["instId"] = re.findall(r"InstrumentID='([\w\d]*)',", r.text)[0]
        stock["insCode"] = (
            stock_id if re.findall(r"InsCode='(\d*)',", r.text)[0] == stock_id else 0
        )
        stock["baseVol"] = float(re.findall(r"BaseVol=([\.\d]*),", r.text)[0])
        try:
            stock["name"] = re.findall(r"LVal18AFC='([\D]*)',", r.text)[0]
        except:
            return
        try:
            stock["title"] = re.findall(r"Title='([\D]*)',", r.text)[0]
        except:
            return
        try:
            stock["sectorPe"] = float(re.findall(r"SectorPE='([\.\d]*)',", r.text)[0])
        except:
            stock["sectorPe"] = None
        try:
            stock["shareCount"] = float(re.findall(r"ZTitad=([\.\d]*),", r.text)[0])
        except:
            stock["shareCount"] = None

        try:
            stock["estimatedEps"] = float(
                re.findall(r"EstimatedEPS='([\.\d]*)',", r.text)[0]
            )
        except:
            stock["estimatedEps"] = None
        if stock["name"] == "',DEven='',LSecVal='',CgrValCot='',Flow='',InstrumentID='":
            return False
    except:
        # print("Again stock detail ", stock_id)
        stock = get_stock_detail(stock_id)
    return stock


def clean_adjusted_price(r):
    if r.text == "":
        return []
    history = []
    for item in r.text.split(";"):
        item_list = item.split(",")
        history_item = {}
        history_item["date"] = item_list[0]
        history_item["jalaliDate"] = JalaliDate.to_jalali(
            int(item_list[0][0:4]), int(item_list[0][4:6]), int(item_list[0][6:8])
        ).isoformat()
        history_item["max_price"] = item_list[1]
        history_item["min_price"] = item_list[2]
        history_item["open_price"] = item_list[3]
        history_item["last_price"] = item_list[4]
        history_item["volume"] = item_list[5]
        history_item["close_price"] = item_list[6]
        history.append(history_item)
    return history


def clean_unadjusted_price(r):
    price_history_list = r.text.split(";")
    history = list()
    for item in price_history_list:
        item_list = item.split("@")
        if len(item_list) < 3:
            break
        history_item = {}
        history_item["date"] = item_list[0]
        history_item["jalaliDate"] = JalaliDate.to_jalali(
            int(item_list[0][0:4]), int(item_list[0][4:6]), int(item_list[0][6:8])
        ).isoformat()
        history_item["max_price"] = item_list[1]
        history_item["min_price"] = item_list[2]
        history_item["close_price"] = item_list[3]
        history_item["last_price"] = item_list[4]
        history_item["open_price"] = item_list[5]
        history_item["yesterday_price"] = item_list[6]
        history_item["value"] = item_list[7]
        history_item["volume"] = item_list[8]
        history_item["quantity"] = item_list[9]
        history.append(history_item)
    return history


def crawl_prices(id):
    url = r"https://members.tsetmc.com/tsev2/chart/data/Financial.aspx?i={}&t=ph&a={}"
    url1 = url.format(id, 0)  # Adjusted prices
    r1 = requests.get(url1, timeout=10, verify=False)
    t1 = clean_adjusted_price(r1)
    url = r"https://members.tsetmc.com/tsev2/chart/data/Financial.aspx?i={}&t=ph&a={}"
    url = "http://members.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={}&Top=999999&A={}"
    url1 = url.format(id, 1)  # UnAdjusted prices
    r = requests.get(url1.format(id), timeout=10, verify=False)
    t0 = clean_unadjusted_price(r)

    if t1 == []:
        df = pd.DataFrame.from_dict(t0)
    else:
        df = pd.DataFrame.from_dict(t0).merge(
            pd.DataFrame.from_dict(t1),
            on=["date", "jalaliDate", "volume"],
            how="left",
            suffixes=("", "_Adjusted"),
        )
    stock_detail = get_stock_detail(id)
    if type(stock_detail) != type({}):
        return pd.DataFrame()
    l = ["sectorPe", "shareCount", "estimatedEps", "insCode"]
    for i in stock_detail:
        if i in l:
            continue
        df[i] = stock_detail[i]

    return df


Id = pd.read_pickle(r"Get all ids\\ids_Current_added_group.p")


object = pd.read_pickle(r"Get all ids\\ids_all.p")
for i in object:
    Id.append(i)
Id = list(set(Id))
Id.sort()

#%%
'17617474823279712' in Id

#%%

path = r"E:\RA_teias\Data\Price\\"

def gen_price(path, stock_id, error, i):
    try:
        t = crawl_prices(stock_id)
        if i is not None:
            pickle.dump(t, open(path + str(stock_id) + ".p", "wb"))
        # print(i, "Done")
    except:
        error.append(stock_id)
        # print(i, "Error")


#%%
def excepthook(args):
    3 == 1 + 2

threading.excepthook = excepthook
Data = pd.DataFrame()

def Crawl_all(path, Id, m):
    counter = 0
    error = []
    threads = {}
    # result = [None] * len(Id)
    for i, stock_id in enumerate(Id):
        counter += 1
        print(counter, len(Id), stock_id, i)
        threads[i] = threading.Thread(target=gen_price, args=(path, stock_id, error, i))
        threads[i].start()
        if i == 1:
            continue
        if i % m == 1:
            for j in range(m + 2):
                threads[i - j].join()
    for i in threads:
        threads[i].join()
    print("Done")
    return error

error = Crawl_all(path, Id, 200)
#%%
for i in [200,100, 100, 50, 10, 5,2,2]:
    print("-------------{}---------------".format(len(error)))
    error = Crawl_all(path, error, i)
    print("-------------{}---------------".format(len(error)))

#%%
import os

Data = pd.DataFrame()
arr = os.listdir(path)
for i, name in enumerate(arr):
    print(i, len(Data))
    i = pd.read_pickle(path + name)
    if i is not None:
        Data = Data.append(i)


#%%

path = r"E:\RA_teias\Data\\"
name = "Stock_Prices_1400_10_07"
print(len(Data))
Data.to_parquet(path + name + ".parquet")
#%%
len(Data.name.unique())

#%%
path = r"E:\RA_teias\Data\\"
name = "Stock_Prices_1400_10_07"
Data = pd.read_parquet(path + name + ".parquet")
print(len(Data))
#%%
df = pd.read_parquet(path + "Stock_Prices_1400_06_29.parquet")
Data = Data[Data.date <= df.date.max()]
# %%
len(df), len(Data)
# %%
df.groupby("name").count()


# %%
Data.groupby("name").count()

#%%
list(set(Data.name.unique()) - set(df.name.unique()))
# set(df.name.unique()) - set(Data.name.unique())
#%%
Data[Data.stock_id == 17617474823279712]