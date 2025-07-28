\# Adobe India Hackathon 2025 - Round 1A Submission



\## Approach for Round 1A



This solution extracts a structured outline from a PDF document.



\* \*\*PDF Parsing\*\*: Uses the `PyMuPDF` library to read text blocks and their font properties (size, style) from the PDF.

\* \*\*Heading Detection\*\*: It identifies headings by analyzing font sizes. It finds the most common font size to determine what is normal body text. Any text with a significantly larger font size is classified as a heading (H1, H2, H3). The document title is assumed to be the text with the largest font size on the first page.

\* \[cite\_start]\*\*Containerization\*\*: The solution is packaged in a Docker container with all dependencies, designed to run completely offline as per the requirements\[cite: 60].



\## Libraries Used

\* PyMuPDF

\* numpy

