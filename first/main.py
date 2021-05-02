from dish import Dish
from user import User
from plate import Plate
from database import Database


# 其他一些与流程相关的函数可以定义在这里
# 也可以新开文件去定义
# 或者放到现有的类里

def pay(dish_prices: float, user_balance: float, db: Database):
    """
    判断用户余额是否能够支付所有菜品，并扣除相应余额，更新数据库user集合
    :param dish_prices:
    :param user_balance:
    :param db:
    :return:
    """
    pass


if __name__ == '__main__':
    dish = Dish()
    user = User()
    plate = Plate(dish.sumInfo(), user.sumInfo())
    plate_info = plate.sumInfo()
    db = Database("mongodb://localhost:27017/", "smartCanteen")
    pass
