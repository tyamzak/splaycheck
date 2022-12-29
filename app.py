from datetime import datetime as dt
from datetime import timedelta as d
import pandas as pd
import collections

# ログ何分の中からカウントするか
TARGET_MINUTES = 10
# 特定の範囲のログから何個以上同じパスワード・ユニークなユーザーIDが見つかったら記録するか
FREQ = 5
# 全てのログを記録するか、初めに見つかった時のみ記録するか
ALL_LOG_RECORDS = False
# DEBUG用
IS_DEBUG = False


# @profile
def splay_count(lines:collections.deque)->dict:
    #dictを返す
    dict_password = {}

    df = pd.DataFrame(lines)
    sps = df[2].value_counts()
    for k in sps.keys():
        

        access_list = []

        if sps[k] >= FREQ:
            if df[df[2]==k].nunique()[1] >= FREQ :

                dic = {}
                for i in df.index:

                    if k == df.iloc[i,2]:

                        dic['datetime'] = df.iloc[i,0]
                        dic['username'] = df.iloc[i,1]
                        dic['password'] = df.iloc[i,2]

                        access_list.append(dic.copy())


                dict_password[k] = access_list
            # else: break
        else:
            break


    return dict_password, lines

def pop_old(lines:collections.deque, new_accessed_date:dt, xmin:d)->list:

    oldest = new_accessed_date - xmin
    if not lines:
        return lines

    while True:
        if lines[0][0] < oldest:
            lines.popleft()

            if not lines:
                break
        else:
            break
    #listを返す
    return lines

def read_log(path):

    lines_xmin = collections.deque()
    # lines_xmin = []
    dicts_passwords = {}


    cnt = 0

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:

        while True:
            line = f.readline().replace('\n','')

            cnt += 1
            if IS_DEBUG:
                if cnt % 1000 == 0:
                    print(f'{cnt}番目まで実施')
                if cnt > 10000:
                    break
            if not line:
                break

            else:
                try:
                    s = line.split('/',10)

                    xmin = d(minutes=TARGET_MINUTES)
                        
                    accessed_date = dt.strptime(f"{s[0]}-{s[1]}-{s[2]} {s[3]}:{s[4]}:{s[5]}", "%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    if IS_DEBUG:
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
                                if ALL_LOG_RECORDS:
                                    lasttime = dicts_passwords[i][-1]['datetime']
                                    if i == "01":
                                        print('found')
                                    for pasitem in dict_password[i]:

                                        if lasttime < pasitem['datetime']:
                                            # print(f"Splay append : {i}")
                                            dicts_passwords[i].append(pasitem.copy())
                            else:
                                print(f"Splay found : {i}")
                                dicts_passwords[i] = dict_password[i].copy()

                    #新しいaccessed_dateのxmin前以前のlistをポップする
                    lines_xmin = pop_old(lines_xmin,accessed_date,xmin)
                try:
                    idpass = s[10].split(',')
                    id = idpass[0]
                    password = idpass[2]
                    if ALL_LOG_RECORDS:
                        lines_xmin.append([accessed_date,id,password])
                    else:
                        if not password in dicts_passwords.keys():
                            lines_xmin.append([accessed_date,id,password])
                except Exception as e:
                    if IS_DEBUG:
                        print(e)
                finally:
                    pass



    return dicts_passwords
    


filepath = "log.txt"

dictlist = read_log(filepath)
df = pd.DataFrame.from_dict(dictlist,orient = 'index')
df.to_csv('result.csv')
print('終了')







