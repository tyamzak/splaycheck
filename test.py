from datetime import datetime as dt
from datetime import timedelta as d
import pandas as pd

# ログ何分の中からカウントするか
TARGET_MINUTES = 6
# 特定の範囲のログから何個以上見つかったら記録するか
FREQ = 5


def splay_count(lines:list)->dict:
    #dictを返す
    dict_password = {}
    indexes_for_pop = []
    df = pd.DataFrame(lines)
    sps = df[2].replace('(.*)\n',r'\1',regex=True).value_counts()
    for k in sps.keys():
        
        if k == "":
            continue

        access_list = []

        if sps[k] >= FREQ:

            dic = {}
            for i in df.index:
                if k == df.iloc[i,2].replace('\n',''):

                    dic['datetime'] = df.iloc[i,0]
                    dic['username'] = df.iloc[i,1]
                    dic['password'] = df.iloc[i,2].replace('\n','')

                    access_list.append(dic)
                    indexes_for_pop.append(i)
            dict_password[k] = access_list
            
    indexes_for_pop.sort(reverse=True)
    for i in indexes_for_pop:
        lines.pop(i)

    return dict_password, lines

def pop_old(lines:list, new_accessed_date:dt, xmin:d)->list:

    oldest = new_accessed_date - xmin
    if not lines:
        return lines

    while True:
        if lines[0][0] < oldest:
            lines.pop(0)
            if not lines:
                break
        else:
            break
    #listを返す
    return lines

def read_log(path):

    lines_xmin = []
    dicts_passwords = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:

        while True:
            line = f.readline()
            if not line:
                break

            else:
                try:
                    s = line.split('/',10)

                    xmin = d(minutes=6)
                        
                    accessed_date = dt.strptime(f"{s[0]}-{s[1]}-{s[2]} {s[3]}:{s[4]}:{s[5]}", "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(e)

                # 初回限定の処理
                if not lines_xmin:
                    startdate = accessed_date
                    enddate = startdate + xmin

                # 規定秒数分のログが溜まったら
                if accessed_date > enddate:
                    #splayのカウントを行う
                    dict_password, lines_xmin = splay_count(lines_xmin)
                    if dict_password:
                        for i in dict_password:
                            if i in dicts_passwords:
                                dicts_passwords[i].append(dict_password[i])
                            else:
                                dicts_passwords[i] = dict_password[i]

                    #新しいaccessed_dateのxmin前以前のlistをポップする
                    lines_xmin = pop_old(lines_xmin,accessed_date,xmin)
                try:
                    idpass = s[10].split(',')
                    id = idpass[0]
                    password = idpass[2]

                    lines_xmin.append([accessed_date,id,password])
                except Exception as e:
                    print(e)
                finally:
                    pass



    return dicts_passwords
    

filepath = "log.txt"

dictlist = read_log(filepath)

print('終了')