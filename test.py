"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

This file is the entry point for running unittest tests.
Here are some examples of how you can use it:

python3 ./test.py # run all tests that are imported in test.py
python3 ./test.py -v # verbose output
python3 ./test.py TestStudent # run all tests in the TestStudent class
python3 ./test.py TestStudent.test_sanity_student # run one test
python3 ./test.py -k test_verif
    # run all tests with names containg substring "test_verif"

"""

# These tests check the syntax presented in Part 1
from test.parser_test import *
from test.ast_test import *
# Below are tests you should uncomment as you make progress.

# uncomment the next line
from test.eval_test import *

# 3 and 4 can be done independently, for most of it.

from test.verif_test import *

from test.enumerate_test import *

from test.synth_test import *
# You should also check on some input files that the correct
# program is synthesized.

from test.student_test import *

import unittest

if __name__ == '__main__':
    unittest.main()
