import requests
from bs4 import BeautifulSoup
import os
import json
import pandas as pd

find_analogy = True
check_gram = False

# Получаем старые данные об аптеках

jsons_old = []
for file in os.listdir('rest')[0:3]:
    with open('rest/' + file, 'r', encoding='utf-8') as f:  # открыли файл
        text = json.load(f)  # загнали все из файла в переменную
        jsons_old.append(text)

ids = set()
med = {}
aptekas = []

for i in jsons_old:
    apt = {}
    for it in i[1:]:
        if it[-1] not in ids:
            ids.add(it[-1])
            med[it[-1]] = {'name': it[4], 'prod': it[5], 'expiration': it[6], 'code': it[3]}
        apt[it[-1]] = {'price': it[2][0] / 100, 'amount': float(it[7])}
    aptekas.append(apt)

# получаем справочник

with open('spr.txt', 'r', encoding='utf-8') as f:
    spr = f.readlines()

info = list(map(lambda x: x.split('|'), spr))

# переводим его в датафрейм
d_info = {}

for st in info[1:]:
    d_info[st[0]] = {'name': st[1], 'manufactor': st[2], 'id_mnn': st[3], 'mnn': st[4][:-2]}
df = pd.DataFrame(d_info)
df = df.transpose()
df.index = pd.Series(df.index).apply(int)


def to_int(x):
    try:
        return int(x)
    except:
        return x


df['id_mnn'] = df['id_mnn'].apply(to_int)

# finds all the aptekas where there is an item and returns a set of indexes

def find_apt(st):
    res = set()
    search = find_it(fix_search(st))
    for i in search:
        for num, apt in enumerate(aptekas):
            if i in apt:
                res.add(num)
    return res


# find in spec apt

def find_in_apt_num(st, apt):
    res = []
    a = aptekas[apt]
    search = find_it(fix_search(st))
    for i in search:
        if i in a:
            res.append(i)
    return sorted(res, key=lambda x: aptekas[apt][x]['amount'], reverse=True)


def find_in_apt_num_best(st, apt):
    res = []
    a = aptekas[apt]
    search = find_it(fix_search(st))
    for i in search:
        if i in a:
            res.append(i)
    a = sorted(res, key=lambda x: aptekas[apt][x]['amount'], reverse=True)
    resu = set()
    resu.add(a[0])
    resu.add(sorted(res, key=lambda x: aptekas[apt][x]['price'], reverse=True)[-1])
    resu.add(sorted(res, key=lambda x: aptekas[apt][x]['price'], reverse=True)[0])
    for i in a:
        resu.add(i)
        if len(resu) >= 5:
            break
    return sorted(list(resu), key=lambda x: aptekas[apt][x]['price'])


def give_names(nums):
    return [med[x]['name'] for x in nums]


def find_in_apt(st, apt):
    return give_names(find_in_apt_num(st, apt))

# fix search query

def fix_search(st):
    if not check_gram:
        return st
    else:
        url = "https://yandex.com/search/xml?l10n=en&user=solovjevvlad&key=03.122513439:cd83a7c3373e1a8c0a58faae7d89fd32"
        params = {
            'query': st
        }
        r = requests.get(url, params)
        q = BeautifulSoup(r.text, features='lxml')
        if len(q.response.find_all('reask')) > 0:
            return q.response.reask.find('text').text
        else:
            return st


# находит все id, которые соответствуют поисковому запросу

def find_it(st):
    if find_analogy:
        res = set(df[[st.lower() in x for x in df['name'].apply(lambda y: y.lower())]].index)
        res = res.union(find_analogy(list(res)))
        return list(res)
    else:
        return df[[st.lower() in x for x in df['name'].apply(lambda y: y.lower())]].index


def find_analogy(numbers):
    # для примера можно ввести декстроза и алгоритм выдаст глюкозу
    res = set()
    for num in numbers:
        if type(df.loc[num]['id_mnn']) == type(1):
            n = df.loc[num]['id_mnn']
            res = res.union(set(list(df[df['id_mnn'] == n].index)))
    return res