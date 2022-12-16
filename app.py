import pandas as pd
from datetime import datetime
from collections import deque

def read_log(path):

    logs = dict() # キー=パスワード, 値=アクセスリスト

    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        read_state = 0
        que = deque(maxlen=5)
        while True:
            line = f.readline()
            if not line:
                break

            que.append(line) # いったん流れた日時行を取得するため直近5行をキューに保持

            if read_state == 0:   # 開始行の探索中
                if line.startswith('サブリスト: 動体検知開始'):
                    line = que[-4] # 日時行
                    pos = line.find(' ')
                    dt = datetime.strptime(line[pos+1:].strip(), '%Y-%m-%d %H:%M:%S')
                    read_state = 1

            elif read_state == 1: # カメラ行の探索中
                if line.startswith('カメラ No.:'):
                    log = line.split(':')[1].strip()
                    if log not in logs:
                        logs[log] = []
                    logs[log].append(dt)
                    read_state = 0

    return logs

logs = read_log('log.txt')
print('read_log end.')

# 結果をカメラ毎にCSV出力
for log, dts in logs.items():
    df = pd.DataFrame({'Date':dts})
    df['cnt'] = 1
    df = df.set_index('Date')
    df = df.resample('H').sum()
    df.to_csv(f'{log}.csv')