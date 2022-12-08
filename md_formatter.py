from collections.abc import Callable
import os

numbers = list("0123456789")
letters = list("abcdefghijklmnopqrstuvwxyz")
newlines = ["\n", "\r", "\r\n", "\n\r"]
illegal_chars = '<>:"/\|?*' + '[]'

# tools

def is_p(line: str):
    return (
        len(line) >= 1 and not line[0] == " " and not is_nl(line)
        and not is_h(line)
        and not is_li(line)
        and not is_blockquote(line)
        and not is_codeblock_fence(line)
        and not is_tr(line)
        and not is_footnote(line)
        and not is_dv_inline_field(line))

def is_ul_li(line: str):
    line = line.strip()
    return len(line) >= 1 and line[0] in ["-", "*", "+"] and (len(line) == 1 or line[1] == " ")

def is_ul_cb(line: str):
    # - [ ]
    line = line.strip()
    return (len(line) >= 5
        and line[0] in ["-", "*", "+"]
        and line[1] == " "
        and line[2] == "["
        and line[4] == "]"
        and (len(line) == 5 or line[5] == " "))

def is_ol_li(line: str):
    line = line.strip()

    dotindex = line.find(".")

    if dotindex not in [-1, 0]:
        potential_number = line[:dotindex]
        for c in potential_number:
            if c not in numbers:
                return False

        return len(line) == dotindex + 1 or line[dotindex + 1] == " "

    return False

def is_li(line: str):
    return is_ul_li(line) or is_ol_li(line)

def is_blockquote(line: str):
    line = line.strip()
    return len(line) >= 1 and line[0] == ">" and (len(line) == 1 or line[1] == " ")

def is_codeblock_fence(line: str):
    return len(line) >= 3 and line.strip()[:3] == "```"

def is_nl(line: str):
    return len(line) == 1 and line[0] in newlines

def is_h(line: str, min_level: int = 1, max_level: int = 6, ignore_level=None):
    for level in range(min_level, max_level + 1):
        if ignore_level == level:
            continue
        if line.startswith(h(level)):
            return True

    return False

def is_tr(line: str):
    return len(line) >= 1 and line[0] == "|"

def is_footnote(line: str):
    line = line.strip()
    return len(line) >= 5 and line[0:2] == "[^" and "]:" in line

def is_forcing_nl(line: str):
    return len(line) >= 1 and line.strip()[-1] == "\\"

def is_dv_inline_field(line: str):
    line = line.strip()
    return line.find("::") > 0

# update tools

def link(filename: str, alias: str = None) -> str:
    return f"[[{filename[:-3] + (f'|{alias}' if alias else '')}]]"

def remove_links(line: str):
    while "[[" in line:
        # if linked with alias, only keep alias
        end = line.find("]]")
        if "|" in line[:end]:
            start = line.find("[[")
            middle = line.find("|")
            line = line[:start + 2] + line[middle + 1:]

        line = line.replace("[[", "", 1).replace("]]", "", 1)

    return line

def h(level: int):
    if level not in range(1, 7):
        return None

    return level * "#" + " "

def italic(s: str):
    return "_" + s + "_"

# read/write tools

def write_lines(lines: list, dir_: str):
    with open(dir_, "w", encoding="utf-8") as file:
        print(f"writing {dir_} ...")
        file.writelines(lines)

def write(text: str, dir_: str):
    with open(dir_, "w", encoding="utf-8") as file:
        print(f"writing {dir_} ...")
        file.write(text)

def remove_illegal_chars(s: str):
    for c in illegal_chars:
        s = s.replace(c, "")
    return s

def on_all(folder_path: str, do: list[Callable[[list[str]], list[str]]]):
    print(f"---\nreading {folder_path} ...")

    for filename in os.listdir(folder_path):
        dir_ = os.path.join(folder_path, filename)

        # skip hidden files and folders
        if filename[0] == ".":
            print(f"skipping {dir_} (hidden)")
            continue

        # skip non-markdown files
        dotindex = filename.rfind(".")
        if dotindex != -1 and filename[dotindex + 1:] != "md":
            print(f"skipping {dir_} (not md)")
            continue

        try:
            with open(dir_, "r", encoding="utf-8") as file:
                try:
                    lines = file.readlines()
                    new_lines = lines

                    for do_ in do:
                        new_lines = do_(new_lines)

                    # only write if something has changed
                    if new_lines != lines:
                        write_lines(new_lines, dir_)

                except UnicodeDecodeError:
                    # probably not a text file
                    print(f"couldn't decode {dir_}")
                    continue

        except PermissionError:
            # we hit a folder; recurse
            on_all(dir_, do)

# format

def format_blanklines(lines: list[str]) -> list[str]:
    new_lines = []

    # needed for merging multiple paragraphs
    lines.append("\n")

    is_first_text_found = False
    is_in_frontmatter = False
    is_in_code_block = False
    line_next_already_added = 0

    for i in range(len(lines) - 1):
        if line_next_already_added > 0:
            line_next_already_added -= 1
            continue

        line = lines[i]
        line_next = lines[i + 1]

        if not is_first_text_found:
            # remove leading blanklines
            if line == "\n":
                continue
            else:
                is_first_text_found = True

                # look for frontmatter
                if line.strip() == "---":
                    is_in_frontmatter = True
                    new_lines.append(line)
                    continue

        # don't format frontmatter
        if is_in_frontmatter:
            if line.strip() == "---":
                is_in_frontmatter = False
            new_lines.append(line)
            continue

        # don't format codeblocks
        if line.strip()[:3] == "```":
            is_in_code_block = not is_in_code_block
            new_lines.append(line)
            continue
        if is_in_code_block or (len(line) > 4 and line[:4] == "    "):
            new_lines.append(line)
            continue

        # don't format tables
        if is_tr(line):
            new_lines.append(line)
            continue

        # if multiple consecutive lines are normal paragraphs,
        # they are probably meant to be one paragraph and not many.
        if is_p(line) and not is_forcing_nl(line):
            line_concat = line
            n_merged = 0

            # concate consecutive lines
            for j in range(i + 1, len(lines) - 1):
                if is_p(lines[j]):
                    line_concat = line_concat.rstrip() + " " + line_next.lstrip()
                    n_merged += 1
                else:
                    break

            line = line_concat
            line_next = lines[i + 1 + n_merged]
            line_next_already_added += n_merged

        # remove double blanklines
        if not (is_nl(line) and is_nl(line_next)):
            new_lines.append(line)

        # add blanklines after everything except
        # - lists
        # - backslashes
        # - multi-line footnotes with lists
        if (
            len(line) >= 1
            and not is_nl(line) and not is_nl(line_next)
            and not is_li(line) and not is_blockquote(line)
            and not is_forcing_nl(line)
            and not (is_footnote(line) and is_li(line_next))):

            new_lines.append("\n")

    # add last line
    if len(lines) > 0 and lines[-1] != "\n":
        # strip and add nl to keep empty files one line long
        new_lines.append(lines[-1].rstrip() + "\n")

    return new_lines

def trim_trailing_whitespace(lines: list[str]) -> list[str]:
    # also makes sure the files ends with a blankline

    new_lines = []

    for line in lines:
        line = line.rstrip()
        line_ending = "\n"

        # keep whitespace after empty list item
        if KEEP_WHITESPACE_AFTER_EMPTY_LI:
            is_empty_ul_li = len(line) == 1 and is_ul_li(line)
            is_empty_ul_cb = len(line) == 5 and is_ul_cb(line)
            is_empty_ol_li = is_ol_li(line) and len(line[line.find("."):]) == 1
            is_empty_dv_inline_field = is_dv_inline_field(line) and len(line[line.find("::"):]) == 2

            if is_empty_ul_li or is_empty_ul_cb or is_empty_ol_li or is_empty_dv_inline_field:
                line_ending = " " + line_ending

        new_lines.append(line + line_ending)

    return new_lines

def replace_chars(lines: list[str]) -> list[str]:
    new_lines = []

    for line in lines:
        for rule in REPLACE_CHARS_RULES:
            line = line.replace(rule[0], rule[1])

        new_lines.append(line)

    return new_lines

def format(folder_path: str):
    print(f"\nFormatting {folder_path}\n---")

    # order is important
    on_all(folder_path, [replace_chars, trim_trailing_whitespace, format_blanklines])

    print("---\nDone!\n")

# external

def embed_gdoc_comments(path: str, filename: str):
    dir_ = path + filename

    print("reading ...")
    print("---")

    letters0 = list("abcdefghijklmnopqrstuvwxyz")
    letters0.insert(0,"")
    n = 26

    # go backwards to easily retreive the last comment
    # – since it ends with the end of the file
    for i in reversed(range(n ** 2 + n)):
        c0 = letters0[i // n]
        c1 = letters[i % n]
        tag = "[" + c0 + c1 + "]"

        new_text = ""

        with open(dir_, "r", encoding="utf-8") as file:
            text = file.read()
            l_index = text.find(tag)
            r_index = text.rfind(tag)

            if l_index == -1 or r_index == -1:
                continue

            print(tag, "at", l_index, "and", r_index)

            # remove tag
            new_text = text[:l_index] + text[l_index + len(tag):]

            # by default, insert comment at end of file
            bl_index = len(text) - 1

            for char_index in range(l_index + len(tag), len(text)):
                # find a blank line
                if text[char_index:char_index + 2] == "\n\n":
                    bl_index = char_index
                    print("blank line at", bl_index)
                    break

            # since we have removed the tag
            bl_index = bl_index - len(tag)

            # retreive comment
            comment = text[r_index + len(tag):]

            # remove comment from bottom
            new_text = new_text[:r_index - len(tag)]
            # insert comment at blank line nearest tag
            # +2 to get between the newlines
            new_text = new_text[:bl_index + 2] + comment + new_text[bl_index + 2:]

        write(new_text, dir_)

    print("---")
    print("done!")

def embed_dreams(days_folder_path: str, dreams_folder_path: str):
    print("searching ...")

    dreams = os.listdir(dreams_folder_path)
    days = os.listdir(days_folder_path)

    for dream in dreams:
        date = dream[2:len("d-YYYY-MM-dd")]

        for day in days:
            if day.startswith(date):
                day_dir = os.path.join(days_folder_path, day)
                embed_dream(day_dir, dream)

                break

    print("done!")

def embed_dream(day_dir: str, dream_filename: str):
    dream_link = link(dream_filename)
    new_lines = []

    with open(day_dir, "r", encoding="utf-8") as file:
        text = file.read()
        if dream_filename[:-3] in text:
            return

    with open(day_dir, "r", encoding="utf-8") as file:
        dream_added = False

        for line in file.readlines():
            line_stripped = line.strip()

            # first paragraph
            if not dream_added and len(line_stripped) > 0 and line_stripped[0] not in ["-", "#"]:
                new_lines.append(dream_link)
                new_lines.append("\n\n")
                new_lines.append(line)

                dream_added = True
                continue
            else:
                new_lines.append(line)

    write_lines(new_lines, day_dir)

# main

KEEP_WHITESPACE_AFTER_EMPTY_LI = True
REPLACE_CHARS_RULES = [
    ["…", "..."],
    ['“', '"'],
    ['”', '"'],
    ["‘", "'"],
    ["’", "'"],
    #["—", "–"],
    ["	", "  "]]

def main():
    print("\n-------")
    print("NEW RUN")
    print("-------\n")

    root = "../writing"
    folder = f"{root}/"
    folder1 = f"{root}/dokumentation/dagbok/2018/dagar"

    format(folder)

if __name__ == "__main__":
    main()
