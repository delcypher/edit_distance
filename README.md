Introduction
============

This is a simple implementation in python of the Wagner-Fischer algorithm[1]
for the computing minimum edit distance of two strings.

In addition the tool will display all the possible sequence of operations
that will give the minimum edit distance.


[1] http://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm

Usage
=====

Example:

```
$ ed.py "sitting" "kitten"
```

This will report the minimum edit distance and all the solutions
as a sequence of operations to transform the string ``sitting``
into ``kitten``.
