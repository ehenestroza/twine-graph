import argparse
import os.path as op
from .twine_graph import TwineGraph


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

    story = TwineGraph(
        file_root,
        in_format=file_ext[1:],
        encoding=args.encoding
    )

    if file_ext != ".json":
        story.save_json(file_root)
    if not args.nograph:
        passage_labels = True if args.labels in ["passages", "both"] else False
        link_labels = True if args.labels in ["links", "both"] else False
        story.save_graph(file_root, out_format=args.graph_format, title=args.title,
                         passage_labels=passage_labels, link_labels=link_labels,
                         remove_singletons=args.remove_singletons, char_limit=args.char_limit)


if __name__ == "__main__":
    main()
