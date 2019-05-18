#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import typing
import subprocess
import pathlib
import os

FAKE_TEST_SUCCESS = '''[==========] Running 140 tests from 7 test suites.
[----------] Global test environment set-up.
[----------] 20 tests from SaturatedMathTest/0 (unsigned 1), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAdd
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSub
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).NonSaturatingAdd
[       OK ] SaturatedMathTest/0 (unsigned 1).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).NonSaturatingSub
[       OK ] SaturatedMathTest/0 (unsigned 1).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMax
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMin
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMax
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMin
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/0 (unsigned 1) (0 ms total)
[----------] 20 tests from SaturatedMathTest/1 (unsigned 1), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAdd
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSub
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).NonSaturatingAdd
[       OK ] SaturatedMathTest/1 (unsigned 1).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).NonSaturatingSub
[       OK ] SaturatedMathTest/1 (unsigned 1).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMax
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMin
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMax
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMin
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/1 (unsigned 1) (0 ms total)
[----------] 20 tests from SaturatedMathTest/2 (signed 1), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAdd
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSub
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).NonSaturatingAdd
[       OK ] SaturatedMathTest/2 (signed 1).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).NonSaturatingSub
[       OK ] SaturatedMathTest/2 (signed 1).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMax
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMin
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMax
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMin
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/2 (signed 1) (0 ms total)
[----------] 20 tests from SaturatedMathTest/3 (unsigned 4), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAdd
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSub
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).NonSaturatingAdd
[       OK ] SaturatedMathTest/3 (unsigned 4).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).NonSaturatingSub
[       OK ] SaturatedMathTest/3 (unsigned 4).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMax
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMin
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMax
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMin
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/3 (unsigned 4) (0 ms total)
[----------] 20 tests from SaturatedMathTest/4 (signed 4), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAdd
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSub
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).NonSaturatingAdd
[       OK ] SaturatedMathTest/4 (signed 4).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).NonSaturatingSub
[       OK ] SaturatedMathTest/4 (signed 4).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMax
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMin
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMax
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMin
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/4 (signed 4) (0 ms total)
[----------] 20 tests from SaturatedMathTest/5 (unsigned 8), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAdd
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSub
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).NonSaturatingAdd
[       OK ] SaturatedMathTest/5 (unsigned 8).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).NonSaturatingSub
[       OK ] SaturatedMathTest/5 (unsigned 8).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMax
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMin
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMax
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMin
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/5 (unsigned 8) (0 ms total)
[----------] 20 tests from SaturatedMathTest/6 (signed 8), where TypeParam = <type>
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAdd
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSub
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).NonSaturatingAdd
[       OK ] SaturatedMathTest/6 (signed 8).NonSaturatingAdd (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).NonSaturatingSub
[       OK ] SaturatedMathTest/6 (signed 8).NonSaturatingSub (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMax
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMax
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMax (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMin
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMin (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMin
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMinPlusOne
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMinPlusOneMin
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxToZero
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxToZero (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddZeroToMax
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddZeroToMax (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMax
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMax (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMax
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMax (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMin
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMin (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMin
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMin (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMinPlusOne
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMinPlusOne (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMinPlusOneMin
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMinPlusOneMin (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxFromZero
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxFromZero (0 ms)
[ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubZeroFromMax
[       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubZeroFromMax (0 ms)
[----------] 20 tests from SaturatedMathTest/6 (signed 8) (0 ms total)
[----------] Global test environment tear-down
[==========] 140 tests from 7 test suites ran. (0 ms total)
[  PASSED  ] 140 tests.
'''.splitlines()


FAKE_TEST_FAILURE = '''[----------] 20 tests from SaturatedMathTest/6 (signed 8) (0 ms total)
[----------] Global test environment tear-down
[==========] 140 tests from 7 test suites ran. (0 ms total)
[  FAILED  ] 140 tests.
'''.splitlines()


class MockSerial:

    def __init__(self, fake_data: typing.List[str]):
        self._fake_data = fake_data
        self._fake_data_index = 0

    def readline(self) -> typing.Optional[bytes]:
        line = None
        try:
            line = self._fake_data[self._fake_data_index]
            self._fake_data_index += 1
        except IndexError:
            pass
        if line is not None:
            return bytearray(line, 'utf-8')
        else:
            return bytearray()


def run_nait(args: typing.List[str],
             check_result: bool = True,
             env: typing.Optional[typing.Dict[str, str]] = None) -> subprocess.CompletedProcess:
    """
    Helper to invoke nait for unit testing within the proper python coverage wrapper.
    """
    root_dir = pathlib.Path(__file__).parent.parent.parent
    setup = root_dir / pathlib.Path('setup').with_suffix('.cfg')
    coverage_args = ['coverage', 'run', '--parallel-mode', '--rcfile={}'.format(str(setup))]
    nait = root_dir / pathlib.Path('src') / pathlib.Path('nait')
    this_env = os.environ.copy()
    if env is not None:
        this_env.update(env)
    return subprocess.run(coverage_args + [str(nait)] + args,
                          check=check_result,
                          stdout=subprocess.PIPE,
                          env=this_env)


def get_mock_JLinkExe() -> pathlib.Path:
    return pathlib.Path(__file__).parent / pathlib.Path('mock_JLinkExe').with_suffix('.py')


def get_s32K144_jlink_script() -> pathlib.Path:
    return pathlib.Path(__file__).parent / pathlib.Path('test_math_saturation_loadfile_swd').with_suffix('.jlink')
