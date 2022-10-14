#%%
import pandas as pd
import numpy as np
import re
import statsmodels.api as sm

# import finance_byu.rolling as rolling
import requests
import pandas as pd
from bs4 import BeautifulSoup
import math

#%%
def convert_ar_characters(input_str):

    mapping = {
        "ك": "ک",
        "گ": "گ",
        "دِ": "د",
        "بِ": "ب",
        "زِ": "ز",
        "ذِ": "ذ",
        "شِ": "ش",
        "سِ": "س",
        "ى": "ی",
        "ي": "ی",
    }
    return _multiple_replace(mapping, input_str)


def _multiple_replace(mapping, text):
    pattern = "|".join(map(re.escape, mapping.keys()))
    return re.sub(pattern, lambda m: mapping[m.group()], str(text))


def vv(row):
    X = row.split("-")
    return int(X[0] + X[1] + X[2])


def vv2(row):
    X = row.split("/")
    return int(X[0] + X[1] + X[2])


def addDash(row):
    row = str(row)
    X = [1, 1, 1]
    X[0] = row[0:4]
    X[1] = row[4:6]
    X[2] = row[6:8]
    return X[0] + "-" + X[1] + "-" + X[2]


def removeSlash(row):
    X = row.split("/")
    if len(X[1]) < 2:
        X[1] = "0" + X[1]
    if len(X[2]) < 2:
        X[2] = "0" + X[2]
    return int(X[0] + X[1] + X[2])


def removeSlash2(row):
    X = row.split("/")
    if len(X[1]) < 2:
        X[1] = "0" + X[1]
    if len(X[0]) < 2:
        X[0] = "0" + X[0]

    return int(X[2] + X[0] + X[1])


def removeDash(row):
    X = row.split("-")
    if len(X[1]) < 2:
        X[1] = "0" + X[1]
    if len(X[2]) < 2:
        X[2] = "0" + X[2]
    return int(X[0] + X[1] + X[2])


path = r"G:\Economics\Finance(Masoud.-teias)\Data\\"
path = r"E:\RA_teias\Data\\"
#%%
def group_id():
    r = requests.get(
        "http://www.tsetmc.com/Loader.aspx?ParTree=111C1213"
    )  # This URL contains all sector groups.
    soup = BeautifulSoup(r.text, "html.parser")
    header = soup.find_all("table")[0].find("tr")
    list_header = []
    for items in header:
        try:
            list_header.append(items.get_text())
        except:
            continue

    # for getting the data
    HTML_data = soup.find_all("table")[0].find_all("tr")[1:]
    data = []
    for element in HTML_data:
        sub_data = []
        for sub_element in element:
            try:
                sub_data.append(sub_element.get_text())
            except:
                continue
        data.append(sub_data)
    df = pd.DataFrame(data=data, columns=list_header).rename(
        columns={"گروه های صنعت": "group_name", "کد گروه های صنعت": "group_id"}
    )
    return df


groupnameid = group_id()
groupnameid["group_id"] = groupnameid.group_id.apply(lambda x: x.strip())
#%%
def Overall_index():
    url = (
        r"http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i=32097828799138957&t=value"
    )
    r = requests.get(url)
    jalaliDate = []
    Value = []
    for i in r.text.split(";"):
        x = i.split(",")
        jalaliDate.append(x[0])
        Value.append(float(x[1]))
    df = pd.DataFrame(
        {
            "jalaliDate": jalaliDate,
            "Value": Value,
        },
        columns=["jalaliDate", "Value"],
    )
    return df


# overal_index = Overall_index()

# %%
pdf = pd.read_parquet(path + "Stock_Prices_1401_02_25.parquet")
print(len(pdf))


col = "group_name"
pdf[col] = pdf[col].apply(lambda x: convert_ar_characters(x))
groupnameid[col] = groupnameid[col].apply(lambda x: convert_ar_characters(x))
pdf[col] = pdf.group_name.str.replace("',CgrValCot='ET", "", regex=False)
pdf[col] = pdf.group_name.str.replace("',CgrValCot='QA", "", regex=False)
pdf[col] = pdf.group_name.str.replace("',CgrValCot='EQ", "", regex=False)
pdf[col] = pdf.group_name.str.replace("',CgrValCot='QT", "", regex=False)
mapdict = dict(zip(groupnameid.group_name, groupnameid.group_id))
pdf["group_id"] = pdf.group_name.map(mapdict)
list(pdf[pdf.group_id.isnull()]["group_name"].unique())
#%%

pdf["name"] = pdf.name.apply(lambda x: x.strip())
pdf["name"] = pdf["name"].apply(lambda x: convert_ar_characters(x))
pdf["title"] = pdf.title.apply(lambda x: x.strip())
pdf["title"] = pdf.title.apply(lambda x: convert_ar_characters(x))
pdf.jalaliDate = pdf.jalaliDate.apply(vv)
pdf = pdf.sort_values(by=["name", "date"])
pdf["title"] = pdf.title.str.replace(",FaraDesc ='", "")
pdf["title"] = pdf.title.str.replace("\u200c", "")
pdf["name"] = pdf.name.str.replace("\u200c", "")

#%%

pdf = pdf[~(pdf.name.str.endswith("پذيره"))]
pdf = pdf[~((pdf.group_name.str.contains("غیرفعال")))]
pdf = pdf[
    ~(
        (pdf.title.str.contains("سپرده"))
        | (pdf.title.str.contains("غیرفعال"))
        | (pdf.title.str.contains("نماد تستی"))
        | (pdf.title.str.contains("پذیره"))
        | (pdf.title.str.contains("حذف"))
        | (pdf.title.str.contains("پرداخت شده"))
        | ((pdf.title.str.contains("50%")) & (pdf.title.str.contains("تادیه")))
        | ((pdf.title.str.contains("70%")) & (pdf.title.str.contains("تادیه")))
        | ((pdf.title.str.contains("35%")) & (pdf.title.str.contains("تادیه")))
        | ((pdf.title.str.contains("20%")) & (pdf.title.str.contains("تادیه")))
        | ((pdf.title.str.contains("40%")) & (pdf.title.str.contains("تادیه")))
    )
]
#%%
pdf["market"] = pdf.title.apply(lambda x: x.split("-")[-1].replace("'", "").strip())
#%%
Options = [
    "اختیارف",
    "اختیار",
]
for i in Options:
    pdf.loc[(pdf.title.str.contains(i)), "market"] = "بازار ابزارهای مشتقه"
pdf.loc[
    (pdf.name.str.contains("اخزا"))
    & (pdf.group_name == "اوراق تامین مالی")
    & (pdf.market != "بازار ابزارهای مشتقه"),
    "market",
] = "بازار ابزارهای نوین مالی فرابورس"

pdf.loc[((pdf.title.str.contains("صکوک"))), "market"] = "بازار اوراق بدهی"

pdf.loc[
    (pdf.title.str.contains("اجاره")) & (pdf.group_name == "اوراق تامین مالی"), "market"
] = "بازار ابزارهای نوین مالی فرابورس"

pdf.loc[
    pdf.group_name == "صندوق سرمایه گذاری قابل معامله", "market"
] = "صندوق سرمایه گذاری قابل معامله"
pdf.loc[
    (pdf.title.str.contains("منفعت")) & (pdf.market == ""), "market"
] = "بازار اوراق بدهی"
pdf.loc[
    (pdf.title.str.contains("مرابحه")) & (pdf.market == ""), "market"
] = "بازار اوراق بدهی"


pdf.loc[
    pdf.group_name == "اوراق حق تقدم استفاده از تسهیلات مسکن", "market"
] = "بازار ابزارهای نوین مالی فرابورس"
pdf.loc[
    (pdf.title.str.contains("مشارکت")) & (pdf.market == ""), "market"
] = "بازار اوراق بدهی"
pdf.loc[
    (pdf.title.str.contains("سلف"))
    & (pdf.title.str.contains("بنزین"))
    & (pdf.market == ""),
    "market",
] = "بورس کالا"
pdf.loc[
    (pdf.title.str.contains("سلف"))
    & (pdf.title.str.contains("متانول"))
    & (pdf.market == ""),
    "market",
] = "بورس کالا"
pdf.loc[
    (pdf.title.str.contains("سلف"))
    & (pdf.title.str.contains("برق"))
    & (pdf.market == ""),
    "market",
] = "بورس انرژی"
pdf.loc[
    (pdf.title.str.contains("گواهی"))
    & (pdf.title.str.contains("سیمان"))
    & (pdf.market == ""),
    "market",
] = "بورس کالا"
pdf.loc[
    (pdf.title.str.contains("گواهی"))
    & (pdf.title.str.contains("شیشه"))
    & (pdf.market == ""),
    "market",
] = "بورس کالا"
pdf.loc[(pdf.name.str[-1] == "2"), "market"] = "بازار خرده فروشی بورس"
pdf.loc[(pdf.name.str[-1] == "3"), "market"] = "بازار جبرانی بورس"
pdf.loc[(pdf.name.str[-1] == "4"), "market"] = "بازار معاملات عمده بورس"

#%%
# pd.set_option("display.max_rows",None)
pdf[pdf.market == ""][["name", "market", "title", "group_name"]].drop_duplicates()

#%%
pdf = pdf[pdf.market != ""]
print(len(pdf))
#%%
pdf.loc[(pdf.date >= '20220410')&(pdf.name == 'فولاد')][
    [
        'name','date','close_price','close_price_Adjusted','volume'
    ]
].head(25)

#%%
for i in [
    "max_price_Adjusted",
    "min_price_Adjusted",
    "open_price_Adjusted",
    "last_price_Adjusted",
    "close_price_Adjusted",
]:
    print(i)
    pdf[i] = pdf[i].fillna(value=np.nan)
    pdf[i] = pdf.groupby("name")[i].transform(lambda x: x.fillna(method="ffill"))
    # pdf[i] = pdf.groupby("name")[i].transform(lambda x: x.fillna(method="bfill"))
#%%
pdf.loc[(pdf.date >= '20220410')&(pdf.name == 'فولاد')][
    [
        'name','date','close_price','close_price_Adjusted'
    ]
].head(25)
#%%
symbolGroup = pdf[["name", "group_name", "group_id"]].drop_duplicates(
    subset=["name", "group_name", "group_id"]
)

symbolGroup.to_excel(path + "SymbolGroup.xlsx", index=False)
#%%
shrout = pd.read_csv(path + "SymbolShrout_1400_11_27.csv")[["name", "date", "shrout"]]
mapdict = dict(zip(shrout.set_index(["name", "date"]).index, shrout.shrout))
i = "date"
pdf[i] = pdf[i].astype(int)

pdf["shrout"] = pdf.set_index(["name", "date"]).index.map(mapdict)
i = "volume"
pdf[i] = pdf[i].astype(float)
d = pd.DataFrame()
d = d.append(pdf)
d["shrout"] = d.groupby("name")["shrout"].transform(lambda x: x.fillna(method="bfill"))
d["shrout"] = d.groupby("name")["shrout"].transform(lambda x: x.fillna(method="ffill"))

#%%
pdf = pd.DataFrame()
pdf = pdf.append(d)

i = "group_id"
pdf[i] = pdf[i].astype(float)
i = "close_price"
pdf[i] = pdf[i].astype(float)
i = "quantity"
pdf[i] = pdf[i].astype(float)
i = "close_price_Adjusted"
pdf[i] = pdf[i].astype(float)


gg = pdf.groupby(["name"])
for i in range(-5, 6):
    pdf["Volume({})".format(-i)] = gg.volume.shift(i)
    pdf["price({})".format(-i)] = gg.close_price.shift(i)

# for i in ["last_price", "open_price", "value", "quantity", "volume"]:
#     print(i)
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
#     # pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(2)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(2)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-3)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(3)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(4)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(4)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-4)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
#     pdf.loc[(pdf["Volume(-4)"] == 0) & (pdf["Volume(2)"] == 0), i] = 0


# pList = [1.0, 1000.0, 100.0, 10.0]
# pdf = pdf[~((pdf.close_price.isin(pList)) & (pdf.volume == 0))]

# pdf["close"] = pdf.close_price / pdf.AdjustFactor
gg = pdf.groupby(["name"])
pdf["return"] = gg.close_price_Adjusted.pct_change() * 100
pdf["MarketCap"] = pdf.close_price * pdf.shrout
pdf["yclose"] = gg.close_price_Adjusted.shift()


i = "return"
pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(2)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(2)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-3)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(3)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(4)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(4)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-4)"] == 0) & (pdf["Volume(1)"] == 0), i] = 0
pdf.loc[(pdf["Volume(-4)"] == 0) & (pdf["Volume(2)"] == 0), i] = 0
# pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["price(-1)"].isin(pList)), i] = 0


# gg = pdf.groupby(["name"])
# for i in [
#     "max_price_Adjusted",
#     "min_price_Adjusted",
#     "open_price_Adjusted",
#     "last_price_Adjusted",
#     "close_price_Adjusted",
#     "close_price",
#     "last_price",
#     "open_price",
#     "yesterday_price",
# ]:
#     print(i)
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(1)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(1)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(1)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(2)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(2)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-3)"] == 0) & (pdf["Volume(1)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(3)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["Volume(4)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-2)"] == 0) & (pdf["Volume(4)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-4)"] == 0) & (pdf["Volume(1)"] == 0), i] = np.nan
#     pdf.loc[(pdf["Volume(-4)"] == 0) & (pdf["Volume(2)"] == 0), i] = np.nan
#     # pdf.loc[(pdf["Volume(-1)"] == 0) & (pdf["price(-1)"].isin(pList)), i] = np.nan

pdf = pdf.drop(
    columns=[
        "Volume(5)",
        "price(5)",
        "Volume(4)",
        "price(4)",
        "Volume(3)",
        "price(3)",
        "Volume(2)",
        "price(2)",
        "Volume(1)",
        "price(1)",
        "Volume(0)",
        "price(0)",
        "Volume(-1)",
        "price(-1)",
        "Volume(-2)",
        "price(-2)",
        "Volume(-3)",
        "price(-3)",
        "Volume(-4)",
        "price(-4)",
        "Volume(-5)",
        "yclose",
        "price(-5)",
        "yclose",
    ]
)
pdf.describe()

#%%
pdf[pdf.name == 'جم4']
# %%
for i in [
    "max_price",
    "min_price",
    "close_price",
    "last_price",
    "open_price",
    "value",
    "volume",
    "quantity",
    "max_price_Adjusted",
    "min_price_Adjusted",
    "open_price_Adjusted",
    "last_price_Adjusted",
    "close_price_Adjusted",
]:
    pdf[i] = pdf[i].astype(float)
# %%
pdf[(pdf.name == "ومشان") & (pdf.jalaliDate > 13980104)][
    ["jalaliDate", "close_price", "close_price_Adjusted"]
].head(20)

#%%
# gg = pdf.groupby(["name"])
# for i in [
#     # "max_price",
#     # "min_price",
#     "close_price",
#     # "last_price",
#     # "open_price",
#     "max_price_Adjusted",
#     "min_price_Adjusted",
#     "open_price_Adjusted",
#     "last_price_Adjusted",
#     "close_price_Adjusted",
# ]:
#     print(i)
#     pdf[i] = gg[i].transform(lambda x: x.fillna(method="bfill"))
#%%
firstDate_df = pdf[pdf.volume > 0].sort_values(by = ['date']).groupby("name").first()[['jalaliDate']]
mapingdict = dict(zip(firstDate_df.index,firstDate_df.jalaliDate))
pdf['firstDate'] = pdf.name.map(mapingdict)
#%%
pdf[(pdf.name == "ومشان") & (pdf.jalaliDate > 13980104)][
    ["jalaliDate", "close_price", "close_price_Adjusted",'return','volume','firstDate']
].head(20)

#%%
print(len(pdf.name.unique()))
len(pdf[pdf.jalaliDate>= pdf.firstDate].name.unique())
#%%
#%%
list(pdf[pdf.close_price.isnull()][["name", "return", "date"]].name.unique())
#%%
list(pdf[pdf.close_price_Adjusted.isnull()][["name", "return", "date"]].name.unique())
#%%
pdf = pdf[~pdf.close_price.isnull()]
#%%
pdf[pdf.shrout.isnull()][["name", "return", "date"]].name.unique()
#%%
list(pdf)
#%%
pdf = pdf[
    ~(
        (
        (pdf.close_price == 1000.0)
        & ((pdf.yesterday_price == 1000.0) | (pdf.yesterday_price.isnull()))
    )
    | (
        (pdf.close_price == 100.0)
        & ((pdf.yesterday_price == 100.0) | (pdf.yesterday_price.isnull()))
    )
    | (
        (pdf.close_price == 10.0)
        & ((pdf.yesterday_price == 10.0) | (pdf.yesterday_price.isnull()))
    )
    | (
        (pdf.close_price == 1.0)
        & ((pdf.yesterday_price == 1.0) | (pdf.yesterday_price.isnull()))
    )| (
        (pdf.volume == 0.0)
        & (pdf.yesterday_price.isnull())
    )| (
        (pdf.volume == 0.0)
        & (pdf.close_price  == 1000.0)
    )| (
        (pdf.volume == 0.0)
        & (pdf.close_price  == 100.0)
    )| (
        (pdf.volume == 0.0)
        & (pdf.close_price  == 10.0)
    )| (
        (pdf.volume == 0.0)
        & (pdf.close_price  == 10.0)
    )| (
        (pdf.volume == 0.0)
        & (pdf.close_price  == 1)
    )
    )
]

#%%
pdf[ (
         ~(pdf.yesterday_price.isnull())#(pdf.close_price == 5.0)
        # & ((pdf.yesterday_price == 100.0) | (pdf.yesterday_price.isnull()))
    )][['name','date','close_price','yesterday_price','volume']]

#%%
pdf[(pdf.name == 'جم4')&(pdf.jalaliDate>= 13991227)][['volume','jalaliDate']]
#%%
pdf.to_parquet(
    path
    + "Cleaned_Stock_Prices_{}".format(
        pdf[pdf.date == pdf.date.max()].jalaliDate.iloc[0]
    )
    + ".parquet"
)
# %%
pdf.isnull().sum()
list(
    pdf[
        (pdf.MarketCap.isnull())
        & (~((pdf.title.str.startswith("ح")) & (pdf.name.str.endswith("ح"))))
        & (pdf.group_name != "اوراق حق تقدم استفاده از تسهیلات مسکن")
        & (pdf.group_name != "اوراق تامین مالی")
        & (~pdf.instId.str.startswith("IRK"))
        & (~pdf.title.str.startswith("سپرده"))
        & (~pdf.title.str.startswith("ح"))
        & (~pdf.title.str.contains("اختيارخ"))
        & (~pdf.title.str.contains("اختيارف"))
        & (~pdf.title.str.contains("اختيار"))
        & (~pdf.title.str.contains("آتي"))
    ].name.unique()
)
#%%
pdf[pdf.name == "انرژیح1"].title.unique()
pdf[pdf.title.str.startswith("ح")].name.unique()
pdf[pdf.name == "های وب"].MarketCap.unique()

# %%

path = r"E:\RA_teias\Data\\"
# path = r"G:\Economics\Finance(Masoud.-teias)\Data\\"
# df = pd.read_parquet(path + "Cleaned_Stock_Prices_1400_06_29.parquet")
# print(len(df.name.unique()))
df = pd.read_parquet(path + "Cleaned_Stock_Prices_14010225.parquet")
print(len(df))
#%%
sub_df = df.groupby(['name']).filter(lambda x: x.shape[0] <60)
df = df.groupby(['name']).filter(lambda x: x.shape[0] >60)
#%%
len(df.name.unique())