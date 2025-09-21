import json
import subprocess
from pathlib import Path


def test_validate_templates_pass(tmp_path):
    # create minimal template.json and layer.json that conform to schema
    tpl = tmp_path / "template.json"
    lyr = tmp_path / "layer.json"
    tpl.write_text(json.dumps({
        "first_principles": {"template": "Do this: {query}", "input_context": "query", "expected_output": "first_principles"}
    }))
    lyr.write_text(json.dumps({
        "layers": [{"name": "layer1", "description": "desc", "nodes": [{"id": "n1", "expected_output": "first_principles"}]}]
    }))

    # copy schemas from repo into tmp dir so the validate script can find them
    repo = Path.cwd()
    schema_src = repo / "schemas"
    schema_dst = tmp_path / "schemas"
    import shutil

    shutil.copytree(schema_src, schema_dst)

    # run validation script in that tmp dir
    import sys
    res = subprocess.run([sys.executable, str(repo / "scripts" / "validate_templates.py")], cwd=tmp_path)
    assert res.returncode == 0
