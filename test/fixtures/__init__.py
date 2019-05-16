#
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# This software is distributed under the terms of the MIT License.
#

import typing


FAKE_TEST_0 = '''UpdateCTestConfiguration  from :/Volumes/workspace/github32/libuavcan_v1/build/DartConfiguration.tcl
UpdateCTestConfiguration  from :/Volumes/workspace/github32/libuavcan_v1/build/DartConfiguration.tcl
Test project /Volumes/workspace/github32/libuavcan_v1/build
Constructing a list of tests
Done constructing a list of tests
Updating test list for fixtures
Added 0 tests to meet fixture requirements
Checking test dependency graph...
Checking test dependency graph end
test 1
    Start 1: libuavcan

1: Test command: /Volumes/workspace/github32/libuavcan_v1/build/libuavcan
1: Test timeout computed to be: 10000000
1: Running main() from gmock_main.cc
1: [==========] Running 148 tests from 10 test suites.
1: [----------] Global test environment set-up.
1: [----------] 2 tests from BuildConfigTest
1: [ RUN      ] BuildConfigTest.Version
1: [       OK ] BuildConfigTest.Version (0 ms)
1: [ RUN      ] BuildConfigTest.dsdl_regulated
1: [       OK ] BuildConfigTest.dsdl_regulated (0 ms)
1: [----------] 2 tests from BuildConfigTest (0 ms total)
1:
1: [----------] 2 tests from CanBusTest
1: [ RUN      ] CanBusTest.TypeFd
1: [       OK ] CanBusTest.TypeFd (0 ms)
1: [ RUN      ] CanBusTest.Type2_0
1: [       OK ] CanBusTest.Type2_0 (0 ms)
1: [----------] 2 tests from CanBusTest (0 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/0 (unsigned 1), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAdd
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSub
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/0 (unsigned 1).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).NonSaturatingSub
1: [       OK ] SaturatedMathTest/0 (unsigned 1).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/0 (unsigned 1).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/0 (unsigned 1).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/0 (unsigned 1) (0 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/1 (unsigned 1), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAdd
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSub
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/1 (unsigned 1).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).NonSaturatingSub
1: [       OK ] SaturatedMathTest/1 (unsigned 1).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/1 (unsigned 1).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/1 (unsigned 1).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/1 (unsigned 1) (0 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/2 (signed 1), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAdd
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSub
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/2 (signed 1).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).NonSaturatingSub
1: [       OK ] SaturatedMathTest/2 (signed 1).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/2 (signed 1).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/2 (signed 1).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/2 (signed 1) (0 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/3 (unsigned 4), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAdd
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSub
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/3 (unsigned 4).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).NonSaturatingSub
1: [       OK ] SaturatedMathTest/3 (unsigned 4).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/3 (unsigned 4).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/3 (unsigned 4).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/3 (unsigned 4) (1 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/4 (signed 4), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAdd
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSub
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/4 (signed 4).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).NonSaturatingSub
1: [       OK ] SaturatedMathTest/4 (signed 4).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/4 (signed 4).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/4 (signed 4).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/4 (signed 4) (0 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/5 (unsigned 8), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAdd
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSub
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/5 (unsigned 8).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).NonSaturatingSub
1: [       OK ] SaturatedMathTest/5 (unsigned 8).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/5 (unsigned 8).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/5 (unsigned 8).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/5 (unsigned 8) (0 ms total)
1:
1: [----------] 20 tests from SaturatedMathTest/6 (signed 8), where TypeParam = <type>
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAdd
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSub
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).NonSaturatingAdd
1: [       OK ] SaturatedMathTest/6 (signed 8).NonSaturatingAdd (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).NonSaturatingSub
1: [       OK ] SaturatedMathTest/6 (signed 8).NonSaturatingSub (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMax
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMax
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMin
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMin
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMinPlusOne
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMinPlusOneMin
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxToZero
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddMaxToZero (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingAddZeroToMax
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingAddZeroToMax (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMax
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMax (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMax
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMax (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMin
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMinMin (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMin
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMin (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMinPlusOne
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxMinPlusOne (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMinPlusOneMin
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMinPlusOneMin (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxFromZero
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubMaxFromZero (0 ms)
1: [ RUN      ] SaturatedMathTest/6 (signed 8).SaturatingSubZeroFromMax
1: [       OK ] SaturatedMathTest/6 (signed 8).SaturatingSubZeroFromMax (0 ms)
1: [----------] 20 tests from SaturatedMathTest/6 (signed 8) (0 ms total)
1:
1: [----------] 4 tests from Time/DurationTest/0, where TypeParam = <type>
1: [ RUN      ] Time/DurationTest/0.DefaultValue
1: [       OK ] Time/DurationTest/0.DefaultValue (0 ms)
1: [ RUN      ] Time/DurationTest/0.Concept_fromMicrosecond
1: [       OK ] Time/DurationTest/0.Concept_fromMicrosecond (0 ms)
1: [ RUN      ] Time/DurationTest/0.SaturatedAdd
1: [       OK ] Time/DurationTest/0.SaturatedAdd (0 ms)
1: [ RUN      ] Time/DurationTest/0.SaturatedSubtract
1: [       OK ] Time/DurationTest/0.SaturatedSubtract (0 ms)
1: [----------] 4 tests from Time/DurationTest/0 (0 ms total)
1:
1: [----------] Global test environment tear-down
1: [==========] 148 tests from 10 test suites ran. (1 ms total)
1: [  PASSED  ] 148 tests.
1/1 Test #1: libuavcan ........................   Passed    0.04 sec

100% tests passed, 0 tests failed out of 1

Total Test time (real) =   0.05 sec
'''.splitlines()


class MockSerial:

    def __init__(self, fake_data: typing.List[str]):
        self._fake_data = fake_data
        self._fake_data_index = 0

    def readline(self) -> typing.Optional[str]:
        line = None
        try:
            line = self._fake_data[self._fake_data_index]
            self._fake_data_index += 1
        except IndexError:
            pass
        return line
