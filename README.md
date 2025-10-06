# Web Content Extractor and Archiver

This project is a web content extractor and archiver that fetches content from specified URLs from simplenote only, processes it, and saves it as Markdown files organized by date.start the script with the simplenote url in your clipboard and it will fetch the content from the url and save it as a markdown file in the output directory.

## Project Structure

```
web-content-extractor
├── src
│   ├── simex.py          # Main script to orchestrate fetching and processing
│   ├── fetcher.py        # Functions for fetching content from URLs
│   ├── processor.py      # Functions for processing fetched HTML content
│   ├── archiver.py       # Manages saving processed content as Markdown files
│   ├── imp_clip.py       # Functions for updating sources from clipboard
│   └── utils
│       └── __init__.py   # Utility functions shared across modules
├── requirements.txt      # Project dependencies
├── config.yaml           # Configuration settings for sources and paths
├── output                # Directory for saved Markdown files
└── README.md             # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd web-content-extractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Configure the `config.yaml` file to specify the URLs and output filenames.
2. Run the main script:
   ```
   python src/llmix.py
   ```

## Customization

- Modify the `SOURCES` dictionary in `config.yaml` to add or change the URLs you want to fetch content from.
- Adjust the `BASE_PATH` in `config.yaml` to change where the Markdown files are saved.

## Contributing

Feel free to submit issues or pull requests for improvements or additional features.