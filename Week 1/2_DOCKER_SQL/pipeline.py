import sys

import pandas as pd

print(sys.argv)

# below is command line argument
day = sys.argv[1] # arg 0 is the name of the file
# Some fancy stuff with pandas
print(f"job finished successfully for {day}")