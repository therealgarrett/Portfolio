

# PyTweets Readme
>A Twitter analysis tool.

![](https://img.shields.io/github/issues/detail/last-update/badges/shields/979.svg)
[![Build Status][travis-image]][travis-url]
[![Downloads Stats][npm-downloads]][npm-url]
![image](https://user-images.githubusercontent.com/34954082/50373569-eb739f80-0595-11e9-8e90-5fb94d1892af.png)
## Getting Started

PyTweets is a terminal application that streams tweets for data analysis using Twitter's API. All tweets from this program are processed and stored for later use in a MySQL database. Please read through **Required Packages** for compatability documentation as this will save you time for future deployment to your local machine.

## Prerequisites

To run PyTweets you need Python 3.6+

See [RealPython](https://realpython.com/installing-python/) for installing and running Python3 on your system. 
Installing [Homebrew](https://brew.sh) and [PyPI](https://pypi.org/project/pypi-install/) on your system will prepare you for any missing dependencies.
```
$ pip install your_package_name
$ brew install your_package_name
```

## Required Packages 

Add **requirements.txt** to your project path and then do the following:
```
$ pip install -r requirements.txt
```
You will have then installed required dependicies
### Other Requirements 
``` 
$ pip install ssl 
```

Install - [MySQL](https://dev.mysql.com/downloads/mysql/)

Install - [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)


## Running the tests
Save PyTweets into your local environment and run from terminal.
```
$ cd your_dir/script.py
$ python3 script.py
```

## Release History
* 0.0.1
  * First Release 


## Authors
**Garrett Lubin** - garrett.lubin@gmail.com

Twitter: [@therealgarrett](https://twitter.com/tharealgarrett) 


## Contributing

1. Fork it (https://github.com/therealgarrett)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
