
TARGET := main

COMPILER := GCC

%.cpp : %.py
	python parser.py $<

%{TARGET} : ${TARGET}.cpp
	${COMILER} -o $@ $^