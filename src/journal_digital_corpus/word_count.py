from pathlib import Path
import sys

def count_words_in_txt_files(directory: Path) -> int:
    total_words = 0
    for txt_file in directory.glob("**/*.txt"):
        try:
            with txt_file.open('r', encoding='utf-8') as file:
                content = file.read()
                words = content.split()
                total_words += len(words)
        except Exception as e:
            print(f"Error reading file {txt_file}: {e}")
            sys.exit(1)
    return total_words

if __name__ == '__main__':
    corpus_txt_dir = Path("corpus_txt").resolve()
    if not corpus_txt_dir.is_dir():
        print(f"Error: {corpus_txt_dir} is not a valid directory.")
        sys.exit(1)
    
    word_count = count_words_in_txt_files(corpus_txt_dir)
    print(f"Total words across all .txt files in corpus_txt: {word_count}")
