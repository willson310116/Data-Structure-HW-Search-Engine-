import numpy as np
import os
import time
################ Page Rank list ################
def getpage():
    '''
    The function will return the page rank matrix as a shape of (500,500) numpy.ndarray
    and the # of connections of each page as a dictionary.
    '''
    target_dictionary = "./web-search-files/"
    listdir = os.listdir(target_dictionary)
    listdir.remove(".DS_Store")
    # print(listdir)
    listdir.sort(key = lambda s: float(s[4:])) # sort file name with number
    # print(listdir)
    page_mat = []
    connect = dict()
    for file in listdir:
        path = target_dictionary + file
        if file != "page500":
            with open(path) as f:
                data = f.read() # str
                data_list = data.split("\n") # str -> list
                split_index = data_list.index("---------------------")
                pages = data_list[:split_index] # pages are before the line
                pages = [int(pages[i][4:]) for i in range(len(pages))] # page100 -> 100
                page_vector = [1/len(pages) if i in pages else 0 for i in range(501)] # vector ## N = 501 ##
                page_mat.append(page_vector)
                connect[int(file[4:])] = len(pages) # add # of page connection to dict 
        
        # page500 is empty, ie it doesn't point to other pages
        # but there are still other pages point to page500
        elif file == "page500":
            page_vector = [0]*501
            page_mat.append(page_vector)
            connect[int(file[4:])] = 0

    page_mat = np.array(page_mat) #This matrix should be transposed
    return page_mat.T, connect


def page_rank(d,DIFF,page_mat):
    """
    The function will return the latest update and the its rank
    """
    page_mat_mod = page_mat * d
    # init = np.array([1/500]*500)
    init = np.array([1/501]*501) # N = 501
    update = init.copy() # avoid changing init
    while True:
        temp = update.copy() # store the last update
        update = np.dot(page_mat_mod, update) + init*(1-d) # calculate update
        diff = sum(abs(temp - update))
        if diff < DIFF:
            break
    return update, update.argsort()[::-1]

# page_mat = getpage()[0]
# update = page_rank(0.25,0.100,page_mat)[0]

def write_Q1_ans(rank,update,connect,d,DIFF):
    """
    The function will write our result into the corresponding file
    """
    ans = []
    for i in range(len(rank)):
#     print(f"page{rank[i]}\t{connect[rank[i]]}\t{round(update[rank[i]],8)}")
        result = f"page{rank[i]}\t{connect[rank[i]]}\t{round(update[rank[i]],8)}"
        ans.append(result)
    DIFF_dict = {0.100:"100", 0.010:"010", 0.001:"001"}
    file = "pr_"+str(int(d*100))+"_"+DIFF_dict[DIFF]+".txt"
    with open(file,"w") as f:
        f.write('\n'.join(ans))

def Q1():
    page_mat, connect = getpage()
    d_list = [0.25, 0.45, 0.65, 0.85]
    DIFF_list = [0.100, 0.010, 0.001]
    for i in range(len(d_list)):
        for j in range(len(DIFF_list)):
            # Q1(d_list[i], DIFF_list[j])
            update, rank = page_rank(d_list[i], DIFF_list[j], page_mat)
            write_Q1_ans(rank, update, connect, d_list[i], DIFF_list[j])

# def Q1(d,DIFF):
#     update, rank = page_rank(d,DIFF)
#     write_Q1_ans(rank,update,d,DIFF) 

# page_mat, connect = getpage()
# d_list = [0.25, 0.45, 0.65, 0.85]
# DIFF_list = [0.100, 0.010, 0.001]
# for i in range(len(d_list)):
#     for j in range(len(DIFF_list)):
#         Q1(d_list[i], DIFF_list[j])



################ Reverse index ################
def getword():
    target_dictionary = "./web-search-files/"
    listdir = os.listdir(target_dictionary)
    listdir.remove(".DS_Store")
    listdir.sort(key = lambda s: int(s[4:])) # sort file name with number
    word_list = []

    for file in listdir:
        if file != "page500":
            path = target_dictionary + file
            with open(path) as f:
                data = f.read()
                data_list = data.split("\n")
                split_index = data_list.index("---------------------")
                word = data_list[split_index+1:][-2]
                word_list.append(word)

    word_dict = dict()

    for i in range(len(word_list)):
        word_dict[i] = word_list[i].split(" ")[:-1]

    temp = []

    for i in range(len(word_dict)):
        temp.extend(word_dict[i])
    new_word_list = sorted(list(set(temp)))

    return new_word_list, word_dict

def find_page(word_list, word_dict):
    ans = []
    for i in range(len(word_list)):
        s = f"{word_list[i]}\t"
        for j in range(len(word_dict)):
            if word_list[i] in word_dict[j]:
                s += f" page{j}"
        ans.append(s)
    with open("reverseindex.txt","w") as f:
        f.write('\n'.join(ans))

def Q2():
    word_list, word_dict = getword()
    find_page(word_list, word_dict)

################ Search engine ################

def search_engine(d,DIFF,page_mat,input_list,word_list,word_dict):
    rank = page_rank(d,DIFF,page_mat)[1] # 固定d, DIFF下的page rank
    
    for i in range(len(input_list)):
        if " " in input_list[i]:
            input_list[i] = input_list[i].split(" ")
    s = ""
    
    for i in range(len(input_list)):
		# 單一輸入(str)
        if not isinstance(input_list[i],list):

            # s += f"{input_list[i]}\t"

            if input_list[i] in word_list: # web有這個字
                count = 0
                for j in range(len(rank)):
                    if rank[j] == 500:
                        continue
                    elif count >= 10: #只算輸出前10個page
                        break
                    elif input_list[i] in word_dict[rank[j]]:
                        count += 1
                        s += f"page{rank[j]} "
            else: # web沒有這個字
                s += "none"

		# 多輸入(list)
        else:
            item = ""
            for a in range(len(input_list[i])):
                item += f"{input_list[i][a]} "
			# AND 部分

            # s += f"AND ({item.strip()})\t"
            s += f"AND "

            count = 0
            if all(word in word_list for word in input_list[i]): # 所有word出現在web裡面->True
                for j in range(len(rank)):
                    if rank[j] == 500:
                        continue
                    elif count >= 10:
                        break
                    elif all(word in word_dict[rank[j]] for word in input_list[i]):
                        count += 1
                        s += f"page{rank[j]} "
                    elif j == len(rank)-1 and count == 0: # 沒有一個page同時有這些word的情況 (OR不會有這種情況)
                        s += "none"
            else:
                s += "none"

            s += "\n"

			# OR 部分

            # s += f"OR ({item.strip()})\t"

            s += f"OR "

            count = 0
            if any(word in word_list for word in input_list[i]): # 任何一個word出現在web裡面->True
                for j in range(len(rank)):
                    if rank[j] == 500:
                        continue
                    elif count >= 10:
                        break
                    elif any(word in word_dict[rank[j]] for word in input_list[i]):
                        count += 1
                        s += f"page{rank[j]} "
            else:
                s += "none"
        s += "\n"
	# print(s)
    DIFF_dict = {0.100:"100", 0.010:"010", 0.001:"001"}
    file = "result_"+str(int(d*100))+"_"+DIFF_dict[DIFF]+".txt"
    with open(file,"w") as f:
        f.write(s)
		

def Q3():
    page_mat = getpage()[0]
    word_list, word_dict = getword() # word_list: web 裡面所有的字，sorted list, word_dict: 每個page包含的字，dict
    with open("list.txt") as f:
        test = f.read().split("\n")
    d_list = [0.25, 0.45, 0.65, 0.85]
    DIFF_list = [0.100, 0.010, 0.001]
    for i in range(len(d_list)):
        for j in range(len(DIFF_list)):
            # Q3(d_list[i], DIFF_list[j])
            search_engine(d_list[i], DIFF_list[j], page_mat, test, word_list, word_dict)

# for printing on terminal, no need to write file #
def search_engine_2(d,DIFF,page_mat,input_words,word_list,word_dict): 
    rank = page_rank(d,DIFF,page_mat)[1] # 固定d, DIFF下的page rank

    if " " in input_words: # 多輸入
        input_words = input_words.split(" ")
    
    
    s = ""
    
    if isinstance(input_words,str): # 單一輸入
        if input_words in word_list: # web有這個字
            count = 0
            for i in range(len(rank)):
                if rank[i] == 500:
                    continue
                elif count >= 10:
                    break
                elif input_words in word_dict[rank[i]]:
                    count += 1
                    s += f"page{rank[i]} "
        else: # web 沒這個字
            s += "none"

    elif isinstance(input_words,list): # 多輸入

        # AND part
        s += f"AND "
        count = 0
        if all(word in word_list for word in input_words): # 所有word出現在web裡面->True
            for i in range(len(rank)):
                if rank[i] == 500:
                    continue
                elif count >= 10:
                    break
                elif all(word in word_dict[rank[i]] for word in input_words):
                    count += 1
                    s += f"page{rank[i]} "
                elif i == len(rank)-1 and count == 0: # 沒有一個page同時有這些word的情況 (OR不會有這種情況)
                    s += "none"
        else:
            s += "none"

        s += "\n"

        # OR part

        s += "OR "

        count = 0
        if any(word in word_list for word in input_words): # 任何一個word出現在web裡面->True
            for i in range(len(rank)):
                if rank[i] == 500:
                    continue
                elif count >= 10:
                    break
                elif any(word in word_dict[rank[i]] for word in input_words):
                    count += 1
                    s += f"page{rank[i]} "
        else:
            s += "none"
    # s += "\n"
    print(s)

    



# Q1()
# Q2()
# Q3()

with open("list.txt") as f:
        test = f.read().split("\n")

page_mat = getpage()[0] # get page matrix
word_list, word_dict = getword()

s = input("Type word(s) you want to search\n> ")
while s!= "*end*":
    d = float(input("Assign a d (a float from 0~1)\n> "))
    DIFF = float(input("Assign a DIFF (a float under 0.1 is recommended)\n> "))
    old_time = time.time()
    search_engine_2(d, DIFF, page_mat, s, word_list, word_dict)
    new_time = time.time()
    print(f"--------It cost {new_time - old_time} sec to search--------")
    s = input("Type word(s) you want to search\n> ")


# 確定有page連到page500
# target_dictionary = "./web-search-files/"
# listdir = os.listdir(target_dictionary)
# listdir.sort(key = lambda s: int(s[4:])) # sort file name with number
# have500 = []
# for file in listdir:
#     path = target_dictionary + file
#     with open(path) as f:
#         data = f.read() # str
#         data_list = data.split("\n") # str -> list
#         split_index = data_list.index("---------------------")
#         pages = data_list[:split_index] # pages are before the line
#         pages = [int(pages[i][4:]) for i in range(len(pages))] # page100 -> 100
#     if 500 in pages:
#         have500.append(f"{file}")
# print(have500)



