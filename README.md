# Modern PDF processing with Natural PDF

**Dataharvest 2026**

Jonathan Soma, Columbia University

Learn to extract data from PDFs with the spatial magic of Natural PDF. Basic text extraction to OCR, AI, and complex layouts — everything you need to get structured data out of any PDF.

**[View the workshop materials](https://jsoma.github.io/natural-pdf-workshop/)**

[Open in Codespaces](https://codespaces.new/jsoma/natural-pdf-workshop?ref=main)

## Materials

### Natural PDF

#### Natural PDF basics with text and tables

Natural PDF is a spatially-aware PDF processing library that makes accessing PDF data a breeze.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/01-natural-pdf-basics-with-text-and-tables-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/01-natural-pdf-basics-with-text-and-tables.ipynb) | [Codespaces](https://codespaces.new/jsoma/natural-pdf-workshop?ref=main) | [Download .ipynb](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/01-natural-pdf-basics-with-text-and-tables-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/01-natural-pdf-basics-with-text-and-tables-ANSWERS.html)

- [Natural PDF documentation](https://jsoma.github.io/natural-pdf/)

#### Recognizing text with OCR engines using Natural PDF

Some PDFs are just images of text instead of being actual text. This is when you need OCR (optical character recognition).

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/02-ocr-and-ai-magic-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/02-ocr-and-ai-magic.ipynb) | [Codespaces](https://codespaces.new/jsoma/natural-pdf-workshop?ref=main) | [Download .ipynb](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/02-ocr-and-ai-magic-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/02-ocr-and-ai-magic-ANSWERS.html)

- [GLM OCR](https://huggingface.co/zai-org/GLM-OCR)
- [RapidOCR](https://github.com/rapidai/rapidocr)
- [PaddleOCR](https://www.paddleocr.ai/latest/en/index.html)

#### AI and data extraction

AI is a great (albeit flawed) method for extracting specific data from your PDFs.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/03-ai-and-data-extraction-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/03-ai-and-data-extraction.ipynb) | [Codespaces](https://codespaces.new/jsoma/natural-pdf-workshop?ref=main) | [Download .ipynb](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/03-ai-and-data-extraction-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/03-ai-and-data-extraction-ANSWERS.html)

- [OpenAI structured outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)

#### Columns, multi-page flows and other page structures

A one-page PDF with a single block of text is easy mode. Things get more complicated when you have actual layouts.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/04-page-structure-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/04-page-structure.ipynb) | [Codespaces](https://codespaces.new/jsoma/natural-pdf-workshop?ref=main) | [Download .ipynb](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/04-page-structure-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/04-page-structure-ANSWERS.html)

- [Microsoft's table transfer (TATR)](https://github.com/microsoft/table-transformer)
- [YOLO document layout](https://github.com/opendatalab/DocLayout-YOLO/)
- [LayoutLMv3](https://huggingface.co/docs/transformers/en/model_doc/layoutlmv3)
- [merveenoyan/smol-vision](https://github.com/merveenoyan/smol-vision)

#### Putting it all together

Let's see what it looks like to put this all together in a real-life scenario.

Try: [Open in Colab](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/05-final-boss-ANSWERS.ipynb) | [Colab (code-along)](https://colab.research.google.com/github/jsoma/natural-pdf-workshop/blob/main/docs/natural-pdf/05-final-boss.ipynb) | [Codespaces](https://codespaces.new/jsoma/natural-pdf-workshop?ref=main) | [Download .ipynb](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/05-final-boss-ANSWERS.ipynb) | [Read online](https://jsoma.github.io/natural-pdf-workshop/natural-pdf/05-final-boss-ANSWERS.html)

## Contact

[js4571@columbia.edu](mailto:js4571@columbia.edu) · [@dangerscarf](https://x.com/dangerscarf) · [Lede Program](https://ledeprogram.com/) · [jonathansoma.com](https://jonathansoma.com/) · [Bad PDFs](https://badpdfs.com/)
