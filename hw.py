import numpy as np
import os
import time

################ Page Rank list ################
def getpage():
    '''
    This function will return the page rank matrix as a shape of (501,501) numpy.ndarray
    and the # of connections of each page as a dictionary.
    '''
    target_dictionary = "./web-search-files/"
    listdir = os.listdir(target_dictionary)
    listdir.remove(".DS_Store")
    listdir.sort(key = lambda s: float(s[4:])) # sort file name with number
    
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

    page_mat = np.array(page_mat) # This matrix should be transposed
    return page_mat.T, connect


def page_rank(d,DIFF,page_mat):
    """
    This function will return the latest update and the its rank based on the d and DIFF
    d should be a float from 0~1
    DIFF is recommended to be a float under 0.1
    """
    page_mat_mod = page_mat * d
    init = np.array([1/501]*501) # N = 501
    update = init.copy() # avoid changing init
    while True:
        temp = update.copy() # store the last update
        update = np.dot(page_mat_mod, update) + init*(1-d) # calculate update
        diff = sum(abs(temp - update))
        if diff < DIFF:
            break
    return update, update.argsort()[::-1]

def write_Q1_ans(rank,update,connect,d,DIFF):
    """
    This function will write our result 
    (the rank of the pages, connections of each pages and their importance value) 
    into the corresponding files
    """ 
    ans = []
    for i in range(len(rank)):
        result = f"page{rank[i]}\t{connect[rank[i]]}\t{round(update[rank[i]],8)}"
        ans.append(result)

    DIFF_dict = {0.100:"100", 0.010:"010", 0.001:"001"}
    file = "pr_" + str(int(d*100)) + "_" + DIFF_dict[DIFF] + ".txt"
    with open(file,"w") as f:
        f.write('\n'.join(ans))

def Q1():
    """
    This function will make files with some combinations of d and DIFF by executing 
    functions: write_Q1_ans, page_rank, getpage
    """
    page_mat, connect = getpage()
    d_list = [0.25, 0.45, 0.65, 0.85]
    DIFF_list = [0.100, 0.010, 0.001]
    for i in range(len(d_list)):
        for j in range(len(DIFF_list)):
            update, rank = page_rank(d_list[i], DIFF_list[j], page_mat)
            write_Q1_ans(rank, update, connect, d_list[i], DIFF_list[j])


################ Reverse index ################
def getword():
    """
    This function will return a word_list (list) and a word_dictionary (dict)
    word_list contains all the words contained in every pages (this web)
    word_dictionary contains page numbers as its keys and the words in that pages as its value,
    where those keys are str and values are list
    """
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
                word = data_list[split_index+1:][-2] # the last item is " "
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
    """
    This function makes a reverseindex.txt file,
    which contains every words in the web and the pages that contain those words
    """
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
    """
    This function simply execute functions: getword, find_page
    """
    word_list, word_dict = getword()
    find_page(word_list, word_dict)

################ Search engine ################

def search_engine(d,DIFF,page_mat,input_list,word_list,word_dict):
    """
    This function will find the top 10 hit page of the words contained in the input_list.
    
    If the item in input_list is a str which represents a single word input,
    then it will just print the reuslt(top 10 page).

    If the item in input_list is a list which represents multiple words input,
    then it will print two results, which are AND and OR. AND means the page should contain all the input words,
    while OR means the page can contain any of the input words.
    
    Lastly, the function will write the result to the corresponding file.
    """
    rank = page_rank(d,DIFF,page_mat)[1] # page rank with fixed d, DIFF
    
    for i in range(len(input_list)):
        if " " in input_list[i]:
            input_list[i] = input_list[i].split(" ")
    s = ""
    
    for i in range(len(input_list)):
		# single input (str)
        if not isinstance(input_list[i],list):

            # s += f"{input_list[i]}\t"

            if input_list[i] in word_list: # the word exists in web
                count = 0
                for j in range(len(rank)):
                    if rank[j] == 500:
                        continue
                    elif count >= 10: # only count for top 10 pages
                        break
                    elif input_list[i] in word_dict[rank[j]]:
                        count += 1
                        s += f"page{rank[j]} "
            else: # the word doesn't exist in web
                s += "none"

		# multiple inputs (list)
        else:
            item = ""
            for a in range(len(input_list[i])):
                item += f"{input_list[i][a]} "
			# AND part

            # s += f"AND ({item.strip()})\t"
            s += f"AND "

            count = 0
            if all(word in word_list for word in input_list[i]): # all words exist in web -> True
                for j in range(len(rank)):
                    if rank[j] == 500:
                        continue
                    elif count >= 10:
                        break
                    elif all(word in word_dict[rank[j]] for word in input_list[i]):
                        count += 1
                        s += f"page{rank[j]} "
                    elif j == len(rank)-1 and count == 0: # none of the word exists in the page (OR doesn't have this situation)
                        s += "none"
            else:
                s += "none"

            s += "\n"

			# OR part

            s += f"OR "

            count = 0
            if any(word in word_list for word in input_list[i]): # any word exists in web -> True
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

    DIFF_dict = {0.100:"100", 0.010:"010", 0.001:"001"}
    file = "result_"+str(int(d*100))+"_"+DIFF_dict[DIFF]+".txt"
    with open(file,"w") as f:
        f.write(s)
		

def Q3():
    """
    This function execute search_engine with some combinations of d and DIFF.
    """
    page_mat = getpage()[0]
    word_list, word_dict = getword() # word_list: all the words in web(sorted list), word_dict: all the words contained in each page(dict)
    with open("list.txt") as f:
        test = f.read().split("\n")
    d_list = [0.25, 0.45, 0.65, 0.85]
    DIFF_list = [0.100, 0.010, 0.001]
    for i in range(len(d_list)):
        for j in range(len(DIFF_list)):
            search_engine(d_list[i], DIFF_list[j], page_mat, test, word_list, word_dict)

# for printing on terminal, no need to write file #
def search_engine_2(d,DIFF,page_mat,input_words,word_list,word_dict): 
    """
    Different from search_engine, this function allows users to search words manually
    by input words and assign d and DIFF.
    """
    rank = page_rank(d,DIFF,page_mat)[1] # page rank with fixed d, DIFF

    if " " in input_words: # multiple inputs
        input_words = input_words.split(" ")
    
    s = ""
    
    if isinstance(input_words,str): # single input
        if input_words in word_list: # the word exists in web
            count = 0
            for i in range(len(rank)):
                if rank[i] == 500:
                    continue
                elif count >= 10:
                    break
                elif input_words in word_dict[rank[i]]:
                    count += 1
                    s += f"page{rank[i]} "
        else: # the word doesn't exist
            s += "none"

    elif isinstance(input_words,list): # multiple inputs

        # AND part
        s += f"AND "
        count = 0
        if all(word in word_list for word in input_words): # all words exist in web -> True
            for i in range(len(rank)):
                if rank[i] == 500:
                    continue
                elif count >= 10:
                    break
                elif all(word in word_dict[rank[i]] for word in input_words):
                    count += 1
                    s += f"page{rank[i]} "
                elif i == len(rank)-1 and count == 0: # none of the word exists in the page (OR doesn't have this situation)
                    s += "none"
        else:
            s += "none"

        s += "\n"

        # OR part

        s += "OR "

        count = 0
        if any(word in word_list for word in input_words): # any word exists in web -> True
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
    print(s)

def main1():
    """
    The main1 function executes function search_engine_2 by inputing d, DIFF manually 
    and print the result(top 10 pages); users can type *end* to end the function.
    """
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

def main2():
    """
    The main function executes function search_engine_2 with fixed d, DIFF 
    and print the result(top 10 pages); users can type *end* to end the function.
    """
    with open("list.txt") as f:
        test = f.read().split("\n")

    page_mat = getpage()[0] # get page matrix
    word_list, word_dict = getword()

    d = float(input("Assign a d (a float from 0~1)\n> "))
    DIFF = float(input("Assign a DIFF (a float under 0.1 is recommended)\n> "))
    s = input("Type word(s) you want to search\n> ")
    
    while s!= "*end*":
        old_time = time.time()
        search_engine_2(d, DIFF, page_mat, s, word_list, word_dict)
        new_time = time.time()
        print(f"--------It cost {round(new_time - old_time, 8)} sec to search--------")
        s = input("Type word(s) you want to search\n> ")

Q1()
Q2()
Q3()

choice = input("Type 1 if you want to fix d and DIFF when searching word(s)\nType 2 if you don't\n> ")
if choice == "1":
    main2()
elif choice == "2":
    main1()
else:
    print("Wrong input")
