# Overview

<table>
<tbody>
<tr class="odd">
<td>tests</td>
<td><div class="line-block"><a href="https://travis-ci.org/rtibbles/python-delta-crdts"><img src="https://api.travis-ci.org/rtibbles/python-delta-crdts.svg?branch=master" alt="Travis-CI Build Status" /></a> <a href="https://ci.appveyor.com/project/rtibbles/python-delta-crdts"><img src="https://ci.appveyor.com/api/projects/status/github/rtibbles/python-delta-crdts?branch=master&amp;svg=true" alt="AppVeyor Build Status" /></a> <a href="https://requires.io/github/rtibbles/python-delta-crdts/requirements/?branch=master"><img src="https://requires.io/github/rtibbles/python-delta-crdts/requirements.svg?branch=master" alt="Requirements Status" /></a><br />
<a href="https://codecov.io/github/rtibbles/python-delta-crdts"><img src="https://codecov.io/gh/rtibbles/python-delta-crdts/branch/master/graphs/badge.svg?branch=master" alt="Coverage Status" /></a></div></td>
</tr>
<tr class="even">
<td>package</td>
<td><div class="line-block"><a href="https://pypi.org/project/delta_crdts"><img src="https://img.shields.io/pypi/v/delta_crdts.svg" alt="PyPI Package latest release" /></a> <a href="https://pypi.org/project/delta_crdts"><img src="https://img.shields.io/pypi/wheel/delta_crdts.svg" alt="PyPI Wheel" /></a> <a href="https://pypi.org/project/delta_crdts"><img src="https://img.shields.io/pypi/pyversions/delta_crdts.svg" alt="Supported versions" /></a> <a href="https://pypi.org/project/delta_crdts"><img src="https://img.shields.io/pypi/implementation/delta_crdts.svg" alt="Supported implementations" /></a><br />
<a href="https://github.com/rtibbles/python-delta-crdts/compare/v0.0.0...master"><img src="https://img.shields.io/github/commits-since/rtibbles/python-delta-crdts/v0.0.0.svg" alt="Commits since latest release" /></a></div></td>
</tr>
</tbody>
</table>

A Python implementation of Delta CRDTs

  - Free software: MIT license

## Installation

    pip install delta_crdts

You can also install the in-development version with:

    pip install https://github.com/rtibbles/python-delta-crdts/archive/master.zip

## Documentation

To use the project:

``` python
import delta_crdts
delta_crdts.longest()
```

## Development

To run the all tests run:

    tox

Note, to combine the coverage data from all the tox environments run:

<table>
<colgroup>
<col style="width: 10%" />
<col style="width: 90%" />
</colgroup>
<tbody>
<tr class="odd">
<td>Windows</td>
<td><pre><code>set PYTEST_ADDOPTS=--cov-append
tox</code></pre></td>
</tr>
<tr class="even">
<td>Other</td>
<td><pre><code>PYTEST_ADDOPTS=--cov-append tox</code></pre></td>
</tr>
</tbody>
</table>
