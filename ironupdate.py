import zipfile
import httpx
import sys, os

source = 'https://github.com/najis-poop/IronHeartBot/archive/refs/heads/master.zip'

print("Downloading IronHeartBot from", source)

with httpx.stream('GET', source) as r:
    a = ('\\','|','/','-','|')
    i = 0
    with open("source.zip", "a") as fp:
        for data in r.iter_bytes():
            fp.write(data)
            sys.stdout.write(f'\rDownloading ({r.num_bytes_downloaded} bytes) [{a[i]}]')
            sys.stdout.flush()
            i += 1
            if i == 4:
                i = 0
    sys.stdout.write('\rDownloading: Finished')
    sys.stdout.flush()

a = input('Do you want to extract the zip? [N/y]: ').lower().strip()

if a in ['y','yes']:
    pass
elif (a in ['n','no']) or not a:
    print("Finish updating")
    exit(0)

with zipfile.ZipFile('source.zip') as zipr:
    ld = os.listdir()
    for f in zipr.filelist:
        print(f"Extracting {f.filename}")
        if f.filename in ld:
            print(f"Found {f.filename} in the directory already")
            if not input("\tReplace? (Leave empty for `no`): "):
                continue
        zipr.extract(f)

print("Finish updating")