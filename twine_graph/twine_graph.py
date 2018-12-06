"""A utility for parsing HTML Twine stories and saving them into json or graph formats."""
import re
import json
from bs4 import BeautifulSoup
from graphviz import Digraph


class TwineGraph(object):
    """Twine graph class defining methods for parsing and graphing Twine stories."""

    regexes = {
        "angled_brackets": re.compile(r"\<\<([^\[\]]*?)\>\>"),
        "double_brackets": re.compile(r"\[\[([^\[\]]*?)\]\]"),
        "parentheses": re.compile(r"\(([^\(\)]*?)\)"),
        "commands": re.compile(r"(display|go-to|goto|include|link-goto|set|timedgoto)")
    }

    def __init__(self, in_prefix, in_format="html", encoding="utf-8"):
        """Loads a story either from html with parsing, or directly from json."""
        if in_format == "html":
            soup = BeautifulSoup(open(f"{in_prefix}.html", "r", -1, encoding, "ignore"), "lxml")
            self._parse_story(soup)
        elif in_format == "json":
            self.story = json.load(open(f"{in_prefix}.json", "r", -1, encoding, "ignore"))
        else:
            raise ValueError(f"Invalid value for in_format: {in_format}")

    def save_json(self, out_prefix, indent=2):
        """Saves a json representation of the story to a file."""
        with open(f"{out_prefix}.json", 'w', -1, 'utf-8', 'ignore') as f:
            json.dump(self.story, f, indent=indent)

    def save_graph(self, out_prefix, out_format='pdf', title=None, passage_labels=True,
                   link_labels=False, remove_singletons=False, char_limit=80):
        """Saves a graph representation of the story to a file."""
        comment = title if title is not None else out_prefix
        dot = Digraph(comment=comment)

        # Find singletons
        if remove_singletons:
            pids_linked = set()
            for passage in self.story["passages"]:
                pids_linked.add(passage["pid"])
                for link in passage["links"]:
                    pids_linked.add(link["destination"]["pid"])

        # Determine node name for each passage and create nodes
        for passage in self.story["passages"]:
            if remove_singletons and passage["pid"] not in pids_linked:
                continue
            label = self._trim_text(passage["name"], char_limit) if passage_labels else None
            dot.node(str(passage["pid"]), label)

        # Create edges for passages
        for passage in self.story["passages"]:
            for link in passage["links"]:
                label = self._trim_text(link["text"], char_limit) if link_labels else None
                dot.edge(str(passage["pid"]), str(link["destination"]["pid"]), label)
        dot.format = out_format
        dot.render(f"{out_prefix}.gv")

    def _parse_story(self, soup):
        """Find all passage tags and pull text and links into a structured story."""
        self.story = {"passages": []}
        self.name_to_pid = {}

        # Detect Twine format automatically
        try:
            twine_format = "harlowe"
            passage_tag = "tw-passagedata"
            soup_passages = soup.find_all(passage_tag)
            assert len(soup_passages) > 0
        except AssertionError:
            twine_format = "sugarcube"
            passage_tag = "div"
            soup_passages = soup.find_all(passage_tag)

        # Store passages as a list and map names to ids
        idx = 1
        passages = []
        for passage in soup_passages:
            if twine_format == "sugarcube":
                try:
                    passage_name = passage["tiddler"]
                    passage_id = idx
                    idx += 1
                except KeyError:
                    continue
            elif twine_format == "harlowe":
                passage_name = passage["name"]
                passage_id = int(passage["pid"])
            else:
                continue
            self.name_to_pid[passage_name] = passage_id
            passages.append((passage_id, passage_name, passage.text))

        # Store passages into story as structured data
        for passage_id, passage_name, passage_text in passages:
            self.story["passages"].append({
                "pid": passage_id,
                "name": passage_name,
                "text": passage_text,
                "links": self._find_links(passage_text, twine_format=twine_format)
            })

    def _find_links(self, text, twine_format="harlowe"):
        """Discover multiple possible link types from a passage's text."""
        links = []

        # Look for command links
        if twine_format == "harlowe":
            regex = "parentheses"

        elif twine_format == "sugarcube":
            regex = "angled_brackets"
        else:
            raise ValueError(f"Invalid value for twine_format: {twine_format}")
        for link in self.regexes[regex].findall(text):
            command = self.regexes["commands"].match(link)
            if command:
                single_quotes = re.findall("'(.*?)\'", link)
                double_quotes = re.findall('"(.*?)"', link)
                if double_quotes:
                    link_name = double_quotes[-1]
                elif single_quotes:
                    link_name = single_quotes[-1]
                else:
                    link_name = link.split(' ')[1]
                links.append((link_name, f"<{command.group(0)}>"))

        # Look for native links
        for link in self.regexes["double_brackets"].findall(text):
            if len(link.split('<-')) == 2:
                link_name, link_text = link.split('<-')
            elif len(link.split('->')) == 2:
                link_text, link_name = link.split('->')
            elif len(link.split('|')) == 2:
                link_text, link_name = link.split('|')
            else:
                link_name = link
                link_text = link
            links.append((link_name, link_text))

        # Clean up links and put them into structured format
        structured_links = []
        for link_name, link_text in links:
            link_name = re.sub('"', '', link_name.strip())
            if link_name in self.name_to_pid:
                structured_links.append({
                    "text": link_text,
                    "destination": {
                        "name": link_name,
                        "pid": self.name_to_pid[link_name]
                    }
                })
        return structured_links

    def _trim_text(self, text, char_limit):
        """Trim a piece of text to conform to char limit."""
        if len(text) <= char_limit:
            return text
        else:
            chunk_len = int((char_limit - 5) / 2)
            return text[:chunk_len] + " ... " + text[-chunk_len:]
