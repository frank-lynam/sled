# sled
Frank's Starfield Linux ES\* Deployer

## Usage

This script sets up the Linux Steam version of Starfield with mods.

Download plugins as .zip, .7z or .rar and put them in `enabled/` and run `python3 sled.py`. The script will walk you through getting stuff working.

### SFSE

If you don't have SFSE, you'll need it, and this helps set it up for you. Just download the 7z file into the `enabled/` folder and it'll walk you through it. Same with the SFPTE plugins enabler. Just put it in there. Make sure their files start with those abbreviations.

If you want up update SFSE or SFPTE, put the new ones it in there and run `python3 sled.py sfse`.

### Load order

It loads them in alphabetical order linux-style (by ascii code). Change it up by changing the file names. Then re-deploy by running the script.

### But... why?

I do a lot of AI tinkering in my free time, which is easier on Linux. And Windows has felt like too much work lately, so I gave up on dual booting it. But if my hundreds of hours wandering Skyrim are any indication, I knew quality of life in Starfield would depend on mods. And there's just so many weird steps to making them work and I'm just so lazy! *So lazy!* So I made a script for it.

### Windows version?

No.

### I dunno git / bash

You should learn! It's easier than it looks. Just open a terminal, like xterm or whatever, and try this:

```bash
cd ~
mkdir workspace
cd workspace
git clone https://github.com/frank-lynam/sled
cd sled
```

Now you've got this code!

Download and copy plugins, SFSE and SFPTE into your ~/workspace/sled/enabled/` folder and then go back to your terminal and run:

```bash
cd ~/workspace/sled
python3 sled.py
```

And it should tell you everything you need to do =]
