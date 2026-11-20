import contextlib
import io
import re
import unittest

import duckdb

from discoball.const import ROOT_DIR


class TabularSideQuestTests(unittest.TestCase):
    def test_polars_documentation_examples(self):
        for name in ["expressions", "types_nulls", "joins"]:
            path = ROOT_DIR / "src/discoball/lesson_6" / f"{name}.md"
            namespace = {}
            with self.subTest(quest=name), contextlib.redirect_stdout(io.StringIO()):
                for snippet in re.findall(
                    r"```python\n(.*?)\n```", path.read_text(), re.DOTALL
                ):
                    # Execute only trusted, repository-owned lesson snippets.
                    exec(compile(snippet, str(path), "exec"), namespace)  # noqa: S102
            if name == "expressions":
                self.assertEqual(namespace["selected"].height, 2)
            elif name == "types_nulls":
                self.assertEqual(namespace["parsed"]["count"].null_count(), 3)
            else:
                self.assertEqual(namespace["joined"].height, 3)

    def test_sql_documentation_examples(self):
        quests = {
            "lesson_2/joins_side_quest.md": [3, 1, 1],
            "lesson_3/denominators_side_quest.md": [1, 1, 1],
        }
        with duckdb.connect() as connection:
            for name, expected_rows in quests.items():
                path = ROOT_DIR / "src/discoball" / name
                snippets = re.findall(
                    r"```sql\n(.*?)\n```", path.read_text(), re.DOTALL
                )
                self.assertEqual(len(snippets), len(expected_rows))
                for snippet, expected in zip(snippets, expected_rows, strict=True):
                    with self.subTest(quest=name, query=snippet):
                        rows = connection.execute(snippet).fetchall()
                        self.assertEqual(len(rows), expected)
                if name.startswith("lesson_3"):
                    self.assertEqual(rows, [(0, None, None)])


if __name__ == "__main__":
    unittest.main()
