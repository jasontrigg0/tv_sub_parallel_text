import subprocess
import os
import re
import argparse
import csv

#given the imdb code of a tv episode
#get an english <> spanish aligned text of the subtitles

#imdb code:
#https://www.imdb.com/title/tt0583459/?ref_=ttep_ep1 -> IMDB_ID = 583459 (ie what's after tt0)

#setup: downloaded the three entries under XCES/XML (xces en es)
#for OpenSubtitles v2018 on this page: http://opus.nlpl.eu/
#put these three files in SUBTITLES_DIR
#the XCES file is extracted into en-es.xml
#the other two is still zips (en.zip, es.zip)

#basically en.zip and es.zip contain a directory structure with {en,es}/year/episode/subtitle_file.xml
#(note there can be multiple subtitle files in the same episode directory -- I think these are redundant / different versions?
#en-es.xml is a file with full information about how to align all pairs of files from en.zip / es.zip

#general process:
#given an episode id: rip out the portion of en-es.xml that describes how to align that episode
#extract only the specific episode files from en.zip and es.zip
#then align using a tool called uplug-readalign
#downloaded from https://fastapi.metacpan.org/source/TIEDEMANN/uplug-main-0.3.8/tools/uplug-readalign
#into SUBTITLES_DIR

ALIGN_XML_START="""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE cesAlign PUBLIC "-//CES//DTD XML cesAlign//EN" "">
<cesAlign version="1.0">
<linkGrp targType="s" fromDoc="/tmp/en.xml" toDoc="/tmp/es.xml">
"""

ALIGN_XML_END="""</linkGrp>
</cesAlign>
"""

def read_cl():
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_csv')
    parser.add_argument('--imdb_id')
    args = parser.parse_args()
    return args

def align_imdb_id(imdb_id):
    SUBTITLES_DIR = "/ssd/files/aligned_subtitles/open_subtitles"

    #run grep command to get filenames and the lines to copy from en-es.xml
    #example output:
    #13657935:<linkGrp targType="s" fromDoc="en/1994/583459/6763337.xml.gz" toDoc="es/1994/583459/3515260.xml.gz">
    #13658435:</linkGrp>
    output = subprocess.check_output("less "+SUBTITLES_DIR+"/link_list.txt | grep -A1 '/"+str(imdb_id)+"/'", shell=True).decode("UTF-8")
    line1 = output.split("\n")[0].split(":")[0]
    line2 = output.split("\n")[1].split(":")[0]
    en_file = re.findall('fromDoc\="(.*?)"',output)[0] #format from en-es.xml: "en/1994/583459/6763337.xml.gz"
    en_file = "OpenSubtitles/xml/" + re.sub("\.gz$","",en_file) #format in the zip file: "OpenSubtitles/xml/en/1994/583459/6763337.xml"
    es_file = re.findall('toDoc\="(.*?)"',output)[0] #format from en-es.xml: "es/2014/3552926/5834596.xml.gz"
    es_file = "OpenSubtitles/xml/" + re.sub("\.gz$","",es_file) #format in zip file: "OpenSubtitles/xml/es/1994/583459/3515260.xml"
    with open("/tmp/align.xml", 'w') as f_out:
        f_out.write(ALIGN_XML_START)

    os.system("sed -n -e '"+str(int(line1)+1)+","+str(int(line2)-1)+"p' "+SUBTITLES_DIR+"/en-es.xml >> /tmp/align.xml")
    with open("/tmp/align.xml", 'a') as f_out:
        f_out.write(ALIGN_XML_END)

    os.system("unzip -p "+SUBTITLES_DIR+"/en.zip "+en_file+" > /tmp/en.xml")
    os.system("unzip -p "+SUBTITLES_DIR+"/es.zip "+es_file+" > /tmp/es.xml")
    os.system(SUBTITLES_DIR+f"/uplug-readalign /tmp/align.xml > /tmp/alignment_{imdb_id}.txt")

if __name__ == "__main__":
    args = read_cl()
    #IMDB_ID = 583459 #example: friends episode 1
    #IMDB_ID = 583647 #friends episode 2

    if args.episode_csv:
        with open(args.episode_csv) as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                try:
                    align_imdb_id(row["id"])
                except:
                    print(f"Unable to align {row}. Skipping...")
                    continue
    elif args.imdb_id:
        try:
            align_imdb_id(args.imdb_id)
        except:
            print(f"Unable to align")
    else:
        raise
