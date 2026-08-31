"""PCC 编译器端到端测试。

覆盖：词法分析、语法分析、中间代码生成、汇编生成、gcc 链接运行。
"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pcc.generate import creat_mcode  # noqa: E402
from pcc.lexer import Lexer, Token  # noqa: E402
from pcc.to_asm import to_asm  # noqa: E402

TEST_DIR = Path(__file__).resolve().parent.parent / "test"


# ----------------------------------------------------------------------
# 词法分析
# ----------------------------------------------------------------------
class TestLexer:
    def test_token_count(self):
        wl = Lexer(str(TEST_DIR / "test.c"))
        assert wl.flag is True
        assert len(wl.word_list) == 92

    def test_first_tokens(self):
        wl = Lexer(str(TEST_DIR / "test.c"))
        types = [t.type for t in wl.word_list[:5]]
        assert types == ["type", "name", "(", ")", "{"]

    def test_string_literals(self):
        wl = Lexer(str(TEST_DIR / "fibonacci.c"))
        assert len(wl.string_list) >= 2

    def test_token_is_dataclass(self):
        wl = Lexer(str(TEST_DIR / "test.c"))
        assert isinstance(wl.word_list[0], Token)

    def test_lexer_error_on_unmatched_bracket(self):
        from pcc.lexer import LexError
        bad = TEST_DIR / "_bad_syntax.c"
        bad.write_text("int main(){\n  int a;\n")
        try:
            with pytest.raises(LexError):
                Lexer(str(bad))
        finally:
            bad.unlink(missing_ok=True)


# ----------------------------------------------------------------------
# 中间代码（四元式）
# ----------------------------------------------------------------------
class TestCodegen:
    def test_mid_code_count(self):
        res = creat_mcode(str(TEST_DIR / "test.c"))
        assert len(res["mid_code"]) == 19

    def test_mid_code_assignments(self):
        res = creat_mcode(str(TEST_DIR / "test.c"))
        first = res["mid_code"][0]
        assert str(first) == "(=,0,0,index)"

    def test_while_loop_marks(self):
        res = creat_mcode(str(TEST_DIR / "test.c"))
        ops = [m.op for m in res["mid_code"]]
        assert "code_block" in ops
        assert any("j" in op for op in ops)

    def test_fibonacci_compiles(self):
        res = creat_mcode(str(TEST_DIR / "fibonacci.c"))
        assert len(res["mid_code"]) > 10


# ----------------------------------------------------------------------
# 汇编生成
# ----------------------------------------------------------------------
class TestAsm:
    def test_asm_generated(self, tmp_path):
        src = TEST_DIR / "test.c"
        out = tmp_path / "out.s"
        # 生成到临时目录
        import shutil
        shutil.copy(src, tmp_path / "test.c")
        to_asm(str(tmp_path / "test.c"))
        asm = (tmp_path / "test.s").read_text(encoding="utf-8")
        assert ".text" in asm
        assert "main:" in asm
        assert ".string" in asm
        assert "printf@PLT" in asm

    def test_asm_ident_version(self):
        src = TEST_DIR / "test.c"
        out = src.with_suffix(".s")
        to_asm(str(src))
        asm = out.read_text(encoding="utf-8")
        assert "PCC: 2.0.0" in asm


# ----------------------------------------------------------------------
# 端到端：gcc 链接并运行
# ----------------------------------------------------------------------
@pytest.mark.skipif(
    subprocess.run(["which", "gcc"], capture_output=True).returncode != 0,
    reason="gcc not available",
)
class TestEndToEnd:
    def _build_and_run(self, c_file: Path) -> str:
        to_asm(str(c_file))
        exe = c_file.with_suffix("")
        subprocess.run(["gcc", str(c_file.with_suffix(".s")), "-o", str(exe)], check=True)
        result = subprocess.run([str(exe)], capture_output=True, text=True, check=True)
        return result.stdout

    def test_99mul(self):
        out = self._build_and_run(TEST_DIR / "99mul.c")
        assert "1*1=1" in out
        assert "10*10=100" in out

    def test_fibonacci(self):
        out = self._build_and_run(TEST_DIR / "fibonacci.c")
        assert "f(0)=1" in out
        assert "f(10)=144" in out

    def test_print(self):
        out = self._build_and_run(TEST_DIR / "print.c")
        assert len(out) > 0
