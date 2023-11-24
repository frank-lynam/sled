import os, sys

# Intro text
print()
print("Frank's Starfield Linux ESM Deployer!")
print("This tool finds your Starfield install and the "
  + "associated compatdata folders, where Steam stores "
  + "the plugin data.")
print("This can install sfse, modify your ini files and "
  + "deploy plugins to the right compatdata folder for you")
print("To pick which mods are enabled, put them in the "
  + "enabled folder, the load order is alphabetical")
print("To update sfse, put the new sfse in the enabled "
  + "folder and run this with the \"sfse\" parameter")
print()

# Set up file paths
steamapps = os.path.expanduser("~") + "/.steam/steam/steamapps/"

sf = steamapps + "common/Starfield"

# Sanitize file paths for shell commands
def sn(t):
  for x in "() '\"":
    t = t.replace(x,"\\"+x)
  return t

# See if a path exists
def checkpath(t, p="", noisy=False):
  if len(t) == 0:
    if noisy:
      print (f"Found {p}")
    return True
  if p == "" or t[0] in os.listdir(p):
    return checkpath(t[1:], p + "/" + t[0], noisy)
  else:
    if noisy:
      print (f"Couldn't find {t[0]} in {p}")
    return False

# Check if Starfield is installed
if not checkpath(sf.split("/")[1:], noisy=True):
  print("Couldn't find a Starfield install.")
  print("Sled requires you to install Starfield via Steam.")
  exit()

# Check for compatdata paths
my_path = ("pfx/drive_c/users/steamuser/My Documents/My "
  + "Games/Starfield").split("/")
compats = []
for compat in os.listdir(steamapps + "compatdata"):
  if checkpath(my_path, steamapps + "compatdata/" + compat):
    compats.append(compat)

compats = sorted(compats)

if len(compats) == 0:
  print ("Dang, couldn't find Starfield My Games folder.")
  print("Have you installed and run it at least once in Steam?")
  exit()

if not os.path.isdir("enabled"):
  os.mkdir("enabled")

print (f"Found {len(compats)} compatdata folders: {compats}")
print (f"Assuming {compats[0]} is the actual Starfield install")
print()

# Check for sfse compatdata
do_sfse = False
if len(compats) == 1:
  print ("Didn't see anything that looks like sfse has been run yet.")
  do_sfse = True

# This finds files to use in plugins
def find_data(stack, esm=False):
  if len(stack) == 0:
    return None
  maybe = [stack[0] + "/" + x 
    for x in os.listdir(stack[0])
    if os.path.isdir(stack[0] + "/" + x)]
  for x in maybe:
    maybes = os.listdir(x)
    if esm:
      for y in maybes:
        if any([y.lower().endswith(z) for z in esm]):
          if not os.path.isdir(x + "/" + y):
            return x + "/" + y
    else:
      if "Data" in maybes: 
        return x + "/Data/"
      if "data" in maybes:
        return x + "/data/"
      if any([y.lower() in [z.lower() for z in maybes] 
              for y in ["meshes", "textures", "geometries", "sound"]]):
        return x + "/"
  return find_data(stack[1:] + maybe, esm)

# Extracts various compressed filetypes
def extract(source, dest="staging/a/b"):
  if source.lower().endswith("7z"):
    os.system(f"7z x {sn(source)} -o{sn(dest)} > /dev/null")
  elif plugin.lower().endswith("rar"):
    os.system(f"unrar x {sn(source)} {sn(dest)} > /dev/null")
  elif plugin.lower().endswith("zip"):
    os.system(f"unzip {sn(source)} -d{sn(dest)} > /dev/null")
  else:
    return False
  return True

# Handle the sfse install if needed
if do_sfse or "sfse" in sys.argv:
  if do_sfse and "sfse_loader.exe" in os.listdir(sf):
    print ("Looks like it's been added to your Starfield install, "
      + "make sure you run it once!")
  if not any([x.lower().startswith("sfse") and x.endswith(".7z") 
              for x in os.listdir("enabled")]):
    print("I don't see an sfse build in the enabled folder.")
    print("If want to add it or a new one to your Starfield install, "
      + "download one and put it there and run this again to install "
      + "it for you!")
    exit()
  else:
    print("Looks like there's an sfse build in the enabled folder.")
    print("Want me to add that sfse to your Starfield installation "
      + "folder?")
    print("Then you'll have to add it to steam as an outside "
      + "application, run it once and run this script again.")
    yn = input("[y]: ")
    if len(yn) > 0 and not yn.lower().startswith("y"):
      print("Alrighty, doing nothing =]")
      exit()
    print("Alrighty, installing sfse to Starfield folder")

    # Extract and find sfse and sfpte files
    if os.path.exists("staging"):
      os.system("rm -rf staging")
    os.system("mkdir -p staging/a/b")
    for sfse in [["sfse", sf], ["sfpte", sf + "/Data/SFSE/Plugins"]]:
      print ("Looking for " + sfse[0])
      for plugin in os.listdir("enabled"):
        if plugin.lower().startswith(sfse[0]):
          print("Using " + plugin)
          os.system("rm -rf staging/a/b/*")
          extract("enabled/" + plugin, dest="staging/a/b")
          os.system(f"mkdir -p {sn(sfse[1])}")
          for ft in ["exe", "dll"]:
            item = find_data(["staging/a"], ft)
            if item:
              print(f"Found {item[11:]}")
              os.system(f"cp {sn(item)} {sn(sfse[1])}")
          break

    # Clean up and give some guidance
    os.system("chmod a+wr -R staging")
    os.system("rm -rf staging")

    print ("SFSE should be in the Starfield folder now")
    print ("Now you need to add it as an external game in Steam "
      + "and launch it at least once")
    print ("Load Steam, go to Games -> Add a Non-Steam Game to "
      + "My Library...")
    print (f"Then navigate to {sf}")
    print ("And add \"sfse_loader.exe\" as a game and load it once")
    print ("It should load a little terminal window then "
      + "eventually load Starfield")
    print ("If you stream games to another machine, do this through "
      + "VNC first, then Connect to Starfield after it loads")
    print ("Once you exit Starfield, run this again to install "
      + "the plugins! =]\n")
  exit()

# Do plugin install
print(f"Assuming {compats[-1]} is the sfse compatdata folder")

# Check for My Games folder
cd = steamapps + "compatdata/" + compats[-1]
mygames = cd + "/" + "/".join(my_path)
appdata = cd + "/pfx/drive_c/users/steamuser/AppData/Local/Starfield"

if not checkpath(mygames.split("/")[1:], noisy=True):
  print("Couldn't find My Games folder for sfse install, "
    + "have you run sfse in Steam yet?")
  exit()

if not checkpath(appdata.split("/")[1:], noisy=True):
  print("Couldn't find proper AppData folder for sfse install, "
    + "have you run sfse in Steam yet?")
  exit()

print("Staging plugins")

if os.path.exists("staging"):
  os.system("rm -rf staging")
os.mkdir("staging")
os.mkdir("staging/a")
os.mkdir("staging/a/b")
os.mkdir("staging/Data")

# This was an idea I had to fix some issues with
# path case sensitivity that didn't help
def recurse_lower(source, dest, lower=True):
  if lower:
    os.system(f"find {sn(source)}* > .sledding")
    with open(".sledding") as fl:
      sources = [x.strip() for x in fl.readlines()]
    os.remove(".sledding")
    [os.system(f"mkdir -p " +
  f"{sn(dest+'/'+'/'.join(x[len(source):].lower().split('/')[:-1]))}"
     + f" && cp {sn(x)} {sn(dest + x[len(source):].lower())}") 
     for x in sources if os.path.isfile(x)]
  else: 
    os.system(f"cp -r {sn(source)}* {sn(dest)}")

# This lets you know when one plugin is overwriting another
def check_conflicts(source, dest):
  os.system(f"find {sn(source)}* > .sledding")
  with open(".sledding") as fl:
    sources = [x.strip() for x in fl.readlines()]
  os.remove(".sledding")
  dests = [dest + "/" + 
    '/'.join(x[len(source):].lower().split('/')[:-1]) 
    for x in sources if os.path.isfile(x)]
  return [x for x in dests if os.path.isfile(x)]

# This is the loop that actually stages the data
modlist = ["Mods staged:"]
warnings = []
enabled = sorted(os.listdir("enabled"))
for plugin in enabled:
  print (f"\nProcessing {plugin}")
  os.system("chmod a+wr -R staging/a/b")
  os.system("rm -rf staging/a/b")
  os.mkdir("staging/a/b")
  if any([plugin.lower().startswith(x) for x in ["sfse", "sfpte"]]):
    print("Skipping sfse stuff")
    continue
  if not extract("enabled/" + plugin):
    print("Skipping, seems like prolly not a mod")
    continue

  # This was a design choice I made for the find data function
  # to make recursion easiet
  paths = ["staging/a/b/" + x for x in os.listdir("staging/a/b")]

  # This slightly convoluted logic is in case there's an esm not
  # in the data folder
  data_path = find_data(["staging/a"])
  esm_path = find_data(["staging/a"], ["esm", "esp", "esl"])
  if data_path == None and esm_path == None:
    print ("Warning! No data or esm found!")
    warnings.append(f"No data or esm found in {plugin}")
  else:
    modlist.append(plugin)
    if data_path != None:
      print (f"Using {data_path[11:]}")
      if esm_path != None and data_path in esm_path:
        print (f"Skipping {esm_path[11:]}, already in data path")
        esm_path = None
      warnings = warnings + [f"File conflict when adding {plugin}: " 
        + x for x in check_conflicts(data_path, "staging/Data")]
      recurse_lower(data_path, "staging/Data/")
    if esm_path != None:
      print (f"Using {esm_path[11:]}")
      os.system(f"cp {sn(esm_path)} staging/Data")

os.system("chmod a+wr -R staging/a/b")
os.system("rm -rf staging/a/b")

# Since linux is case sensitive, some plugins capitalize the
# data folders and some don't and this seemed to cause issues
os.system("chmod a+wr -R staging/Data")
for x in ["textures", "meshes", "geometries", "sound"]:
  if (x.title() in os.listdir("staging/Data") 
      and x in os.listdir("staging/Data")):
    os.system(f"cp -r staging/Data/{x.title()}/* staging/Data/{x}/")
    os.system(f"rm -rf staging/Data/{x.title()}")

# Create the plugins.txt file
plugin_txt = "# Autogenerated by Frank's Sled!"
for y in os.listdir("staging/Data"):
  if any([y.lower().endswith(z) for z in ["esm", "esp", "esl"]]):
    if not os.path.isdir("staging/Data/" + y):
      plugin_txt += "\n*" + y

print ("\nWriting plugins.txt:\n" + plugin_txt)
with open(appdata + "/plugins.txt", "w") as fl:
  fl.write(plugin_txt)

# Move over the staged data
print ("\nDeleting existing Data folder")
os.system(f"rm -rf {sn(mygames)}/Data")

print ("Moving over staged data")
os.system(f"mv staging/Data {sn(mygames)}")
os.rmdir("staging/a")
os.rmdir("staging")

# Do the bInvalidate thing in both places just in case
with open(mygames + "/StarfieldPrefs.ini") as fl:
  prefs = fl.read()
if "bInvalidateOlderFiles" in prefs:
  print ("\nbInvalidateOlderFiles confirmed")
else:
  prefs.replace("[Archive]", "[Archive]\nbInvalidateOlderFiles=1")
  with open(mygames + "StarfieldPrefs.ini", "W") as fl:
    fl.write(prefs)
  print ("\nbInvalidateOlderFiles added!")

with open(mygames + "/StarfieldCustom.ini", "w") as fl:
  fl.write("[Archive]\nbInvalidateOlderFiles=1\n"
           + "sResourceDataDirsFinal=")
print ("StarfieldCustom.ini also written")

# Display any warnings last
print ("\n" + "\n - ".join(modlist))
if len(warnings) > 0:
  print("\nWarnings:" + "\n - ".join(warnings))

print ("\nReady to play! Go launch sfse from Steam =]\n")
