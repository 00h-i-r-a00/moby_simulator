all: compile

compile: clean
	javac -d bin/ -cp .:jars/*: src/MobySimulator.java
	@echo "Done building!!"

clean:
	find ./src/ ./jars/ -name "*.class" -type f -delete
