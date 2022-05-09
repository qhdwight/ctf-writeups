# Oracle

## Approach

1) Load the `.class` file into Ghidra
2) Copy paste from the diassembler view into a C++ file
3) Modify a few things to make it compile and what not
4) Compile that C++ file as `oracle`
5) Open that binary in Ghidra and snag a few addresses to avoid
6) Run angr on it, with `find` set to 'Good job' being in standard output
