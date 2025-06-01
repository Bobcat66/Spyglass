# MIT License
#
# Copyright (c) 2025 FRC 1076 PiHi Samurai
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import robotpy_apriltag as apriltag
# A singleton class for maintaining global field configuration

_tag_size: float
_family: str
_layout: apriltag.AprilTagFieldLayout

def setTagSize(size: float) -> None:
    global _tag_size
    _tag_size = size

def getTagSize() -> float:
    global _tag_size
    return _tag_size


def setFamily(family: str) -> None:
    global _family
    _family = family

def getFamily() -> str:
    global _family
    return _family


def loadLayout(layoutName: str) -> None:
    global _layout
    _layout = apriltag.AprilTagFieldLayout("resources/fields/" + layoutName + ".json")

def setLayout(layout: apriltag.AprilTagFieldLayout) -> None:
    #For testing only
    global _layout
    _layout = layout

def getLayout() -> apriltag.AprilTagFieldLayout:
    global _layout
    return _layout




