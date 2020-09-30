import sys
from build import generate_cpp

src = sys.argv[1]
dts = sys.argv[2]

generate_cpp(src, dst)