# from multiprocessing.spawn import old_main_modules
import pandas as pd

# def clean_wo_customer_data(old_df, new_df):
#     #check old df is correct, use left join instead
#     new_df = new_df.reset_index(drop=True)
#     old_df = old_df.reset_index(drop=True)
#     new_df.drop(['HP', 'Address', 'Name'], axis=1, inplace=True)
#     new_df = new_df.merge(old_df[['Order No.', 'HP', 'Address', 'Name']], how="left", on="Order No.")
#     new_df = new_df.reset_index(drop=True)
    
#     return new_df
    

old_df = pd.DataFrame({"Order No." : [1,2,3], "Status": [1,2,3], "Name" :[1,2,3], "HP" : [1,2,3], "Address": [1,2,3]})
new_df = pd.DataFrame({"Order No." : [1,2,3], "Status": [1,2,3], "Name" :[1,2,3], "HP" : [1,2,3], "Address": [1,2,3]})

# # new = old_df.merge(new_df, how="left", on="Col1")

print(old_df.iloc[0 : 2, :])
print(old_df.iloc[2: , :])

# # test_dict = {"hello" : [1,2,3]}

# # print(str(test_dict))



# import pandas as pd

# original = pd.read_excel("Combined Data.xlsx")
# test = pd.read_excel("test_combined_data.xlsx")

# for index in range(len(original)):
#     if original["Order No."][index] != test["Order No."][index]:
#         print("Original: " + str(original["Order No."][index]))
#         print("test_combined_data: " + str(test["Order No."][index]))
#         break