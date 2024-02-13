# Processor

This folder contais all background processing codes.

generate_features.py - Used as the one-time processor to generate the feature mappings for a list of books. Given book title and descriptions in the form of csv file (books.csv), it writes the feature mappings of the given books into mapped_books.csv.

Run below command to generate the feature mappings:

python .\generate_features.py

After generating the feature mappings. Copy paste the mapped_books.csv file contents to updated_books.csv in the project home folder.