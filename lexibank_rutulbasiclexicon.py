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
    id = "rutulbasiclexicon"
    #language_class = CustomLanguage
    form_spec = FormSpec(separators="~;,/", missing_data=["∅"], first_form_only=True)

    def cmd_makecldf(self, args):
        # add bib
        args.writer.add_sources()
        args.log.info("added sources")

        # load data
        data = self.raw_dir.read_csv(
                "rutul_basic_lexicon_lexibank-3.tsv", delimiter="\t", dicts=True)

        # retrieve concepts
        concepts = {}
        for concept in self.concepts:
            idx = concept["NUMBER"] + "_" + slug(concept["ENGLISH"])
            args.writer.add_concept(
                    ID=idx,
                    Name=concept["ENGLISH"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"]
                    )
            concepts[concept["ENGLISH"]] = idx
        languages = {}
        for language in self.languages:
            idx = language["village"].replace(" ", "-")
            glot = ""
            if language["gltc_dialect"] != "NA":
                glot = language["gltc_dialect"]
            elif language["gltc_lang"] != "NA":
                glot = language["gltc_lang"]
            args.writer.add_language(
                    ID=idx,
                    Name=language["village"],
                    Latitude=language["lat"].replace(",", "."),
                    Longitude=language["lon"].replace(",", "."),
                    Glottocode=glot
                    )

        idx = 1
        for i, row in pb(enumerate(data)):
            concept = row["feature_title"].split("‘")[1][:-1]

            language = row["settlement"]
            if row['answer'] != '—':
                args.writer.add_form_with_segments(
                        Parameter_ID=concepts[concept],
                        Language_ID=language,
                        Value=row["value"],
                        Form=row["answer"],
                        Segments=row["answer_lexibank"].strip().split(),
                        Source="rutul"
                        )

