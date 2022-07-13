import pandas as pd

combined_data = pd.read_excel("Combined Data.xlsx")
index_list = []
for i, value in combined_data["Name"].iteritems():
    if value == None or value == "":
        index_list.append(i)    

print(index_list)


# print("Hell0".__contains__("S", "e"))