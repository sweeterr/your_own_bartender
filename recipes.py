import re
import logging
import _pickle as pickle
from pathlib import Path
from bs4 import BeautifulSoup


class Recipe:
    def __init__(self, file_path):
        self.file_path = file_path
        self.soup = self.__get_soup()
        self.title = self.__get_title()
        self.ingredients = []
        self.notes = []
        self.instructions = []
        self.amount = ""
        self.__parse_res()

    def __get_soup(self):
        with self.file_path.open(encoding="utf-8") as fin:
            return BeautifulSoup(fin, "lxml")

    def __get_title(self):
        title = self.soup.find("section")["title"]
        if not title:
            logging.warning(f"No title was found in {self.file_path}.")
            title = self.file_path
        return title

    def __get_ingredients(self):
        ingredients = [m.text for m in self.soup.find_all("p", class_=re.compile("^res0?$"))]
        if not ingredients:
            logging.warning(f"No ingredients were found for {self.title} in {self.file_path}.")
        return ingredients

    def __get_note(self):
        note = ""
        try:
            note = self.soup.find_all("p", class_=re.compile("res-txt"))[0].text
        except IndexError:
            logging.warning(f"No ingredients were found for {self.title} in {self.file_path}.")
        return note

    def __get_instructions(self):
        instructions = ""
        try:
            instructions = self.soup.find_all("p", class_=re.compile("res-txt1$"))[0].text
        except IndexError:
            logging.warning(f"No instructions were found for {self.title} in {self.file_path}.")
        return instructions

    def __get_amount(self):
        try:
            amount = self.soup.find_all("p", class_=re.compile("res-txt1?b"))[0].text
        except IndexError:
            amount = ""
            logging.warning(f"No amount was found for {self.title} in {self.file_path}.")
        return amount

    def as_dict(self):
        d = {}
        for attr, value in self.__dict__.items():
            if attr == "soup":
                continue
            else:
                d[attr] = str(value)
        return d

    def __parse_res(self):
        matches = self.soup.find_all("p", class_=re.compile("^res"))
        for m in matches:
            if m["class"][0] in ["res", "res0"]:
                self.ingredients.append(m.text)
            elif m["class"][0] in ["res-txtb", "res-txt1b"]:
                self.amount = m.text
            elif m["class"][0] in ["res-txt", "res-txt1"]:
                if self.ingredients:
                    self.instructions.append(m.text)
                else:
                    self.notes.append(m.text)

        if not self.notes:
            logging.warning(f"No notes were found for {self.title} in {self.file_path}.")
        if not self.amount:
            logging.warning(f"No amount was found for {self.title} in {self.file_path}.")
        if not self.ingredients:
            logging.warning(f"No ingredients were found for {self.title} in {self.file_path}.")
        if not self.instructions:
            logging.warning(f"No instructions were found for {self.title} in {self.file_path}.")


def get_recipes():
    cocktails = {}
    recipe_dir = Path("book", "OEBPS", "xhtml")
    recipe_files = recipe_dir.glob(pattern="Recipe*[!a].xhtml")
    with open("cocktails.json", "w", encoding="utf-8") as fout:
        for recipe_file in recipe_files:
            r = Recipe(recipe_file)
            cocktails[r.title] = r
            fout.write(f"{r.as_dict()}\n")
    with open("cocktails.pickle", "wb") as fout:
        fout.write(pickle.dumps(cocktails))


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    get_recipes()


if __name__ == "__main__":
    main()
