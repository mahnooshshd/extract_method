# Extract Method

*Extract Method* is a python implementation of an automated code refactoring tool for refactoring Java Long Method and Feature Envy code smells. The proposed tool aims to deal with issues related to long method detection, refactoring, selection of the proper name for the new method, and identification of the destination class. The tool mainly uses graph analysis techniques to identify and refactor Java long method smells.

## Getting started
### Install requirements
First, install the tool requirements, which are available in the requirement.txt file. Use the following command:
```bash
pip install -r requirements.pip
```

### Run the Extract Method tool

Put the project's source code directory in the root directory of the Extract Method tool and run the tool with the following command:

```bash
python main.py projetc_directory_name project_jar_file_path
```

Replace `projetc_directory_name` with the name of your Java project.
Replace `project_jar_file_path` with the path to the jar file of your Java project.

The execution of the tool can take a few minutes or some hours, depending on the project size. After execution, the recommended refactorings for the project will be in the output directory. The output will be in the json format file. 


## Benchmarks
Currently, three Java projects are available in this repository as the benchmark on which our tool runs successfully:

* ArgoUML (v0.34)
* FreeMind (v0.9.0)
* JEdit

## Demo
Figure 1 demonstrates the `caseALogicalExpressionTail` method with 45 lines of code in class `org.argouml.profile.internal.ocl.EvaluateExpression` of the **ArgoUML** project. This method is detected as a long method by the proposed tool. The identified lines of code to be extracted as the new method have been highlighted in the figure. 
From line 14 to line 40 is considered to be extracted as a new method. It is observed that these lines of code are used to set the value of the field in the `EvaluateExpression` class named `val`, which is a separate responsibility compared to the rest of the method's body. 
Figure 2 shows the dependency graph of `caseALogicalExpressionTail` method used for analyzing the method during refactoring process.  


![ArgoUML method body](./docs/figs/argo_uml_method1.png)

_Figure 1. Extract Method opportunity identified by the proposed approach in `org.argouml.profile.internal.ocl.EvaluateExpression` class of the ArgoUML project._


![ArgoUML method dependency graph](./docs/figs/argo_uml_method1_dependency_graph.png)

_Figure 2. Dependecy graph of method in Figure 1._



## Publications 

[1] Shahidi, M., Ashtiani, M., & Zakeri-Nasrabadi, M. (2022). An automated extract method refactoring approach to correct the long method code smell. Journal of Systems and Software, 187, 111221. [https://doi.org/10.1016/J.JSS.2022.111221](https://doi.org/10.1016/J.JSS.2022.111221).


## Read more

[Documentation website](https://m-zakeri.github.io/extract_method)








