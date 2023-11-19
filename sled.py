import os, sys

print()
print("Frank's Starfield Linux ESM Deployer!")
print("This tool finds your Starfield install and the associated compatdata folders, where Steam stores the plugin data.")
print("This can install sfse, modify your ini files and deploy plugins to the right compatdata folder for you")
print("To pick which mods are enabled, put them in the enabled folder")
print("To update sfse, put the new sfse in the enabled folder and run this with the \"sfse\" parameter")
print()

steamapps = os.path.expanduser("~") + "/.steam/steam/steamapps/"

sf = steamapps + "common/Starfield"

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

if not checkpath(sf.split("/")[1:], noisy=True):
  print("Couldn't find a Starfield install.\nThis requires you to install Starfield via Steam.")
  exit()

my_path = "pfx/drive_c/users/steamuser/My Documents/My Games/Starfield".split("/")
compats = []
for compat in os.listdir(steamapps + "compatdata"):
  if checkpath(my_path, steamapps + "compatdata/" + compat):
    compats.append(compat)

compats = sorted(compats)

if len(compats) == 0:
  print ("Dang, couldn't find Starfield. Have you installed and run it at least once in Steam?")
  exit()

print (f"Found {len(compats)} compatdata folders: {compats}")
print (f"Assuming {compats[0]} is the actual Starfield install")
print()

do_sfse = False
if len(compats) == 1:
  print ("Didn't see anything that looks like sfse has been run yet.")
  do_sfse = True

if do_sfse or "sfse" in sys.argv:
  if do_sfse and "sfse_loader.exe" in os.listdir(sf):
    print ("Looks like it's been added to your Starfield install, make sure you run it once!")
  if not any([x.startswith("SFSE") and x.endswith(".7z") for x in os.listdir("enabled")]):
    print("I don't see an sfse build in the enabled folder.\nIf want to add it or a new one to your Starfield install, download one and put it there and run this again to install it for you!")
    exit()
  else:
    print("Looks like there's an sfse build in the enabled folder.")
    print("Want me to add that sfse to your Starfield installation folder?")
    print("Then you'll have to add it to steam as an outside application, run it once and run this script again.")
    input("[y]: ", yn)
    if len(yn) > 0 and not yn.lower().startswith("y"):
      print("Alrighty, doing nothing =]")
      exit()
    print("Alrighty, installing sfse to Starfield folder")
    sf
    # extract SFSE stuff to the starfield binary folder
    # Then tell them how to add sfse as an app in steam
    # And run it once
  exit()

print(f"Assuming {compats[-1]} is the sfse compatdata folder")

cd = steamapps + "compatdata/" + compats[-1]
mygames = cd + "/" + "/".join(my_path)
appdata = cd + "/pfx/drive_c/users/steamuser/AppData/Local/Starfield"

if not checkpath(mygames.split("/")[1:], noisy=True):
  print("Couldn't find My Games folder for sfse install, have you run sfse in Steam yet?")
  exit()

if not checkpath(appdata.split("/")[1:], noisy=True):
  print("Couldn't find proper AppData folder for sfse install, have you run sfse in Steam yet?")
  exit()

print("Staging plugins")

if os.path.exists("staging"):
  os.system("rm -rf staging")
os.mkdir("staging")
os.mkdir("staging/a")
os.mkdir("staging/Data")

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
        if any([y.lower().endswith(z) for z in ["esm", "esp", "esl"]]):
          if not os.path.isdir(x + "/" + y):
            return x + "/" + y
    else:
      if "Data" in maybes: 
        return x + "/Data/"
      if "data" in maybes:
        return x + "/data/"
      if any([y.lower() in [z.lower() for z in maybes] for y in ["meshes", "textures", "geometries", "sound"]]):
        return x + "/"
  return find_data(stack[1:] + maybe, esm)

modlist = ["Mods staged:"]
for plugin in os.listdir("enabled"):
  print (f"\nProcessing {plugin}")
  os.system("chmod a+wr -R staging/a/b")
  os.system("rm -rf staging/a/b")
  os.mkdir("staging/a/b")
  if plugin.lower().endswith("7z"):
    if plugin.lower().startswith("sfse"):
      print("Skipping sfse")
      continue
    os.system(f"7z x 'enabled/{plugin}' -ostaging/a/b > /dev/null")
  elif plugin.lower().endswith("rar"):
    os.system(f"unrar x 'enabled/{plugin}' staging/a/b > /dev/null")
  elif plugin.lower().endswith("zip"):
    os.system(f"unzip 'enabled/{plugin}' -dstaging/a/b > /dev/null")
  else:
    print("Skipping, seems like prolly not a mod")
    continue

  paths = ["staging/a/b/" + x for x in os.listdir("staging/a/b")]

  data_path = find_data(["staging/a"])
  esm_path = find_data(["staging/a"], True)
  if data_path == None and esm_path == None:
    print ("Warning! No data or esm found!")
  else:
    modlist.append(plugin)
    if data_path != None:
      print (f"Using {data_path[11:]}")
      if esm_path != None and data_path in esm_path:
        print (f"Skipping {esm_path[11:]}, already in data path")
        esm_path = None
      os.system(f"cp -r {data_path}* staging/Data")
    if esm_path != None:
      print (f"Using {esm_path[11:]}")
      os.system(f"cp {esm_path} staging/Data")

os.system("chmod a+wr -R staging/a/b")
os.system("rm -rf staging/a/b")

plugin_txt = "# Autogenerated by Frank's Sled!"
for y in os.listdir("staging/Data"):
  if any([y.lower().endswith(z) for z in ["esm", "esp", "esl"]]):
    if not os.path.isdir("staging/Data/" + y):
      plugin_txt += "\n*" + y

print ("\nWriting Plugins.txt:\n" + plugin_txt)
with open(appdata + "/Plugins.txt", "w") as fl:
  fl.write(plugin_txt)

print ("\nDeleting existing Data folder")
os.system(f"rm -rf '{mygames}/Data'")

print ("Moving over staged data")
os.system(f"mv staging/Data '{mygames}'")
os.rmdir("staging/a")
os.rmdir("staging")

print ("\n" + "\n - ".join(modlist))

print ("\nReady to play! Go launch sfse from Steam =]\n")
