import argparse
import json
import os.path as op
from .twine_graph import TwineGraph


def save_graph(story, out_prefix, out_format='pdf', title=None, passage_labels=True,
                link_labels=False, remove_singletons=False, char_limit=80):
    """Saves a graph representation of the story to a file."""    
    from graphviz import Digraph

    comment = title if title is not None else out_prefix
    dot = Digraph(comment=comment)

    nodes, edges = story.save_graph(
        passage_labels, link_labels, remove_singletons, char_limit)

    for id, label in nodes:
        dot.node(id, label)
    for source, target, label in edges:
        dot.edge(source, target, label)

    dot.format = out_format
    dot.render(f"{out_prefix}.gv")


def main():
    """Given arguments, loads a Twine story and saves it to a specific output format."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("infile", help="Location of input file, ending in either .html or .json.")
    parser.add_argument("--title", default=None, help="Title of Twine story for graph output.")
    parser.add_argument("--labels", default="passages", choices=["passages", "links", "both"],
                        help="Whether to derive graph labels from story 'passages' or 'links'.")
    parser.add_argument("--encoding", default="utf-8", help="Character encoding of input file.")
    parser.add_argument("--nograph", default=False, action='store_true', help="Don't output graph.")
    parser.add_argument("--graph-format", default="pdf", help="Render format to use for graphviz.")
    parser.add_argument("--remove-singletons", default=False, action='store_true',
                        help="Remove unconnected single nodes from pdf output.")
    parser.add_argument("--char-limit", type=int, default=80, help="Max size in pdf output texts.")
    args = parser.parse_args()

    file_root, file_ext = op.splitext(args.infile)
    if file_ext not in [".html", ".json"]:
        raise ValueError("Invalid input file: must be .html or .json format.")

    with open(args.infile, "r", -1, args.encoding, "ignore") as fd:
        source = fd.read()
    story = TwineGraph(
        source,
        in_format=file_ext[1:]
    )

    if file_ext != ".json":
        with open(f"{file_root}.json", 'w', -1, 'utf-8', 'ignore') as fp:
            json.dump(story.story, fp, indent=2)
    if not args.nograph:
        passage_labels = True if args.labels in ["passages", "both"] else False
        link_labels = True if args.labels in ["links", "both"] else False
        try:
            save_graph(story, file_root, out_format=args.graph_format, title=args.title,
                       passage_labels=passage_labels, link_labels=link_labels,
                       remove_singletons=args.remove_singletons, char_limit=args.char_limit)
        except ImportError:
            raise ImportError("The graphviz package is required to output graphs.")


if __name__ == "__main__":
    main()
