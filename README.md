# Book Recommendation System

## Overview

This Book Recommendation System is a Python implementation of a weighted graph-based approach to provide book recommendations to users. The system utilizes a dataset of book reviews and book names to calculate similarity scores between books and offer recommendations based on user preferences.

## Features

- **Weighted Graph**: The system uses a weighted graph data structure to represent the book review network. Each book and user is represented as a vertex in the graph, and the edges between them are weighted based on review scores.

- **Similarity Scores**: The system calculates two types of similarity scores between books: unweighted and strict weighted. These scores help determine the similarity between two books, taking into account the reviews they share.

- **Recommendations**: Users can request book recommendations based on their preferences. The system provides a list of recommended books, sorted by similarity score. Users can specify the number of recommendations they want to receive.

## Getting Started

1. **Installation**: Clone this repository to your local machine.

   ```bash
   git clone https://github.com/Aviral-03/Recommendation-system.git

Before you get started, make sure you have the following dependencies installed:

- Python (>=3.11)

You can install the required Python packages using pip with the following command:

```bash
pip install -r requirements.txt
