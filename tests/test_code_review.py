import unittest
import sys
import tempfile
import shutil
import json
from pathlib import Path
from typer.testing import CliRunner

WORKSPACE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from asdlc.review.engine import DeterministicCodeReviewer
from asdlc.review.models import Severity, IssueCategory
from asdlc.orchestrator import SDLCOrchestrator
from asdlc.models import ReviewVerdict
from asdlc.cli.main import app

class TestDeterministicCodeReview(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.reviewer = DeterministicCodeReviewer()
        self.orch = SDLCOrchestrator(project_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_python_deterministic_review(self):
        # 1. 脆弱性を含む Python コード (DUMMY_SECRET_TEST)
        mock_raw_key = "abcdef" + "1234567890abcdef1234567890"
        vulnerable_py = (
            "import os, subprocess, pickle\n"
            f"{'api_' + 'key'} = '{mock_raw_key}'\n"


            "def run_job(cmd, user_input):\n"
            "    eval(user_input)\n"
            "    subprocess.run(cmd, shell=True)\n"
            "    pickle.loads(user_input)\n"
            "    try:\n"
            "        data = os.system('ls ' + user_input)\n"
            "    except:\n"
            "        pass\n"
        )
        report = self.reviewer.review("test_vuln.py", content=vulnerable_py, lang="python")
        self.assertTrue(report.has_errors)
        self.assertTrue(report.is_short_circuited)
        
        rule_ids = [i.rule_id for i in report.issues]
        self.assertIn("SEC-001-HARDCODED-SECRET", rule_ids)
        self.assertIn("PY-SEC-DANGEROUS-EVAL", rule_ids)
        self.assertIn("PY-SEC-SUBPROCESS-SHELL-TRUE", rule_ids)
        self.assertIn("PY-SEC-INSECURE-DESERIALIZATION", rule_ids)
        self.assertIn("PY-SEC-COMMAND-INJECTION", rule_ids)
        self.assertIn("PY-ROB-BARE-EXCEPT-PASS", rule_ids)

        # 2. 正常な Python コード
        clean_py = (
            "import logging\n"
            "from typing import Optional\n"
            "logger = logging.getLogger(__name__)\n\n"
            "def calculate_total(price: float, tax_rate: float) -> float:\n"
            "    if price < 0:\n"
            "        raise ValueError('Price cannot be negative')\n"
            "    return price * (1.0 + tax_rate)\n"
        )
        clean_report = self.reviewer.review("clean.py", content=clean_py, lang="python")
        self.assertFalse(clean_report.has_errors)
        self.assertEqual(len(clean_report.issues), 0)

    def test_02_typescript_deterministic_review(self):
        vulnerable_ts = (
            "const secret = 'auth_token: 12345678901234567890';\n"
            "export function execute(queryStr: any) {\n"
            "    eval('alert(1)');\n"
            "    // @ts-ignore\n"
            "    const sql = `SELECT * FROM users WHERE id = ${queryStr}`;\n"
            "    try {\n"
            "        console.log(sql);\n"
            "    } catch (e) {}\n"
            "}\n"
        )
        report = self.reviewer.review("vuln.ts", content=vulnerable_ts, lang="typescript")
        self.assertTrue(report.has_errors)
        rule_ids = [i.rule_id for i in report.issues]
        self.assertIn("TS-SEC-DANGEROUS-EVAL", rule_ids)
        self.assertIn("TS-ROB-EMPTY-CATCH", rule_ids)
        self.assertIn("TS-SEC-SQL-INJECTION", rule_ids)
        self.assertIn("TS-GOV-TS-IGNORE", rule_ids)
        self.assertIn("TS-ROB-ANY-TYPE", rule_ids)

    def test_03_go_deterministic_review(self):
        vulnerable_go = (
            "package main\n"
            "import (\n"
            "    \"fmt\"\n"
            "    \"unsafe\"\n"
            ")\n"
            "func Handler(query string) {\n"
            "    _ = err\n"
            "    sql := fmt.Sprintf(\"SELECT * FROM users WHERE name = '%s'\", query)\n"
            "    ptr := unsafe.Pointer(&query)\n"
            "    panic(\"fatal crash\")\n"
            "}\n"
        )
        report = self.reviewer.review("main.go", content=vulnerable_go, lang="go")
        self.assertTrue(report.has_errors)
        rule_ids = [i.rule_id for i in report.issues]
        self.assertIn("GO-ROB-UNCHECKED-ERROR", rule_ids)
        self.assertIn("GO-SEC-SQL-INJECTION", rule_ids)
        self.assertIn("GO-SEC-UNSAFE-POINTER", rule_ids)
        self.assertIn("GO-ROB-PANIC-USAGE", rule_ids)

    def test_04_c_and_cpp_deterministic_review(self):
        # C
        vulnerable_c = (
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "void test() {\n"
            "    char buf[64];\n"
            "    gets(buf);\n"
            "    strcpy(buf, \"large_string\");\n"
            "    sprintf(buf, \"%s\", \"overflow\");\n"
            "    system(\"rm -rf /tmp\");\n"
            "}\n"
        )
        report_c = self.reviewer.review("main.c", content=vulnerable_c, lang="c")
        self.assertTrue(report_c.has_errors)
        c_rules = [i.rule_id for i in report_c.issues]
        self.assertIn("C-SEC-BANNED-GETS", c_rules)
        self.assertIn("C-SEC-UNBOUNDED-STRCPY", c_rules)
        self.assertIn("C-SEC-UNBOUNDED-SPRINTF", c_rules)
        self.assertIn("C-SEC-COMMAND-EXEC-SYSTEM", c_rules)

        # C++
        vulnerable_cpp = (
            "#include <iostream>\n"
            "void process() {\n"
            "    int* p = new int(10);\n"
            "    try {\n"
            "        delete p;\n"
            "    } catch (...) {}\n"
            "}\n"
        )
        report_cpp = self.reviewer.review("main.cpp", content=vulnerable_cpp, lang="cpp")
        self.assertTrue(report_cpp.has_errors)
        cpp_rules = [i.rule_id for i in report_cpp.issues]
        self.assertIn("CPP-ROB-EMPTY-CATCH-ALL", cpp_rules)
        self.assertIn("CPP-ROB-RAW-NEW-DELETE", cpp_rules)

    def test_05_csharp_deterministic_review(self):
        vulnerable_cs = (
            "using System;\n"
            "using System.Runtime.Serialization.Formatters.Binary;\n"
            "class Program {\n"
            "    void Run(string input) {\n"
            "        var bf = new BinaryFormatter();\n"
            "        try {\n"
            "            SqlCommand cmd = new SqlCommand($\"SELECT * FROM Users WHERE Name = '{input}'\");\n"
            "        } catch (Exception) {}\n"
            "    }\n"
            "}\n"
        )
        report_cs = self.reviewer.review("Program.cs", content=vulnerable_cs, lang="csharp")
        self.assertTrue(report_cs.has_errors)
        cs_rules = [i.rule_id for i in report_cs.issues]
        self.assertIn("CS-SEC-INSECURE-DESERIALIZATION", cs_rules)
        self.assertIn("CS-ROB-EMPTY-CATCH", cs_rules)
        self.assertIn("CS-SEC-SQL-INJECTION", cs_rules)

    def test_06_short_circuiting_and_orchestrator(self):
        # 1. 脆弱なコードを成果物として登録
        vuln_file = Path(self.test_dir) / "auth_service.py"
        vuln_file.write_text("def login(pwd):\n    eval(pwd)\n", encoding="utf-8")

        # 2. オーケストレーターでレビュー実行 -> Short-Circuit FAIL
        eval_res = self.orch.review_artifact("auth_service.py")
        self.assertEqual(eval_res.verdict, ReviewVerdict.FAIL)
        self.assertTrue(eval_res.remediation_required)
        self.assertIn("Short-Circuit FAIL", eval_res.summary)
        self.assertLess(eval_res.total_score, 60.0)

        # 3. 健全なコードを成果物として登録
        clean_file = Path(self.test_dir) / "math_util.py"
        clean_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")

        eval_clean = self.orch.review_artifact("math_util.py")
        self.assertEqual(eval_clean.verdict, ReviewVerdict.PASS)
        self.assertGreaterEqual(eval_clean.total_score, 80.0)

    def test_07_sarif_generation(self):
        code = "def f():\n    eval('1+1')\n"
        report = self.reviewer.review("test.py", content=code, lang="python")
        sarif = report.to_sarif_dict()
        
        self.assertEqual(sarif["version"], "2.1.0")
        self.assertIn("runs", sarif)
        self.assertEqual(len(sarif["runs"]), 1)
        results = sarif["runs"][0]["results"]
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["ruleId"], "PY-SEC-DANGEROUS-EVAL")
        self.assertEqual(results[0]["level"], "error")

    def test_08_cli_review_code_and_sarif(self):
        sample_path = Path(self.test_dir) / "sample_test.py"
        sample_path.write_text("def add(x: int, y: int) -> int:\n    return x + y\n", encoding="utf-8")

        runner = CliRunner()
        # 決定論的のみ
        res_d = runner.invoke(app, ["review", str(sample_path), "-d"])
        self.assertEqual(res_d.exit_code, 0)
        self.assertIn("Stage 1 決定論的静的解析ゲート", res_d.output)

        # SARIF 出力
        res_sarif = runner.invoke(app, ["review", str(sample_path), "--sarif"])
        self.assertEqual(res_sarif.exit_code, 0)
        sarif_data = json.loads(res_sarif.output)
        self.assertEqual(sarif_data["version"], "2.1.0")

if __name__ == "__main__":
    unittest.main()
