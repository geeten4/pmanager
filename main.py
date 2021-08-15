from interface.UI import UI
import sys

# instance of UI manages whole applications
ui = UI()

# pass arguments to UI instance, without "main.py"
sys.argv.remove('main.py')
ui.process(sys.argv)
