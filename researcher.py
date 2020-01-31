import string

from nameparser import HumanName

# modified classes taken from initial study

class Researcher:
    def __init__(self, name, id=None, cited_by=None, domain=None,
                 alt_names=None, interests=None, collab_ids=None,
                 publications=None, is_cp=True, scholar_id=None,
                 microsoft_id=None, employment=None):
        self.name = HumanName(name)
        self.name.capitalize()
        self.full_name = name if ',' not in name else self.name.full_name
        self.cited_by = cited_by
        self.alt_names = alt_names if alt_names is not None else set()
        self.alt_names.add(name)
        self.id = id
        self.scholar_id = scholar_id
        self.microsoft_id = microsoft_id
        self.employment = employment
        self.interests = interests if interests is not None else set()
        self.collab_ids = collab_ids if collab_ids is not None else set()
        self.publications = []
        self.publication_titles = set()
        if publications:
            for publication in publications:
                self.add_publication(publication)
        self.is_cp = is_cp

    def __str__(self):
        return ("Researcher:\n" +
                "\tName: {0}\n"+
                "\tId: {1}\n" +
                "\tPublications:\n" +
                "\t[\n\t{2}\n\t]").format(self.name, self.id, "\n\t".join(map(str, self.publications)))

    def add_collab(self, collab_id):
        self.collab_ids.add(collab_id)

    def add_publication(self, publication):
        self.publications.append(publication)
        self.publication_titles.add(Researcher.standardize_title(publication.title))

    def standardize_title(title):
        return ' '.join(title.casefold()
                        .translate(str.maketrans('', '', string.punctuation))
                        .split())

    def fill_with_scholarly(self, scholarly_author):
        if scholarly_author is None:
            return
        self.scholar_id = scholarly_author.id
        self.cited_by = scholarly_author.citedby
        self.alt_names.add(scholarly_author.name)
        for interest in scholarly_author.interests:
            #if not compare_names(interest, scholarly_author.name):
            self.interests.add(interest)
        if not self.is_cp:
            return
        for pub in scholarly_author.publications:
            if (Researcher.standardize_title(pub.bib.get('title')) not in
                self.publication_titles):
                filled = Publication.from_scholarly_pub(pub)
                if filled is not None:
                    self.add_publication(filled)

class Publication:
    def __init__(self, title, id=None, year=None, type=None, cited_by=None,
                 venue=None, microsoft_id=None, authors=None, is_gscholar=False,
                 is_arxiv=False, is_ms=False):
        # self.title = standardize_title(title)
        self.title = title
        self.id = id
        self.year = year
        self.type = type
        self.venue = venue
        self.cited_by = cited_by
        self.is_gscholar = is_gscholar
        self.is_arxiv = is_arxiv
        self.is_ms = is_ms
        self.authors = authors if authors is not None else []

    def __str__(self):
        return ("Publication:\n" +
                "\tTitle: {0}\n" +
                "\tAuthors: {1}").format(self.title, ", ".join(map(lambda x: str(x.name), self.authors)))

    def from_scholarly_pub(scholarly_pub):
        try:
            if not scholarly_pub._filled:
                scholarly_pub.fill()
        except:
            print('Unable to fill scholarly publication')
            return None
        else:
            try:
                publication = Publication(scholarly_pub.bib['title'], is_gscholar=True)
            except KeyError:
                return None
            else:
                publication._fill_with_scholarly(scholarly_pub)
                return publication

    def _fill_with_scholarly(self, scholarly_pub):
        self.scholar_id = scholarly_pub.bib.get('ID')
        self.type = scholarly_pub.bib.get('ENTRYTYPE', None)
        self.venue = scholarly_pub.bib.get('journal', None)
        self.year = scholarly_pub.bib.get('year', None)
        self.cited_by = getattr(scholarly_pub, 'citedby', None)
        self.authors = [Researcher(author_name, is_cp=False)
            for author_name in Publication.get_coauthors(scholarly_pub)]

    def get_coauthors(pub):
        try:
            coauthors = pub.bib['author']
        except KeyError:
            return []
        else:
            return [author_name for author_name in coauthors.split(' and ')
                    if author_name.lower() != 'others']
