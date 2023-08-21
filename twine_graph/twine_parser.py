from html.parser import HTMLParser


class TwineParser(HTMLParser):
    class Passage:
        def __init__(self, passage_id, passage_name):
            self.id = passage_id
            self.name = passage_name.strip()
            self.text = ""

        def __iter__(self):
            return iter((self.id, self.name, self.text))


    version = None
    passages: list[Passage]

    def __init__(self):
        HTMLParser.__init__(self)
        self.passages = []
        self.in_tag = False
        self.idx = 1

    def handle_starttag(self, tag, attributes):
        if tag == 'div':
            twine_version = "v1";
        elif tag == 'tw-passagedata':
            twine_version = "v2"
        else:
            return

        if self.version is None:
            self.version = twine_version
        elif self.version != twine_version:
            raise ValueError("Invalid format")

        attributes = dict(attributes)
        if twine_version == "v1":
            try:
                passage_name = attributes["tiddler"]
                passage_id = self.idx
                self.idx += 1
            except KeyError:
                return
        else:  # twine_version == "v2":
            passage_name = attributes["name"]
            passage_id = int(attributes["pid"])

        self.passages.append(TwineParser.Passage(passage_id, passage_name))
        self.in_tag = True

    def handle_endtag(self, tag: str) -> None:
        if self.in_tag:
            if tag != ('tw-passagedata' if self.version == 'v2' else 'div'):
                raise ValueError("Invalid format")
            self.in_tag = False

    def handle_data(self, data):
        if self.in_tag:
            self.passages[-1].text += data
