
from icecream import ic
import os
import sys

data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


ic(data_dir)
from l8_helperz import get_user_data, Assistant



if __name__ == "__main__":
    ic("name = main in l8.py")
    #ic(sys.path)
    user = get_user_data()
    ic(user)