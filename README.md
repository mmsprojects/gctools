# GC TOOLS [1.0]()

<img align="center" height=240 src="https://lh3.googleusercontent.com/pw/ADCreHfLLChjxpymS23Q94MRIZfU0nXwcMBpEsxjkZZFXktOS4y8WuXgKhbRZNO79gqyK4VOtQJHB3oLqWD2-IhWVxfxJ12Rqmk32rXyhci6CAaiLekJ9urARe9w7Cf0Q31Ji1sYP0c_tnzcMIuv0PpH_HSS=w500-h500-s-no?authuser=0"/>

GC Tools is a QGIS Plugin created to help user perform ai models like predict tasks and draw samples [Kivy](http://kivy.org), simple and efficient tool.

The project's goal is to approximate Google's [Material Design spec](https://material.io/design/introduction/) as close as possible without sacrificing ease of use or application performance.

This library is a fork of the [KivyMD project](https://gitlab.com/kivymd/KivyMD) the author of which stopped supporting this project four years ago. We found the strength and brought this project to a new level.

Currently we're in **beta** status, so things are changing all the time and we cannot promise any kind of API stability. However it is safe to vendor now and make use of what's currently available.

Join the project! Just fork the project, branch out and submit a pull request when your patch is ready. If any changes are necessary, we'll guide you through the steps that need to be done via PR comments or access to your for may be requested to outright submit them.

If you wish to become a project developer (permission to create branches on the project without forking for easier collaboration), have at least one PR approved and ask for it. If you contribute regularly to the project the role may be offered to you without asking too.

[![PyPI version](https://img.shields.io/pypi/v/kivymd.svg)](https://pypi.org/project/kivymd)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/kivymd.svg)](#Installation)
[![Downloads](https://pepy.tech/badge/kivymd)](https://pepy.tech/project/kivymd)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Discord](https://img.shields.io/discord/566880874789076992?logo=discord)](https://discord.gg/wu3qBST)
[![Twitter](https://img.shields.io/twitter/follow/KivyMD?label=follow&logo=twitter&style=flat&color=brightgreen)](https://twitter.com/KivyMD)
[![YouTube](https://img.shields.io/static/v1?label=subscribe&logo=youtube&logoColor=ff0000&color=brightgreen&message=2k)](https://www.youtube.com/c/KivyMD)
[![Habr](https://img.shields.io/static/v1?label=habr&message=ru&logo=habr&color=brightgreen)](https://habr.com/ru/users/kivymd/posts)
[![StackOverflow](https://img.shields.io/static/v1?label=stackoverflow%20tag&logo=stackoverflow&logoColor=fe7a16&color=brightgreen&message=kivymd)](https://stackoverflow.com/tags/kivymd)
[![Open Collective](https://img.shields.io/opencollective/all/kivymd?label=financial%20contributors&logo=open-collective)](https://opencollective.com/kivymd)

[![Coverage status](https://coveralls.io/repos/github/kivymd/KivyMD/badge.svg)](https://coveralls.io/github/kivymd/KivyMD)
[![Build workflow](https://github.com/kivymd/KivyMD/workflows/Build/badge.svg?branch=master)](https://github.com/kivymd/KivyMD/actions?query=workflow%3ABuild)
[![Test workflow](https://github.com/kivymd/KivyMD/workflows/Test/badge.svg?branch=master)](https://github.com/kivymd/KivyMD/actions?query=workflow%3ATest)
[![Build demos workflow](https://github.com/kivymd/KivyMD/workflows/Build%20demos/badge.svg?branch=master)](https://github.com/kivymd/KivyMD/actions?query=workflow%3A"Build+demos")
[![Documentation status](https://readthedocs.org/projects/kivymd/badge/?version=latest)](https://kivymd.readthedocs.io)
[![Repository size](https://img.shields.io/github/repo-size/kivymd/kivymd.svg)](https://github.com/kivymd/KivyMD)

## Installation

```bash
pip install kivymd==0.104.2
```

### Dependencies:

- [Kivy](https://github.com/kivy/kivy) >= 2.0.0 ([Installation](https://kivy.org/doc/stable/gettingstarted/installation.html))
- [Python 3.6+](https://www.python.org/)
- [Pillow](https://github.com/python-pillow/Pillow/)

### How to install

Command [above](#installation) will install latest release version of KivyMD from 
[PyPI](https://pypi.org/project/kivymd).

If you want to install development version from 
[master](https://github.com/kivymd/KivyMD/tree/master/)
branch, you should specify link to zip archive:

```bash
pip install https://github.com/kivymd/KivyMD/archive/master.zip
```

**_Tip_**: Replace `master.zip` with `<commit hash>.zip` (eg `51b8ef0.zip`) to
download KivyMD from specific commit.

Also you can install manually from sources. Just clone the project and run pip:

```bash
git clone https://github.com/kivymd/KivyMD.git --depth 1
cd KivyMD
pip install .
```

**_Speed Tip_**: If you don't need full commit history (about 1.14 GiB), you can
use a shallow clone (`git clone https://github.com/kivymd/KivyMD.git --depth 1`)
to save time. If you need full commit history, then remove `--depth 1`.

### How to use 

```ini
requirements = kivy==2.0.0, kivymd==0.104.2, sdl2_ttf == 2.0.15, pillow
```

This will download latest release version of KivyMD from [PyPI](https://pypi.org/project/kivymd).

If you want to use development version from [master](https://github.com/kivymd/KivyMD/tree/master/)
branch, you should specify link to zip archive:

```ini
requirements = kivy==2.0.0, https://github.com/kivymd/KivyMD/archive/master.zip
```

Do not forget to run `buildozer android clean` or remove `.buildozer` directory
before building if version was updated (Buildozer doesn't update already
downloaded packages).



### Tutorials on YouTube

<p align="center">
  <a href="https://www.youtube.com/watch?v=kRWtSkIYPFI&list=PLy5hjmUzdc0nMkzhphsqgPCX62NFhkell&index=1">
    <img 
        width="400" 
        src="https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/tutorial.png" 
        title="Click to watch KivyMD Tutorials on YouTube"
    >
  </a>
</p>

[Tutorials](https://www.youtube.com/watch?v=kRWtSkIYPFI&list=PLy5hjmUzdc0nMkzhphsqgPCX62NFhkell&index=1) by [Erik Sandberg](https://github.com/Dirk-Sandberg) show you how to create application with KivyMD and use its widgets.


## Support

If you need assistance or you have a question, you can ask for help on our mailing list:

- **Discord server:** https://discord.gg/wu3qBST (English #support, Russian #ru-support)
- **StackOverflow tag:** [kivymd](https://stackoverflow.com/tags/kivymd)
- **Email:** kivydevelopment@gmail.com

## KivyMD Extensions

Additional extensions for the KivyMD library.

https://github.com/kivymd-extensions

<img align="left" width="128" src="https://github.com/kivymd/internal/raw/main/logo/kivymdbuilder.png"/>


## License

- KivyMD is released under the terms of the 
  under the terms of the [GNU General Public License], 
  same as [Kivy](https://github.com/kivy/kivy/blob/master/LICENSE).

### GC Tools Team

They spent a time improving GC Tools.

- Mateus Melo [@mateusmelo95](https://github.com/mateusmelo95) 
- Remis Balaniuk [@remis](https://github.com/remis) 

## Contributors


