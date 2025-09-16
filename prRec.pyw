import FreeSimpleGUI as sg
import datetime
sg.theme("LightBlue6")

#進捗読み込み
with open('progress.txt', 'r') as f:
    kw_list1 = f.read().split("\n")
    pro_list = []      #project list
    pro_name = []
    for i in kw_list1[:-1]:
        pro = i.split(",")
        pro[1] = int(pro[1])
        pro[2] = datetime.timedelta(seconds=int(pro[2]))
        pro_list.append(pro[:-1])
    for i in pro_list:
        pro_name.append(i[0])

#achive読み込み
with open('archive.txt', 'r') as f:
    arc_list1 = f.read().split("\n")
    arc_list = []      #project list
    for i in arc_list1[:-1]:
        arc = i.split(",")
        arc_list.append(arc[:-1])

#表作成
def pro_watch(data):
    theme = "進行中"
    header = ["-----WORK NAME-----", "PROGRESS", "TIME"]
    L = [[sg.Table(data, headings=header)]]
    return L

def arc_watch(data):
    theme = "完了済み"
    header = ["-----WORK NAME-----", "TIME"]
    L = [[sg.Table(data, headings=header)]]
    return L 

Plist = pro_watch(pro_list)
Alist = arc_watch(arc_list)

#選択
def make_start():
    start_layout = [[sg.T("選択してください")],
                    [sg.Push(), sg.B("既存プロジェクト", k="prg"), sg.Push()],
                    [sg.Push(), sg.B("新規プロジェクト", k="new"), sg.Push()]]
    SL = [[sg.TabGroup([[sg.Tab("選択", start_layout),
                         sg.Tab("進行中", Plist),
                         sg.Tab("完了済み", Alist)]])]]
    
    return sg.Window("業務管理",SL, finalize=True)

#既存プロジェクトを選択
def make_progress():
    
    pro_layout = [[sg.T("プロジェクトを選択してください")],
                  [sg.Listbox(pro_name, k="in1", size=(30,10))],
                  [sg.Push(), sg.B("決定", k="decide"), sg.Push()]]
    return sg.Window("既存プロジェクト選択",pro_layout, finalize=True)

#新規プロジェクト作成
def make_new():
    new_layout = [[sg.T("プロジェクト名"), sg.I(k="in1")],
                  [sg.T("進捗状況[%]"), sg.I("0", k="in2")],
                  [sg.Push(), sg.B("入力完了", k="registration"), sg.Push()]]
    return sg.Window("新規作成", new_layout, finalize=True)

#ストップウォッチメイン動作
#要改変
#Input = I, Button = B, Text = T, key = k, Multiline = ML, Image =Im
def main(work_name, pro_rate, work_time):
    layout = [[sg.T(f"課題 : {work_name}")],
              [sg.T(f"進捗 : {pro_rate}%")],
              [sg.T(f"作業時間 : {work_time}")],
              [sg.Push(), sg.B("START/STOP", k="btn"), sg.Push()],
              [sg.T("0:00:00", font=("Arial",40), k="txt",
                    size=(15,1), justification="center")],
              [sg.T("現在の進捗[%]"),sg.I("100", k="in3")],
              [sg.Push(), sg.B("業務終了", k="end"), sg.Push()],
              [sg.T(k="txt2", justification="center")],
              [sg.Push(), sg.B("記録する", k="record"), sg.Push()]]
    ML = [[sg.TabGroup([[sg.Tab("メイン", layout),
                         sg.Tab("進行中", Plist),
                         sg.Tab("完了済み", Alist)]])]]
    return sg.Window("業務管理", ML, finalize=True)
##win = sg.Window("業務管理アプリ", layout,font=(None,14),size=(320,400))

#ストップウォッチ関連１
def execute(wt,td):
    if startflag == True:
        now = datetime.datetime.now().replace(microsecond=0)
        td = now - start
        td2 = td + wt
        win["txt"].update(td2)
        return wt, td2
    else:
        return td, td

#結果表記
def execute_2(wt, pro_rate):
    in2 = pro_rate
    in3 = int(v["in3"])
    txt2 = f"作業時間{wt}進捗{in3-in2}%"
    win["txt2"].update(txt2)
    return True

#ストップウォッチ関連２
def startstop():
    global start, startflag
    if startflag == True:
        startflag = False
    else:
        start = datetime.datetime.now().replace(microsecond=0)
        startflag = True

clear=False
startflag = False
wt=datetime.timedelta(seconds=0)
td=datetime.timedelta(seconds=0)
#e=event, v=values

#進捗リストが無い場合は新規作成を促す．
if len(pro_list)==0:
    win = make_new()
else:
    win = make_start()

#全体の動作
while True:
    e, v = win.read(timeout=50)
    wt,td = execute(wt,td)
    if e=="prg":
        win.close()
        win = make_progress()
    if e=="new":
        win.close()
        win = make_new()
    if e=="decide":
        work_name = v["in1"][0]
        pro_rate = pro_list[pro_name.index(work_name)][1]
        work_time = pro_list[pro_name.index(work_name)][2]
        e="main"
    if e=="registration":
        work_name = v["in1"]
        pro_rate = int(v["in2"])
        work_time = datetime.timedelta(seconds=0)
        e="main"
    if e=="main":
        win.close()
        Plist = pro_watch(pro_list)
        Alist = arc_watch(arc_list)
        win = main(work_name, pro_rate, work_time)
    if e=="btn":
        startstop()
    if e=="end":
        startflag = False
        clear=execute_2(wt, pro_rate)
    if e=="record":
        startflag==False
        if clear==False:
            clear=execute_2(wt, pro_rate)
        if int(v["in3"])==100:
            arc_list.append([work_name, work_time+wt])
            for d in pro_list:
                d[2]=d[2].seconds+24*3600*d[2].days
            with open('archive.txt', 'w') as f:
                for d in arc_list:
                    for i in d:
                        f.write(str(i)+",")
                    f.write("\n")
            if work_time!=datetime.timedelta(seconds=0):
                del pro_list[pro_name.index(work_name)]
                with open('progress.txt', 'w') as f:
                    for d in pro_list:
                        for i in d:
                            f.write(str(i)+",")
                        f.write("\n") 
        else:
            wt_f = work_time+wt
            if work_time==datetime.timedelta(seconds=0):
                pro_list.append([work_name, int(v["in3"]), wt_f])
            else:
                pro_list[pro_name.index(work_name)]=[work_name, int(v["in3"]), wt_f]
            for d in pro_list:
                d[2]=d[2].seconds+24*3600*d[2].days
            with open('progress.txt', 'w') as f:
                for d in pro_list:
                    for i in d:
                        f.write(str(i)+",")
                    f.write("\n")
            
        e="renew"
    if e=="renew":
        #progress読み込み
        with open('progress.txt', 'r') as f:
            kw_list1 = f.read().split("\n")
            pro_list = []      #project list
            pro_name = []
            for i in kw_list1[:-1]:
                pro = i.split(",")
                pro[1] = int(pro[1])
                pro[2] = datetime.timedelta(seconds=int(pro[2]))
                pro_list.append(pro[:-1])
            for i in pro_list:
                pro_name.append(i[0])

        #achive読み込み
        with open('archive.txt', 'r') as f:
            arc_list1 = f.read().split("\n")
            arc_list = []      #project list
            for i in arc_list1[:-1]:
                arc = i.split(",")
                arc_list.append(arc[:-1])

        Plist = pro_watch(pro_list)
        Alist = arc_watch(arc_list)
                
        wt=datetime.timedelta(seconds=0)
        td=datetime.timedelta(seconds=0)
        win.close()
        if len(pro_list)==0:
            win = make_new()
        else:
            win = make_start()
    if e==None:
        break
    
win.close()
