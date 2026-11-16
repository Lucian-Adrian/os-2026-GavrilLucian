# Operating Systems Lab Hierarchy Mandate

## Lab Structure
Operating Systems coursework must be organized strictly by lab module:
- `lab1-2/`: Combined Laboratory 1 (Linux Resource Management) and Laboratory 2 (xv6 System Calls).
- `lab3/`: Laboratory 3 (The Command Line: Shell, Pipes and Text Filters).
- `lab4/`: Laboratory 4 (The xv6 Shell from the Outside).
- `lab5-6/`, `lab7-8/`: combined reports for Labs 5–6 and 7–8 (supplementary).
- Every lab, including `lab11/`, `lab12/` and `lab13/`, has its own directory named `labN/`.

## File Placement Rules
- Do not dump lab code (`sleep.c`, `args.c`, `oneliners.sh`, `report.sh`), lab notes, or lab reports into `os/` root.
- Course root `os/` must only contain high-level overview files (`README.md`, top-level course notes).
- Each lab directory must contain its own code, verification tests, handouts, and report documents.
