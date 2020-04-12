#read the output of an alignment and produce an epub file for
import re
import os
import csv
import argparse

#sample html:
#MUST: update
# <html>
#   <head><title>Title</title></head>
#   <body>
#     <div>
#       <div style="display:flex; width: 100%">
#         <div style="padding: 10px; width: 50%">Col 1 fdasfsafasfd safd safd saf dsaf dsaf dsa fdsa fdsa </div>
#         <div style="padding: 10px; width: 50%">Col 2 iuopiopipi po ipoi po i poi po ipoipoi poi po i po ipo ipoipoipo i poi po ipoipo iopi op io pi poiopiopip ou p y  up u pi op </div>
#       </div>
#       <div style="display:flex; width: 100%">
#         <div style="padding: 10px; width: 50%">Col 1 fdasfsafasfd safd safd saf dsaf dsaf dsa fdsa fdsa </div>
#         <div style="padding: 10px; width: 50%">Col 2 iuopiopipi po ipoi po i poi po ipoipoi poi po i po ipo ipoipoipo i poi po ipoipo iopi op io pi poiopiopip ou p y  up u pi op </div>
#       </div>
#     </div>
#   </body>
# </html>

def read_cl():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    args = parser.parse_args()
    return args

def alignment_to_paragraphs(alignment_file):
    #one div for each aligned paragraph
    with open(alignment_file) as f_in:
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
                #NOTE: flexbox and other column styles failed with .mobi format,
                #looked good in calibre with .mobi format and ebook-convert --mobi-file-type new
                #but didn't actually work on the kindle
                #tried a couple other things but ended up going with the table layout below
      #           paragraph_divs.append(("""
      # <div style="display:flex; width: 100%">
      #   <div style="padding: 10px; width: 50%">"""+text_chunk["trg"].strip("\n")+"""</div>
      #   <div style="padding: 10px; width: 50%">"""+text_chunk["src"].strip("\n")+"""</div>
      # </div>""").strip("\n"))


                #NOTE: this is the only way I could get multiple columns to show up
                #properly on kindle, even though I thought creating a .mobi with
                #ebook-convert --mobi-file-type new or creating a azw3 could work
                #tried to include padding but that didn't work on the kindle so going
                #with this barebones solution for now
                #L2 on the left, L1 on the right
                #creating separate table for each row is very slow (ran 10 hours with 4G memory
                #and didn't finish)
                #so instead trying one table for each episode -- I read warnings online that
                #tables that run across multiple pages can be problematic but maybe it'll work?
                paragraph_divs.append(("""
         <tr>
           <td>"""+text_chunk["trg"].strip("\n")+"""</td>
           <td>"""+text_chunk["src"].strip("\n")+"""</td>
         </tr>""").strip("\n"))
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

def get_start_html(title):
    return f"""
<html>
  <head>
    <title>{title}</title>
  </head>
  <body>
    <div>
""".strip("\n")

def get_end_html():
    return """
    </div>
  </body>
</html>
""".strip("\n")

def table_start():
    return """
       <table width="100%">
         <col width="50%">
         <col width="50%">
""".strip("\n")

def table_end():
    return """
       </table>
""".strip('\n')

if __name__ == "__main__":
    args = read_cl()

    episode_file = "/tmp/episodes.csv"
    with open(episode_file) as f_in:
        reader = csv.DictReader(f_in)
        html = ""
        html += get_start_html(args.title)
        for row in reader:
            if int(row["episode"]) == 1:
                html += "    <h1>Season " + row["season"] + "</h1>\n"
            html += "    <h2>Episode " + row["episode"] + "</h2>\n"
            alignment_filename = f"/tmp/alignment_{row['id']}.txt"
            if not os.path.exists(alignment_filename):
                #missing alignment
                continue
            html += table_start() + "\n"
            paragraph_divs = alignment_to_paragraphs(alignment_filename)
            html += "\n".join(paragraph_divs)
            html += table_end()
        html += get_end_html()
        print(html)
