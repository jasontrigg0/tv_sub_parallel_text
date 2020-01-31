#read the output of an alignment and produce an epub file for
import re
import os
import csv

#sample html:
# <html>
#   <div>
#     <div style="display:flex; width: 100%">
#       <div style="margin: 10px; width: 50%">Col 1 fdasfsafasfd safd safd saf dsaf dsaf dsa fdsa fdsa </div>
#       <div style="margin: 10px; width: 50%">Col 2 iuopiopipi po ipoi po i poi po ipoipoi poi po i po ipo ipoipoipo i poi po ipoipo iopi op io pi poiopiopip ou p y  up u pi op </div>
#     </div>
#     <div style="display:flex; width: 100%">
#       <div style="margin: 10px; width: 50%">Col 1 fdasfsafasfd safd safd saf dsaf dsaf dsa fdsa fdsa </div>
#       <div style="margin: 10px; width: 50%">Col 2 iuopiopipi po ipoi po i poi po ipoipoi poi po i po ipo ipoipoipo i poi po ipoipo iopi op io pi poiopiopip ou p y  up u pi op </div>
#     </div>
#   </div>
# </html>

START_HTML = """
<html>
  <div>
""".strip("\n")
END_HTML = """
  </div>
</html>
""".strip("\n")

def alignment_to_paragraphs(alignment_file):
    #one div for each aligned paragraph
    with open("/tmp/alignment.txt") as f_in:
        text_chunk = {} #{src:"", trg:""}
        paragraph_divs = []
        in_body = False
        for l in f_in:
            is_delim = "========" in l
            if not in_body:
                if is_delim:
                    in_body = True
                continue

            if is_delim:
                paragraph_divs.append(("""
    <div style="display:flex; width: 100%">
      <div style="margin: 10px; width: 50%">"""+text_chunk["src"].strip("\n")+"""</div>
      <div style="margin: 10px; width: 50%">"""+text_chunk["trg"].strip("\n")+"""</div>
    </div>""").strip("\n"))
                text_chunk = {}
            else:
                src_pattern = "\(src\)=\"\d+\">"
                trg_pattern = "\(trg\)=\"\d+\">"
                if re.findall(src_pattern,l):
                    l = re.sub(src_pattern,"",l)
                    l = l.strip(" ")
                    text_chunk["src"] = text_chunk.get("src","") + l
                elif re.findall(trg_pattern,l):
                    l = re.sub(trg_pattern,"",l)
                    l = l.strip(" ")
                    text_chunk["trg"] = text_chunk.get("trg","") + l
                else:
                    print(l)
                    raise
    return paragraph_divs

if __name__ == "__main__":
    episode_file = "/tmp/episodes.csv"
    with open(episode_file) as f_in:
        reader = csv.DictReader(f_in)
        html = ""
        html += START_HTML
        for row in reader:
            if int(row["episode"]) == 1:
                html += "    <h1>Season " + row["season"] + "</h1>\n"
            html += "    <h2>Episode " + row["episode"] + "</h2>\n"
            alignment_filename = f"/tmp/alignment_{row['id']}.txt"
            paragraph_divs = alignment_to_paragraphs(alignment_filename)
            html += "\n".join(paragraph_divs)
            if int(row["episode"]) > 5: #MUST remove
                break
        html += END_HTML
        print(html)
