from interface.UI import UI
import sys

ui = UI()
sys.argv.remove('main.py')
ui.process(sys.argv)
