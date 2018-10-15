"""A utility for parsing HTML Twine stories and saving them into json or graph formats."""
import re
import json
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
from graphviz import Digraph


class TwineGraph(object):
    """Twine graph class defining methods for parsing and graphing Twine stories."""

    regexes = {
        "angled_brackets": re.compile(r"\<\<([^\[\]]*?)\>\>"),
        "double_brackets": re.compile(r"\[\[([^\[\]]*?)\]\]"),
        "parentheses": re.compile(r"\(([^\(\)]*?)\)")
    }

    def __init__(self, in_prefix, in_format="html", twine_format="harlowe", encoding="utf-8"):
        """Loads a story either from html with parsing, or directly from json."""
        if in_format == "html":
            soup = BeautifulSoup(open(f"{in_prefix}.html", "r", -1, encoding, "ignore"), "lxml")
            self._parse_story(soup, twine_format)
        elif in_format == "json":
            self.story = json.load(open(f"{in_prefix}.json", "r", -1, encoding, "ignore"))

    def save_json(self, out_prefix):
        """Saves a json representation of the story to a file."""
        with open(f"{out_prefix}.json", 'w', -1, 'utf-8', 'ignore') as f:
            json.dump(self.story, f, indent=2)

    def save_graph(self, out_prefix, out_format='pdf', title=None, labels="passages"):
        """Saves a graph representation of the story to a file."""
        comment = out_prefix if title is None else title
        dot = Digraph(comment=comment)

        # Assign most common incoming edge label to each node.
        if labels == "links":
            passage_names = defaultdict(list)
            for passage in self.story["passages"]:
                for link in passage["links"]:
                    passage_names[link["destination"]["pid"]].append(link["text"])

        # Determine node name for each passage and create nodes
        for passage in self.story["passages"]:
            if labels == "links" and passage["pid"] in passage_names:
                passage_name = Counter(passage_names[passage["pid"]]).most_common(1)[0][0]
            else:
                passage_name = passage["name"]
            dot.node(str(passage["pid"]), passage_name)

        # Create edges for passages
        for passage in self.story["passages"]:
            for link in passage["links"]:
                dot.edge(str(passage["pid"]), str(link["destination"]["pid"]))
        dot.format = out_format
        dot.render(f"{out_prefix}.gv")

    def _parse_story(self, soup, twine_format):
        """Find all passage tags and pull text and links into a structured story."""
        self.story = {"passages": []}
        self.name_to_pid = {}

        # Store passages as a list and map names to ids
        passage_tag = "tw-passagedata" if twine_format == "harlowe" else "div"
        passages = []
        idx = 1
        for passage in soup.find_all(passage_tag):
            if twine_format == "sugarcube":  # and "tiddler" in passage:
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
                "links": self._find_links(passage_text)
            })

    def _find_links(self, text):
        """Discover multiple possible link types from a passage's text."""
        links = []
        # Look for action links
        for regex in ["parentheses", "angled_brackets"]:
            for link in self.regexes[regex].findall(text):
                action = re.match("(set|timedgoto|goto|go-to|display|link-goto)", link)
                if action:
                    single_quotes = re.findall("'(.*?)\'", link)
                    double_quotes = re.findall('"(.*?)"', link)
                    if double_quotes:
                        link_name = double_quotes[-1]
                    elif single_quotes:
                        link_name = single_quotes[-1]
                    else:
                        link_name = link.split(' ')[1]
                    links.append((link_name, f"<{action.group(0)}>"))

        # Look for regex links
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
