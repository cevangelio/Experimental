## Sky FX Terminal
from termcolor import colored, cprint

cprint("\n Welcome to Sky FX Terminal!\n", 'red')
print("   g                 get sentiment")
print("   s                 get SR levels")
print("   c                 get current price")
print("   p                 plot")
print("   h                 show this research menu again")
print("   b                 quit this menu, and shows back to main menu")
print("   quit              quit to abandon program")
print("")
print("  How can I help you today? \n")
option = input("> ")

if option == 's':
    import get_sr as gsr
    symbol = input("Symbol: ")
    tf = input("Timeframe: ")
    current_price = gsr.get_current_price(symbol)
    levels = gsr.get_sr(symbol, 240)
    upper_level = gsr.upper_level(current_price, levels)
    lower_level = gsr.lower_level(current_price, levels)
    cprint(f"Levels of {symbol} \nCurrent Price: {current_price}\nUpper Level: {upper_level}\nLower Level: {lower_level}\n")
    print("   a                 get SR for another symbol")
    print("   b                 quit this menu, and shows back to main menu")
    next = input("Next :")
elif option == 'p':
    import plot_sr
    symbol = input("Symbol: ")
    plot_sr.plot_sr(symbol)
    print("   a                 plot for another symbol")
    print("   b                 quit this menu, and shows back to main menu")
    next = input("Next :")


