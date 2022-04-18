import os
import numpy as np
from tkinter import *
from tkinter.constants import *
from time import sleep

currentPath = os.getcwd()
print(currentPath)
os.chdir(currentPath+"/exam")
with open ("input.txt", 'r') as txt_file:
    mod = txt_file.readline()
    capacity = txt_file.readline()
    size = txt_file.readline()
    refline = txt_file.readline().split(' ')
refpage = list(map(int, refline))
mod = int(mod)
capacity = int(capacity)
size = int(size)
tk = Tk()
tk.title("가상기억장치 페이지 교체방법")
tk.option_add("*Font","맑은고딕 25")


def DrawList(memory, page, fault, mt, perc): 
    canvas.delete("all")
    c_height = 100
    c_width = 400
    x_width = c_width / 2
    offset = 25
    spacing = 50
    canvas.create_rectangle(10, 100, 60, 150, fill="white", outline="green", width=5)
    canvas.create_text(30, 140, anchor=SW, text=str(page),font = "calibri 20")
    canvas.create_text(270, 140, anchor=SW, text=mt,font = "calibri 20")
    canvas.create_text(5, 230, anchor=SW, text="page fault:\n"+str(fault),font = "calibri 20")
    canvas.create_text(270, 230, anchor=SW, text="fault rate:\n"+str(perc)+"%",font = "calibri 20")

    for i in range(len(memory)):
        x0 = x_width-offset
        y0 = c_height+(i*spacing)
        x1 = x_width+offset
        y1 = c_height+spacing+(i*spacing)
        canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="red", width=5)
        canvas.create_text(x0+15, y0+40, anchor=SW, text=str(memory[i]),font = "calibri 20")
        
    tk.update_idletasks()

def LFUcache(capacity, rList):
    mt = "LFU"
    #memory: 메모리상태, pcount:들어간 순서 체크 fcount:페이지부재 발생 횟수, pagef: 페이지부재 발생 여부
    memory,fcount,pagef = [],0,'No' 
    table = []
    
    print("\nString|Frame →\t",end='')
    for i in range(capacity):                        
        print(i,end=' ')
    print("Fault\n   ↓\n")

    for page in rList:                                      # 참조리스트에서 페이지를 읽음
        if page not in memory:                              # 참조한 페이지가 frame(메모리)에 없을때 (페이지 부재)
            if len(memory) < capacity:                      # 메모리에 적재 가능(용량이 남아있음)
                memory.append(page)                         # memory에 페이지 추가
                table.append([0, 0])                        #table에 초기값 추가(table은 페이지의 정보를 나타냄)
                                                            #table[page][0]은 재참조된 횟수, table[page][1]은 카운터

                if len(memory) > 0:                         #메모리에 저장된 페이지가 하나라도 있을 때
                    for k in range(len(memory)):
                        table[k][1] += 1                    #각 페이지마다 카운트 횟수 추가

            else:                                           # 메모리가 꽉 찬 상태 -> 페이지 교체
                np1 = np.array(table).reshape(capacity,2)   #table을 2차원 벡터로 변형(열 값 가져오기)
                minval = min(np1[:, 0])                     #table의 첫번째 열 값 중 최솟값(재참조 된 횟수 중 최솟값)을 저장
                tmp = []                                    #재참조된 횟수가 최솟값인 페이지가 여러 개일 때 넣을 리스트
                for j in range(capacity):                   #용량만큼
                    if table[j][0] == minval:               #재참조된 횟수가 최소인 값을 찾아서
                        tmp.append(table[j][1])             #tmp 리스트에 해당되는 페이지의 카운트 값을 차례로 집어넣기

                for p in range(capacity):       
                    if table[p][1] == max(tmp):             #tmp 리스트 중 카운트 값이 가장 큰 값(LRU 기법을 따름)
                        break                               #그 페이지의 인덱스를 p로 저장(교체해야 할 페이지)

                memory[p] = page                            #교체할 페이지를 참조한 페이지로 교체 
                for r in range(capacity):       
                    table[r][1] += 1                        #나머지 페이지의 카운트 증가
                table[p][0] = 0                             #교체된 페이지의 재참조 횟수 초기화
                table[p][1] = 1                             #교체된 페이지의 카운트 초기화

            pagef = 'Yes'                                   # 페이지 부재 발생
            fcount += 1                                     # 페이지 부재 카운트 +1

        else:                                               # 페이지가 주기억장치에 존재 할때
            table[memory.index(page)][0] += 1               
            for u in range(len(memory)):                    #메모리에 있는
                table[u][1] += 1                            # 각 페이지 카운트 증가
            pagef = 'No'                                    #페이지 부재 발생하지 않음        
        
        print("   %i\t\t"%page, end='')
        for x in memory:
            print(x, end=' ')
        for x in range(capacity-len(memory)): 
            print(' ',end=' ')
        print(" %s"%pagef)

        DrawList(memory, page, pagef, mt, round((fcount/len(rList))*100, 2))
        sleep(1)

    print("\nTotal number of reference: %d\nTotal Page Faults: %d\nFault Rate: %0.2f%%"%(len(rList), fcount, (fcount/len(rList))*100))

def LRUcache(capacity, rList):
    mt = "LRU"
    #memory: 메모리상태, stack:스택 fcount:페이지부재 발생 횟수, pagef: 페이지부재 발생 여부
    memory,stack,fcount,pagef = [],[],0,'No' 
    print("\nString|Frame →\t",end='')
    for i in range(capacity):                       
        print(i,end=' ')
    print("Fault\n   ↓\n")

    for page in rList:                                              # 참조리스트에서 페이지를 읽음 
        if page not in memory:                                      # 참조한 페이지가 frame(메모리)에 없을때 (페이지 부재)
            if len(memory) < capacity:                              # 메모리에 적재 가능(용량이 남아있음)
                memory.append(page)                                 # memory에 페이지 추가
                stack.append(len(memory)-1)                         # stack에 해당 페이지의 순서(index) 삽입(즉, 스택은 메모리 index의 list)

            else:                                                   # 메모리가 꽉 찬 상태 -> 페이지 교체
                ind = stack.pop(0)                     # stack 0번째 요소를 ind(i번째)에 할당 -> 즉 비워야 할 스택의 번호가 ind(스택의 bottom)
                memory[ind] = page                                  # memory[ind]에 해당 페이지 추가
                stack.append(ind)                                   #stack의 맨 끝에 ind번의 인덱스 삽입(top에 삽입)

            pagef = 'Yes'                                           # 페이지 부재 발생
            fcount += 1                                             # 페이지 부재 카운트 +1

        else:                                                       # 페이지가 주기억장치에 존재 할때
            remove = stack.pop(stack.index(memory.index(page)))     #memory 안에 해당 페이지가 위치한 index 값을 j라 하면
                                                                    #stack 안에 j가 위치한 index 값을 제거하고 'remove'에 저장
            stack.append(remove)                                    #삭제했던 페이지(remove)를 스택 맨 아래(끝)에 다시 삽입
            pagef = 'No'                                            #페이지 부재 발생하지 않음            

        print("   %d\t\t"%page, end='')
        for x in memory:
            print(x, end=' ')
        for x in range(capacity-len(memory)): 
            print(' ',end=' ')
        print(" %s"%pagef)

        DrawList(memory, page, pagef, mt, round((fcount/len(rList))*100, 2))
        sleep(1)

    print("\nTotal number of reference: %d\nTotal Page Faults: %d\nFault Rate: %0.2f%%"%(len(rList), fcount, (fcount/len(rList))*100))

def start():
    if mod == 1:
        LRUcache(capacity, refpage)
    if mod == 2:
        LFUcache(capacity, refpage)
    
UI_frame = Frame(tk, width= 400, height=100, bg='grey')
UI_frame.grid(row=0, column=0, padx=10, pady=5)
canvas = Canvas(width=400, height=capacity*100, bg="white")
canvas.grid(row=1, column=0, padx=10, pady=5)
Button(UI_frame, text="Start", command=start, bg='red').grid(row=0, column=2, padx=5, pady=5)

tk.mainloop()