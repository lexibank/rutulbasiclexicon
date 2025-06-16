import pathlib
import attr
from clldutils.misc import slug
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar as pb
from pylexibank import Language
from pylexibank import FormSpec


@attr.s
class CustomLanguage(Language):
    Location = attr.ib(default=None)
    Remark = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "rutulbl"
    #language_class = CustomLanguage
    form_spec = FormSpec(separators="~;,/", missing_data=["∅"], first_form_only=True)

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # load data
        data = self.raw_dir.read_csv(
                "rutul_basic_lexicon_lexibank.tsv", delimiter="\t", dicts=True)

        # retrieve concepts
        concepts = {}
        languages = {}
        idx = 1
        for i, row in pb(enumerate(data)):
            concept = row["feature_title"].split("‘")[1][:-1]
            print(concept)
            if concept not in concepts:
                cid = f"{idx}_{slug(concept)}"
                concepts[concept] = cid
                args.writer.add_concept(
                        ID=cid,
                        Name=concept
                        )
                idx += 1
            language = row["settlement"]
            if language not in languages:
                languages[language] = slug(language, lowercase=False)
                args.writer.add_language(
                        ID=languages[language],
                        Name=language
                        )
            if row['answer'] != '—':
                args.writer.add_form_with_segments(
                        Parameter_ID=concepts[concept],
                        Language_ID=languages[language],
                        Value=row["value"],
                        Form=row["answer"],
                        Segments=row["answer_lexibank"].strip().split()
                        )

