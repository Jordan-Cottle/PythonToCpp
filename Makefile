PROJECT := hello

PY_DIR := py
CPP_DIR := cpp
OBJ_DIR := obj


PY_PROJECT_DIR := ${PY_DIR}/${PROJECT}
CPP_PROJECT_DIR := ${CPP_DIR}/${PROJECT}
OBJ_PROJECT_DIR := ${OBJ_DIR}/${PROJECT}

TARGET := main
OBJECTS := main.o

vpath %.py ${PY_PROJECT_DIR}
vpath %.cpp ${CPP_PROJECT_DIR}
vpath %.o ${OBJ_PROJECT_DIR}

all: ${PROJECT} ${TARGET}
	./${TARGET}

%.cpp : %.py
	python translate.py $< ${CPP_PROJECT_DIR}/$@

%.o : %.cpp
	g++ -c -o ${OBJ_PROJECT_DIR}/$@ ${CPP_PROJECT_DIR}/$<

${TARGET}: ${OBJECTS}
	g++ -o $@ $(addprefix ${OBJ_PROJECT_DIR}/, $^)

${PROJECT}:
	mkdir -p ${CPP_PROJECT_DIR}
	mkdir -p ${OBJ_PROJECT_DIR}

clean:
	rm -r ${CPP_DIR}
	rm -r ${OBJ_DIR}
	rm ./main