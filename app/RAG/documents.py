import os

from langchain_core.documents import (
    Document
)

def load_all_documents():

    all_docs = []

    folder = "data/raw"

    for file in os.listdir(folder):

        path = os.path.join(folder, file)

        if file.endswith(".txt"):

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                text = f.read()

                doc = Document(
                    page_content=text,
                    metadata={
                        "source": file
                    }
                )

                all_docs.append(doc)

    return all_docs