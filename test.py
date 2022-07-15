import config_tools_data
from functions import convert_ISO

def get_since_date():
    dictPath = config_tools_data.readConfig()
    since_date = dictPath["SinceDate"]

    try:
        if len(since_date) != 0:
            converted_date = convert_ISO(since_date)
            return converted_date
        else:
            # print(since_date)
            return since_date
    except AttributeError:
        critical_msg = "Please enter since date in correct format!"
        print(critical_msg)

print(get_since_date())