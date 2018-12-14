# Twine Graph

Twine Graph is a Python package and command line tool for parsing passage and link structure
from published .html Twine stories and outputting the resulting graphs in visual (.pdf) or
structured (.json) formats. The goal of Twine Graph is to allow for research and analysis of
story structure in freely-available Twine games.

### Prerequisites

Twine Graph requires Python 3 and the `beautifulsoup4` and `graphviz` packages. Tested primarily
on Mac OS X within an Anaconda environment.

### Installation

The easiest way to install Twine Graph is through `pip`:

```
pip install twine-graph
```

### Example usage

The installed package can be called from the command line through its entry-point, as in the 
following sample call (using the example .html file included in the github project):

```
twine_graph twine_graph_example.html
```

The output .gv.pdf file can be opened for a visual representation of the passage and link structure
of the story, while the output .json file provides a structured representation:

```
{
  "passages": [
    {
      "pid": 1,
      "name": "Hello",
      "text": "[[Hello->World]]",
      "links": [
        {
          "text": "Hello",
          "destination": {
            "name": "World",
            "pid": 2
          }
        }
      ]
    },
    {
      "pid": 2,
      "name": "World",
      "text": "Hello World",
      "links": []
    }
  ]
}
```

### Known Issues

- Doesn't detect links produced by custom javascript
- Doesn't detect links referenced through variables (i.e. variable tracking not supported)

### Related Work

- [twine-parser](https://github.com/unwitting/twine-parser): A Javascript utility for parsing 
twine stories into graph objects.
- [TwineJson](https://github.com/cauli/TwineJson): A utility for Twine that exports a story
into JSON format.

### Author

**Enrique Henestroza Anguiano** 

### License

This project is licensed under the GNU GPL License - see [LICENSE](LICENSE) for details
