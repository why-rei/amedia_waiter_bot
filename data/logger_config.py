import sys
from loguru import logger

l_level = "<b><k><M>{level: ^10}</></></>"
l_datetime = "<g>{time:YYYY-MM-DD > HH:mm:ss}</>"
l_message = "<light-yellow>{message: <60}</>"
l_function = "<bg 42><k>{function: ^20}</></>"

formatter = l_level + "\t|\t" + l_datetime + "\t|\t" + l_message + l_function

logger.remove(0)
logger.add(sys.stderr, level="INFO", format=formatter)
logger.add("../logs/main.log", level="INFO", format=formatter, rotation="1 week", compression="zip")
