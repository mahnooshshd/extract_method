# Extract Method

Extract Method is a python implementation of an automated code refactoring tool for refactoring long method code smell.
## Install requirements

```bash
pip install -r requirements.pip
```

## Usage

Extract method works with help of [Java Callgraph](https://github.com/gousiosg/java-callgraph) tool. To run Extract method for your java projetc, you need to generate a file named call.txt and put in the directory of the project source code. This file can be generated with following command. Replace jar_file_path with tha path of the project's jar file and project_path whith your project source code path.
```bash
java -jar javacg-0.1-SNAPSHOT-static.jar jar_file_path > project_path/call.txt
```
Then put the project source code directory in the root directory of Extract Method and run Exctract Method with following command. Replace projetc_directory_name with the name of the project directory. This can take some minutes to some hours depend on the size of the project.

```bash
python main.py projetc_directory_name
```
 The recommended refactorings for the project will be printed out. You can put the output in a file to save the recommendations.