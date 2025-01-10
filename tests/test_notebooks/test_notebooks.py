import os
from io import StringIO

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

from tests.environment import env
from tests.test_notebooks.environment import nbenv
from tests.utils.filters import nb_filter

FORCE_REWRITE = True
NBBASEDIR = os.path.join(env.cwd, "..", "notebooks")


@pytest.fixture
def ep():
    return ExecutePreprocessor(timeout=600)


def force_rewrite_comparator(expected: str, actual: str) -> str:
    msg = nbenv.string_comparator(expected, actual)
    if not msg and FORCE_REWRITE:
        msg = "Forced rewrite"
    return msg


# @pytest.mark.skip(reason="Skipped until we figure out why this fails in github actions")
@pytest.mark.parametrize(
    "nbname",
    [filename for filename in os.listdir(NBBASEDIR) if not filename.startswith(".") and filename.endswith(".ipynb")],
)
def test_redo_notebook(nbname, ep):
    # The information on how to do this comes from: http://tritemio.github.io/smbits/2016/01/02/execute-notebooks/
    with open(os.path.join(NBBASEDIR, nbname)) as nbf:
        nb = nbformat.read(nbf, as_version=4)
    ep.preprocess(nb, dict(metadata=dict(path=NBBASEDIR)))

    outf = StringIO()
    nbformat.write(nb, outf)

    result = nbenv.eval_single_file(
        os.path.join(NBBASEDIR, nbname),
        outf.getvalue(),
        nb_filter,
        force_rewrite_comparator,
    )
    if result and nbenv.fail_on_error:
        with open(nbenv.temp_file_path(nbname), "w", encoding="utf-8") as actualf:
            actualf.write(outf.getvalue())
