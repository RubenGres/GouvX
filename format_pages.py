import pandas as pd
import json
import os
import pandas as pd
import re


file_root = "data_scraped/"
files = [os.path.join(file_root, json_file) for  json_file in os.listdir(file_root)]

future_df = []

for json_file in files:
  with open(json_file, 'r') as file:
    json_file = json.load(file)

  future_df.append(json_file)

df = pd.DataFrame.from_dict(future_df)


def split_with_md_titles(text):
  # Define a regular expression pattern to match Markdown titles, regardless of level
  title_pattern = r'^(#+)\s*(.*?)\s*#*$'

  # Split the text into lines
  lines = text.split('\n')

  # Initialize a list to store title matches or lines that don't match
  title_matches = []

  # Iterate through each line in the Markdown content
  for line in lines:
    # Try to find a match for the title pattern
    match = re.match(title_pattern, line)

    # If a match is found, append it to the list; otherwise, append the original line
    if match:
        title_matches.append(match.groups())  # Append the matched title
    else:
        title_matches.append(('', line))  # Append the original line

  parsed_sections = []
  current_titles = []
  current_content = []

  for title_match in title_matches:
    title_level = len(title_match[0])  # Number of '#' symbols indicates the title level
    title_text = title_match[1].strip()  # Extract and remove leading/trailing spaces

    # Determine if it's a new section (indicated by a higher title level)
    if title_level == 0:
        current_content.append(title_text)
    else:
      if "\n".join(current_content).strip():
        parsed_sections.append([current_titles.copy(), "\n".join(current_content)])

      if len(current_titles) > 0:
        if title_level <= current_titles[-1][0]:
            current_titles = list(filter(lambda x: x[0] < title_level, current_titles))
            current_titles = current_titles if current_titles else []

      current_titles.append((title_level, title_text))
      current_content = []

  # Append the last section to the list
  parsed_sections.append([current_titles, "\n".join(current_content)])

  # Print the parsed sections (titles list and content)
  result = [{
    "subtitles": [title[1] for title in titles],
    "content": content.strip()
  } for titles, content in parsed_sections]

  return result


def separate_big_text(row):
    intro_len = 0
    if isinstance(row['intro'], str):
        intro_len = len(row['intro'].split())

    if len(row['content'].split()) + intro_len > 512:
        splitted = row['content'].split('\n')
        midpoint = len(splitted)//2
        part_one = splitted[:midpoint]
        part_two = splitted[midpoint:]
        return ['\n'.join(part_one), '\n'.join(part_two)]
    else:
        return row['content']


def combine_content(row):
    breadcrums = ' > '.join(row["breadcrums"])
    intro = row["intro"]

    subtitles = row["subtitles"]
    subtitles_str = ""
    for i, subtitle in enumerate(subtitles, start=1):
      subtitles_str += "#"*i + subtitle + "\n"

    content = row["content"]

    return f"{breadcrums}\n{intro}\n\n{subtitles_str}\n{content}"


df2 = df.copy()
df2['paragraph'] = df2['text'].apply(lambda x: split_with_md_titles(x))
df2 = df2.explode('paragraph')
df2 = pd.concat([df2.drop(['paragraph'], axis=1), df2['paragraph'].apply(pd.Series)], axis=1)

df2['content'] = df2.apply(separate_big_text, axis=1)
df2 = df2.explode('content')

df2["key_content"] = df2.apply(combine_content, axis=1)

df2['key_content_len'] = df2['key_content'].apply(lambda x: len(x.split()))
df2 = df2.sort_values(by='key_content_len', ascending=False)

df2.to_csv("service_public_content_wv.csv")