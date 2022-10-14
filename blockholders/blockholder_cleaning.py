import pandas as pd
import re
import numpy as np
from persiantools.jdatetime import JalaliDate
#%%
path2 = r"D:\RA_Teias\Data\\"
path = r"D:\RA_Teias\Data\Stock_holder_new\\"

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


#%%


#%%
pdf = pd.read_parquet(path2 + "Cleaned_Stock_Prices_14001127.parquet")
print("read Price")
pdf = pdf.drop(
    columns=[
        "stock_id",
        # "title",
        "baseVol",
        "max_price",
        "min_price",
        "last_price",
        "open_price",
        "value",
        "quantity",
    ]
)
# pdf = pdf[pdf["date"] >= 20150324]
invalid_names = []
invalid_names = list(
    pdf[
        (
            (((pdf.title.str.startswith("ح")) & (pdf.name.str.endswith("ح"))))
            | (pdf.group_name == "اوراق حق تقدم استفاده از تسهیلات مسکن")
            | (pdf.group_name == "اوراق تامین مالی")
            # | (pdf.group_name == "صندوق سرمایه گذاری قابل معامله")
            | (pdf.instId.str.startswith("IRK"))
            | (pdf.title.str.startswith("سپرده"))
            | (pdf.title.str.startswith("ح"))
            | (pdf.title.str.contains("اختيارخ"))
            | (pdf.title.str.contains("اختيارف"))
            | (pdf.title.str.contains("اختيار"))
            | (pdf.title.str.contains("آتي"))
            | (pdf.title.str.contains("بازار اوراق بدهي"))
            | (pdf.title.str.startswith("سلف"))
            | (pdf.title.str.contains("بورس کالا"))
            | (pdf.title.str.contains("اوراق"))
        )
    ].name.unique()
)
invalid_names.append("سنگ آهن")
#%%
invalid_names

#%%
df1 = pd.read_pickle(path + "mergerdHolderAllData_cleaned.p").replace("-", np.nan)
print("read Mereged Data")

mlist = [
    "jalaliDate",
    "date",
    "Holder",
    "Holder_id",
    "Number",
    "Percent",
    "Change",
    "ChangeAmount",
    "Firm",
    "name",
    "shrout",
    "stock_id",
    "close_price",
]
df1["Number"] = df1.Number.astype(float)
df1["Percent"] = df1.Percent.astype(float)
df1["Change"] = df1.Change.astype(float)
df1 = df1[mlist]
print("Rename")

pdf["name"] = pdf["name"].apply(lambda x: convert_ar_characters(x))
df1["name"] = df1["name"].apply(lambda x: convert_ar_characters(x))
df1["name"] = df1["name"].apply(lambda x: x.strip())
df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
df1 = df1.drop(df1[df1["name"] == "کرد"].index)
#%%
a = list(df1.Holder_id.unique())
a.sort()
a
#%%
shrout_df = (
    df1[["date", "jalaliDate", "name", "shrout"]]
    .drop_duplicates()
    .reset_index(drop=True)
)
shrout_df["date"] = shrout_df.date.astype(int)
shrout_df = shrout_df.sort_values(by=["name", "date"])
shrout_df.to_csv(path2 + "SymbolShrout_1400_11_27.csv", index=False)
shrout_df
#%%
shrout_df[shrout_df.name == "های وب"]

#%%
len(df1[df1.date == 20190417])
#%%
df1 = df1[~df1.name.isin(invalid_names)]
df1["date"] = df1["date"].astype(str)
a = df1.groupby("date").size().to_frame()
a.plot(y=0, use_index=True)
a[a[0] < 100]
df1["date"] = df1["date"].astype(float)
df1["date"] = df1["date"].astype(int)
#%%
print(len(df1))
df1 = df1[~df1.Holder.isnull()]
print(len(df1))
#%%
gdata = pdf[["group_name", "name"]].drop_duplicates().dropna()
mapingdict = dict(zip(gdata.name, gdata.group_name))
df1["group_name"] = df1["name"].map(mapingdict)
gdata = pdf[["group_id", "group_name"]].dropna().drop_duplicates()
mapingdict = dict(zip(gdata.group_name, gdata.group_id))
df1["group_id"] = df1["group_name"].map(mapingdict)
df1 = df1.dropna()
df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
#%%
df2 = df1[["Holder_id", "Holder", "date"]]
df2 = df2.sort_values(by=["Holder_id"])
Holders = df2.drop_duplicates(
    subset="Holder_id", keep="last", inplace=False
).sort_values(by=["Holder_id"])
try:
    df1 = df1.drop(columns=["Unnamed: 0", "Unnamed: 0.1"])
except:
    try:
        df1 = df1.drop(columns=["Unnamed: 0"])
    except:
        print("No")

df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
# %%
df3 = pd.read_excel(path + "shareholder_names_cleaned_9901_v6.xlsx")
df3 = pd.read_excel(path + "shareholder_names_cleaned_140102_v1.xlsx")
for i in ["shareholder_cleaned", "shareholder_raw"]:
    print(i)
    df3[i] = df3[i].apply(lambda x: convert_ar_characters(x))
print("Holder")
df1["Holder"] = df1["Holder"].apply(lambda x: convert_ar_characters(x))


df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
#%%
df1.loc[df1["Holder_id"] == 53741, "Holder"] = "سرمایه گذاری تدبیر"
# indid = [
#     62690,
#     51770,
#     51817,
#     62446,
#     62465,
#     62608,
#     62640,
#     53836,
#     57041,
#     63264,
#     65212,
#     65212,
#     53508,
#     65197,
#     65197,
#     65030,
#     65030,
#     63264,
#     62671,
#     63117,
#     63308,
#     63110,
#     63316,
# ]
# df1.loc[df1["Holder_id"].isin(indid), "Holder"] = "اشخاص حقیقی"
# df1.loc[df1.Holder == "شخص حقيقي", "Holder"] = "اشخاص حقیقی"

mapingdict = dict(zip(df3["shareholder_raw"], df3["type"]))
df1["type"] = df1["Holder"].map(mapingdict)

mapingdict = dict(zip(df3["shareholder_raw"], df3["shareholder_cleaned"]))
df1["Holder"] = df1["Holder"].map(mapingdict)


df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
#%%


#%%

df1["type"] = df1["type"].fillna("None")
df1["type"] = df1["type"].replace(" fund", "fund")
# df1.loc[
#     df1["Holder_id"] == 56965, "Holder"
# ] = "PRXسبد-شرک43268--موس29115-م.صندوق ت.ف نوین"
# df1.loc[df1["Holder_id"] == 63323, "Holder"] = "تجارت و اسکان احیا سپاهان"
# df1.loc[df1["Holder_id"] == 63087, "Holder"] = "مدیریت ثروت پایا"
# df1.loc[df1["Holder_id"] == 21975, "Holder"] = "فولاد"
# df1.loc[df1["Holder_id"] == 47706, "Holder"] = "فیروزا"
# df1.loc[df1["Holder_id"] == 8018, "Holder"] = "ایران سهم"

# df1.loc[
#     df1["Holder_id"] == 60374, "Holder"
# ] = "BFMصندوق سرمایه گذاری.ا.ب.پاداش پشتیبان پارس"
# df1.loc[df1["Holder_id"] == 62744, "Holder"] = "پدیده تاپان سرآمد"


df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
df1["Holder"] = df1.groupby(["Holder_id"]).Holder.transform(
    lambda x: x.fillna(method="bfill").fillna(method="ffill")
)
#%%
# df1.loc[(
#     df1.Holder.isnull()
#     )&(
#         df1.Holder.str.contains("PRX")
#     ),'Holder'] = 
#%%
dropholders = [
    # "سایر سهامدارن",
    # "اعضا هیئت مدیره",
    # "اشخاص حقیقی",
    # "اشخاص حقوقی",
    # "سهام حقوقی",
    # "سهام حقیقی",
    "سهام کارکنان",
    "سهام کارگری",
    "سهام مسدود",
    # "سهام وثیقه",
    # "شرکت های گروه",
    # "شهرداری ها",
    # "کارکنان",
    # "کارگران",
    # "کارگزاران",
    # "مدیران شرکت",
    # "هیئت مدیره",
    "کد رزرو صندوقهای سرمایه گذاری قابل معامله",
    "کد رزرو صندوق های سرمایه گذاری قابل معامله",
    "کدواسط دستورالعمل اجرایی",
    # "سلب حق تقدم",
]
for i in dropholders:
    print(i)
    df1 = df1[df1.Holder != i]
# df1 = df1.drop(df1.loc[df1["Holder"].isin(dropholders)].index)

df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()

#%%
ids = df1[df1["Holder"].isnull()]["Holder_id"].tolist()
Holders[Holders["Holder_id"].isin(ids)]
# %%
Holders[Holders["Holder_id"].isin(ids)].to_excel(path + "NewHolder.xlsx")
# %%
holder_id = 70338.0
df1[df1.Holder_id == holder_id].name.unique()
df1[df1.Holder_id == holder_id].Holder.unique()
#%%

#
df1[df1.name == 'سمگا'].drop_duplicates(subset = ['name','Holder'])

#%%
df1 = df1.drop_duplicates(keep="first")

df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
#%%
df1 = df1.drop_duplicates(
    keep="first", subset=["name", "date", "Holder_id", "Number"]
).rename(columns={"shrout": "Total"})
#%%
tempt = df1[~df1.Holder.isin(["شخص حقیقی", "اشخاص حقیقی",])][
    ["Holder", "type", "Holder_id"]
].drop_duplicates(keep="last")
tempt["Holder_id"] = tempt.Holder_id.astype(int)
mapingdict = dict(zip(tempt.set_index(["Holder", "type"]).index, tempt["Holder_id"]))
df1["Holder_id2"] = df1.set_index(["Holder", "type"]).index.map(mapingdict)
df1.loc[df1.Holder_id2.isnull(), "Holder_id2"] = df1.loc[
    df1.Holder_id2.isnull()
].Holder_id
df1["Holder_id"] = df1.Holder_id2
df1 = df1.drop(columns=["Holder_id2"])


#%%
df1[df1.Holder == "اخابر"].drop_duplicates(subset=["Holder_id"])[
    ["Holder_id", "name", "date", "Holder", "type", "Number", "Total"]
]
#%%
df1 = (
    df1.groupby(
        [
            "stock_id",
            "Total",
            "name",
            "date",
            "close_price",
            "jalaliDate",
            "group_name",
            "group_id",
            "Holder_id",
            "Holder",
            "type",
        ]
    )
    .agg({"Number": sum, "Percent": sum})
    .reset_index()
)

df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()

#%%
df1 = df1[
    [
        "date",
        "name",
        "stock_id",
        "jalaliDate",
        "group_name",
        "group_id",
        "Holder",
        "Holder_id",
        "Number",
        "type",
        "Percent",
        "Total",
        "close_price",
    ]
]
df1.head()
df1[(df1.name == "آ س پ") & (df1.date == 20140511.0)]
#%%
a = df1.groupby("date").size().to_frame().reset_index()
a.plot(y=0, use_index=True)
a[a[0] < 100]


# %%
def sumPercent(df):
    gg = df.groupby(["date", "name"])
    return gg.Percent.sum()


a = sumPercent(df1)
a[a > 100]

#%%%
def Cleaning(g, ff, a, g_keys):
    i = g.name
    for id, value in enumerate(g_keys):
        if value == i:
            # print("Group " + str(id))
            1+2

    tempt = ff[ff["name"] == i[0]]
    notradedays = tempt.loc[tempt["volume"] == 0]["date"].tolist()

    gg = pd.merge(left=a, right=g, how="left", left_on="date", right_on="date")

    if len(gg) == 0:
        return

    ## Filling the Gaps
    if len(g) > 3:
        v1 = gg["stock_id"][~gg["stock_id"].isna()].index[-1]
        v2 = gg["stock_id"][~gg["stock_id"].isna()].index[0]
        gg = gg[(gg.index <= v1) & (gg.index >= v2)]
        gg = gg.reset_index(drop=True)
        gg["Condition"] = "Orginal"
        gg = FillGaps(gg)

    ### Flatting Data
    # gg = FlatFunction(gg)

    ##Flaging

    mapingdict = dict(zip(list(tempt["date"]), list(tempt["close_price"])))
    gg["close_price"] = gg["date"].map(mapingdict)
    gg = gg.fillna(method="ffill")

    d2 = gg["Number"].diff()
    d3 = gg["Percent"].diff()
    d2.iloc[0] = "-"
    d3.iloc[0] = "-"
    gg["Number_Change"] = d2
    gg["Percent_Change"] = d3

    gg["Trade"] = "Yes"
    gg.loc[(gg["date"].isin(notradedays)), "Trade"] = "No"

    return gg


def FlatFunction(gg):

    cg = gg[(gg.Percent_Change != 0) & (~gg.Percent_Change.isnull())]

    cindex = cg.index
    gindex = gg.index

    for index in cindex:
        i = 1
        flatted = 0
        while i < 6 and flatted == 0:
            ids = list(range(index, index + i))
            dg = gg[gg.index.isin(ids)]
            i += 1
            if abs(dg.Percent_Change.sum()) <= 0.00001:
                pg = gg.loc[gg.index == index - 1]
                if len(pg) < 1:
                    continue
                dgindex = dg.index
                for dinex in dgindex:
                    gg.loc[gg.index == dinex, "Number"] = pg["Number"].iloc[0]
                    gg.loc[gg.index == dinex, "Percent"] = pg["Percent"].iloc[0]
                    gg.loc[gg.index == dinex, "Percent_Change"] = 0
                    gg.loc[gg.index == dinex, "Condition"] = "Flatted"

                flatted = 1
                a = set(cindex)
                b = set(ids)
                cindex = list(a.difference(b))
    return gg


def FillGaps(gg):
    ChangeList = [
        "name",
        "stock_id",
        "group_name",
        "group_id",
        "Holder",
        "Number",
        "type",
        "Percent",
        "Total",
        "close_price",
    ]
    nanid = list(gg[gg.name.isnull()].index)
    for value in nanid:
        NextValue = gg[(~gg.name.isnull()) & (gg.index > value)].index[0]
        if NextValue - value <= 4:
            for i in ChangeList:
                gg.loc[gg.index == value, i] = gg.loc[gg.index == NextValue][i].iloc[0]
        gg.loc[gg.index == value, "Condition"] = "Filled"
    gg = gg[~(gg.name.isnull())]
    return gg


df = df1.reset_index(drop=True)
import requests


def removeSlash(row):
    X = row.split("/")
    if len(X[1]) < 2:
        X[1] = "0" + X[1]
    if len(X[2]) < 2:
        X[2] = "0" + X[2]

    return int(X[0]  + X[1] + X[2])


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
    df["jalaliDate"] = df.jalaliDate.apply(removeSlash)
    return df


overal_index = Overall_index()
mapingdict = dict(zip(df.jalaliDate, df.date))
overal_index["date"] = overal_index.jalaliDate.map(mapingdict)
overal_index = overal_index.dropna()
overal_index
#%%
def removeSlash(row):
    X = row.split("-")
    if len(X[1]) < 2:
        X[1] = "0" + X[1]
    if len(X[2]) < 2:
        X[2] = "0" + X[2]

    return int(X[0] + X[1] + X[2])


# overal_index["jalaliDate"] = overal_index.jalaliDate.apply(removeSlash)
grouped_data = df1.groupby(["name", "Holder_id"])  # ,'type'])
g_keys = list(grouped_data.groups.keys())

ff = pdf
index = overal_index
a = index.drop(columns=["Value"]).rename(columns={"Date": "date"})
print(len(a))
closedays = [13960923, 13960924, 13970504, 13970505]
a = a.drop(a.loc[a["jalaliDate"].isin(closedays)].index)
print(len(a))
new_row = {"date": 20171106}
a = a.append(new_row, ignore_index=True).sort_values(by=["date"])
data = pd.DataFrame()
print(len((g_keys)))
#%%
from tqdm import tqdm
tqdm.pandas()
# from pandarallel import pandarallel
# pandarallel.initialize()
i = g_keys[3195]
g = grouped_data.get_group(i)
data = grouped_data.progress_apply(Cleaning, ff=ff, a=a, g_keys=g_keys)
df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()
# %%

data = (
    (
        data.reset_index(drop=True)
        .dropna()
        .rename(columns={"jalaliDate_x": "jalaliDate"})
        .drop(columns=["jalaliDate_y"])
    )
    .sort_values(by=["date"])
    .reset_index(drop=True)
)


df1[(df1.name == "کماسه") & (df1.date >= 20170325)].sort_values(by="date").head()

#%%
data.to_csv(path + "cleaned_data.csv")
#%%
import pandas as pd

path = r"E:\RA_Teias\Data\Stock_holder_new\\"
data = pd.read_csv(path + "cleaned_data.csv").drop(columns=["Unnamed: 0"])
#%%
a = data.groupby("date").size().to_frame().reset_index()
a.plot(y=0, use_index=True)
tempt = (
    a[a[0] < a[0].quantile(0.0085)].append(a[a[0] == a[0].max()]).sort_values(by="date")
)
#%%
for i in tempt.date:
    print(i)
    pdate = a[a.date < i].tail(1).date.iloc[0]
    new = data[data.date == pdate]
    new["date"] = i
    new["Condition"] = "Flatted"
    data = data.loc[data.date != i].append(new)
#%%
a = data.groupby("date").size().to_frame().reset_index()
a.plot(y=0, use_index=True)
#%%
tempt = pdf[["jalaliDate", "date"]].drop_duplicates()
mapingdict = dict(zip(tempt.date, tempt.jalaliDate))
data["jalaliDate"] = data.date.map(mapingdict)


#%%
def sumPercent(df):
    gg = df.groupby(["date", "name"])
    return gg.Percent.sum()


a = sumPercent(data)
GHunder = list(a[a > 100].index)
print(len(GHunder))
tmt = data.set_index(["date", "name"])
a = sumPercent(tmt)
GHunder = a[a > 100].to_frame().reset_index().sort_values(by=["name", "date"])
multiIndex = GHunder.set_index(["date", "name"]).index
ChangeList = [
    "name",
    "stock_id",
    "group_name",
    "group_id",
    "Holder",
    "Holder_id",
    "Number",
    "type",
    "Percent",
    "Total",
    "close_price",
]
tmt = tmt.sort_values(by=["name", "date", "Percent"]).reset_index()
len(tmt[tmt.name == "فولاد"])
#%%
def sumPercent(df):
    gg = df.groupby(["date", "name"])
    return gg.Percent.sum()


err = []
tmt = tmt.set_index(["date", "name"]).drop(multiIndex).reset_index()
print(len(multiIndex))
a = sumPercent(tmt)
a[a > 100]


#%%
New = pd.DataFrame()
for counter, i in enumerate(multiIndex):
    print(counter, i)
    try:
        name, date = i[1], i[0]
        ndata = tmt[(tmt["name"] == name)].date
        nday = ndata.where(ndata > date).dropna().iloc[0]
        ndata = pd.DataFrame()
        ndata = ndata.append(tmt[(tmt["name"] == name) & (tmt["date"] == nday)])
        ndata
        JalaliDate = tmt[tmt["date"] == date].jalaliDate.iloc[0]
        ndata["date"] = date
        ndata["jalaliDate"] = JalaliDate
        New = New.append(ndata)
    except:
        print("error")
        err.append(i)
        continue
tmt = tmt.append(New)
tmt[(tmt.name == "آ س پ") & (tmt.date == 20140511.0)]
#%%
fkey = zip(list(pdf.name), list(pdf.date))
mapingdict = dict(zip(fkey, pdf.close_price))
tmt["close_price"] = tmt.set_index(["name", "date"]).index.map(mapingdict)
#%%

df = tmt.sort_values(by=["name", "date", "Percent"])
df.head()


df = df.reset_index(drop=True)

df = df.sort_values(by=["name", "date", "Percent"])
df = df.rename(columns={"Number": "nshares", "Total": "shrout"})
df.loc[(df.jalaliDate == 13970502) & (df.name == "دانا"), "shrout"] = 1.500000e09

df["name"] = df["name"].replace("دتهران\u200c", "دتهران")
df["name"] = df["name"].replace("تفیرو\u200c", "تفیرو")
df["Holder"] = df["Holder"].replace("دتهران\u200c", "دتهران")
df["Holder"] = df["Holder"].replace("تفیرو\u200c", "تفیرو")
df[["date", "jalaliDate"]] = df[["date", "jalaliDate"]].astype(int)
df.isnull().sum()
df.loc[df.Number_Change == "0.0", "Percent_Change"] = "0"
df[(df.name == "آ س پ") & (df.date == 20140511.0)]

#%%
def sumPercent2(df):
    gg = df.groupby(["date", "name"])
    return gg.Percent.sum()


a = sumPercent2(df)
GHunder = (
    a[a > 100]
    .to_frame()
    .reset_index()
    .sort_values(by=["name", "date"], ascending=False)
)

GHunder
#%%
df[df.date == df.date.max()].jalaliDate.unique()
#%%

df.to_csv(path + "Cleaned_Stocks_Holders_1400_11_27.csv", index=False)

# %%
import pandas as pd

a = pd.read_csv(r"E:\RA_Teias\Data\\" + "Cleaned_Stocks_Holders_1400_10_06.csv")
# %%
a[a.name == "فولاد"]
#%%
a = df.groupby("date").size().to_frame().reset_index()
a.plot(y=0, use_index=True)
t = a[a[0] < 1000].date.to_list()
df = df[~df.date.isin(t)]
a = df.groupby("date").size().to_frame().reset_index()
a.plot(y=0, use_index=True)
#%%