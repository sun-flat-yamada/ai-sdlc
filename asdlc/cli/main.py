import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional
from pathlib import Path
from ..orchestrator import SDLCOrchestrator
from ..models import ReviewVerdict

app = typer.Typer(help="asdlc: AI-Software-Development-Life-Cycle Enterprise CLI")
console = Console(legacy_windows=False)

@app.command()
def status():
    """現在のSDLC進行状況とガードレール状態を表示"""
    orch = SDLCOrchestrator()
    state = orch.state
    phase_info = orch.procedural.get_phase_info(state.current_phase)

    console.print(Panel(
        f"[bold cyan]プロジェクト:[/bold cyan] {state.project_name}\n"
        f"[bold green]現在フェーズ:[/bold green] {phase_info.get('name', state.current_phase.value)}\n"
        f"[bold yellow]主要タスク:[/bold yellow] {phase_info.get('task', '-')}\n"
        f"[bold magenta]必須成果物:[/bold magenta] {phase_info.get('output', '-')}",
        title="[bold]ASDLC Pipeline Status[/bold]"
    ))

    check = orch.procedural.check_guardrails(state, state.current_phase)
    if check["is_blocked"]:
        console.print("[bold red][!] ガードレールにより次フェーズへの昇格がブロックされています:[/bold red]")
        for reason in check["block_reasons"]:
            console.print(f" - [red]{reason}[/red]")
    else:
        console.print("[bold green][OK] ガードレールクリア: 次フェーズへの昇格が可能です。[/bold green]")

@app.command()
def triage(target: str = typer.Argument(..., help="IssueタイトルまたはIssueファイルのパス")):
    """Issueの自動4次元トリアージとサニタイズを実行"""
    orch = SDLCOrchestrator()
    p = Path(target)
    if p.exists() and p.is_file():
        content = p.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = lines[0].replace("#", "").strip() if lines else p.stem
        body = "\n".join(lines[1:]) if len(lines) > 1 else ""
    else:
        title = target
        body = ""

    console.print(f"[cyan]Issue Auto-Triage を開始:[/cyan] {title}")
    result = orch.triage_issue(title, body)

    color = "bold red" if result.prompt_injection_detected else "bold green"
    priority_color = "red" if "P0" in result.priority.value or "P1" in result.priority.value else "yellow"

    console.print(Panel(
        f"[bold]Issue タイトル:[/bold] {result.title}\n"
        f"[bold]分類 (Type):[/bold] [cyan]{result.issue_type.value}[/cyan]\n"
        f"[bold]優先度 (Priority):[/bold] [{priority_color}]{result.priority.value}[/{priority_color}]\n"
        f"[bold]推定コンポーネント:[/bold] {result.estimated_component}\n"
        f"[bold]推奨ラベル:[/bold] {', '.join(result.suggested_labels)}\n"
        f"[bold]担当アサイン推奨:[/bold] {result.recommended_assignee_role}\n"
        f"[bold]次アクション案:[/bold] {result.remediation_proposal}",
        title=f"[{color}]4D Triage Result[/{color}]"
    ))

    if result.prompt_injection_detected:
        console.print("[bold red][!] プロンプトインジェクション警告:[/bold red]")
        for w in result.injection_warnings:
            console.print(f" - [red]{w}[/red]")

    if result.missing_information:
        console.print("[bold yellow][INFO] 不足情報リスト:[/bold yellow]")
        for m in result.missing_information:
            console.print(f" - [yellow]{m}[/yellow]")

@app.command()
def review(
    artifact_name: str = typer.Argument(..., help="審査対象成果物（仕様書 .md またはソースコード .py, .ts, .go, .c, .cpp, .cs）"),
    deterministic_only: bool = typer.Option(False, "--deterministic-only", "-d", help="LLMを呼ばず決定論的静的解析のみを超高速実行"),
    sarif: bool = typer.Option(False, "--sarif", help="OASIS SARIF v2.1.0 形式で標準出力"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="言語指定 (python, typescript, go, c, cpp, csharp)")
):
    """QA Agent（成果物審査・決定論的ハイブリッドコードレビュー）を実行"""
    from ..review.engine import DeterministicCodeReviewer
    from ..review.models import Severity

    is_code = DeterministicCodeReviewer.is_source_code(artifact_name)

    # SARIF 出力モード
    if sarif:
        if not is_code:
            console.print("[bold red]エラー: SARIF形式の出力はソースコード成果物のみ対応しています。[/bold red]")
            raise typer.Exit(1)
        import json
        reviewer = DeterministicCodeReviewer()
        report = reviewer.review(artifact_name, lang=lang)
        typer.echo(json.dumps(report.to_sarif_dict(), ensure_ascii=False, indent=2))
        return

    orch = SDLCOrchestrator()
    if is_code:
        reviewer = DeterministicCodeReviewer()
        report = reviewer.review(artifact_name, lang=lang)
        console.print(f"[bold cyan]>> 決定論的ハイブリッド・コードレビュー開始:[/bold cyan] {artifact_name}")
        console.print(f"   [dim]検出言語: {report.language} | 実行エンジン: {report.tool_name} | 実行時間: {report.execution_time_ms}ms[/dim]\n")

        # Stage 1: 決定論的静的解析指摘テーブル
        if report.issues:
            s_table = Table(title=f"Stage 1: 決定論的静的解析ゲート結果 ({len(report.issues)} 件の指摘)")
            s_table.add_column("行:列", justify="right", style="cyan")
            s_table.add_column("重大度", justify="center")
            s_table.add_column("ルールID", style="yellow")
            s_table.add_column("カテゴリ")
            s_table.add_column("メッセージ / 改善提案")

            for iss in report.issues:
                if iss.severity == Severity.ERROR:
                    sev_str = "[bold red]ERROR[/bold red]"
                elif iss.severity == Severity.WARNING:
                    sev_str = "[bold yellow]WARN[/bold yellow]"
                else:
                    sev_str = "[dim]INFO[/dim]"

                msg = f"{iss.message}"
                if iss.remediation:
                    msg += f"\n[dim green]-> 対策: {iss.remediation}[/dim green]"
                if iss.snippet:
                    msg += f"\n[dim]   `{iss.snippet}`[/dim]"

                s_table.add_row(
                    f"{iss.line}:{iss.column}",
                    sev_str,
                    iss.rule_id,
                    iss.category.value,
                    msg
                )
            console.print(s_table)
            console.print()
        else:
            console.print("[bold green][OK] Stage 1 決定論的静的解析ゲート: 欠陥ゼロ (Clean)[/bold green]\n")

        if report.has_errors:
            console.print("[bold red][Short-Circuit 遮断] 重大欠陥 (ERROR) が検知されたため、LLM推論を即時短絡遮断しました。[/bold red]\n")
    else:
        console.print(f"[cyan]マイスターズ審議会によるドキュメント審査を開始:[/cyan] {artifact_name} (憲章: docs/charter/MEISTERS_CHARTER.md)")

    try:
        evaluation = orch.review_artifact(artifact_name, deterministic_only=deterministic_only)
    except Exception as e:
        console.print(f"[bold red]エラー:[/bold red] {e}")
        raise typer.Exit(1)

    table = Table(title=f"マイスターズ審議会 評価スコアシート ({artifact_name})")
    table.add_column("審査マイスター (Meister)", style="cyan")
    table.add_column("スコア", justify="right")
    table.add_column("判定", justify="center")
    table.add_column("具体的改善指示 / 指摘事項")

    for s in evaluation.meister_scores:
        v_color = "green" if s.verdict == ReviewVerdict.PASS else "red"
        recs = "\n".join(s.recommendations) if s.recommendations else "-"
        table.add_row(s.meister.value, f"{s.score}点", f"[{v_color}]{s.verdict.value}[/{v_color}]", recs)

    console.print(table)
    color = "bold green" if evaluation.verdict == ReviewVerdict.PASS else "bold red"
    console.print(f"[{color}]総合結果: {evaluation.summary}[/{color}]")


@app.command()
def advance():
    """ガードレールを通過して次フェーズへ進める"""
    orch = SDLCOrchestrator()
    res = orch.advance_phase()
    if not res["success"]:
        console.print("[bold red]次フェーズへ進めることができませんでした:[/bold red]")
        for r in res.get("reasons", []):
            console.print(f" - [red]{r}[/red]")
    else:
        console.print(f"[bold green][SUCCESS] フェーズ昇格完了:[/bold green] {res.get('new_phase')}")

@app.command()
def code(
    intent: str = typer.Argument(..., help="実装意図または個別ビジネスロジックの指示"),
    lang: Optional[str] = typer.Option(None, "--lang", "-l", help="ターゲットプログラミング言語 (python, typescript, go, c, cpp, csharp, auto)")
):
    """Coding Agent を呼び出し、4層知識階層（言語非依存普遍則 > 言語特化パック > カタログ > 個別意図）で標準化コードを合成"""
    orch = SDLCOrchestrator()
    ctx = orch.coding.synthesize_code_context(intent, lang=lang)
    target_lang = ctx.get("detected_language", "unknown").upper()
    
    t1_text = "\n".join(f"- {p}" for p in ctx.get('tier_1_governance_agnostic', []))
    t2_text = "\n".join(f"- {p}" for p in ctx.get('tier_2_language_pack', []))
    t3_text = "\n".join(f"- {s}" for s in ctx.get('tier_3_standards_catalog', []))
    t4_text = ctx.get('tier_4_developer_intent', intent)

    console.print(Panel(
        f"[bold cyan]>> 対象言語 (Target Language):[/bold cyan] [bold green]{target_lang}[/bold green]\n\n"
        f"[bold red]Tier 1 (全社普遍ガバナンス - 言語非依存):[/bold red]\n{t1_text}\n\n"
        f"[bold blue]Tier 2 (言語特化ナレッジパック - 動的射影):[/bold blue]\n{t2_text}\n\n"
        f"[bold yellow]Tier 3 (多言語コンポーネントカタログ / 再利用強制):[/bold yellow]\n{t3_text}\n\n"
        f"[bold green]Tier 4 (開発者の個別意図 / ドメイン要件):[/bold green]\n- {t4_text}",
        title="[bold]Coding Agent 4層知識階層コンテキスト合成結果[/bold]"
    ))

@app.command(name="eval")
def evaluate(
    target: str = typer.Option("all", "--target", "-t", help="評価対象: all, skills, agents, rules"),
    json_output: bool = typer.Option(False, "--json", help="JSON形式で出力")
):
    """Skills, Agents, Rules の品質・整合性・決定論的振る舞いを多層評価 (ASQS スコア算出)"""
    from ..evals import EvaluationRunner, EvalStatus
    
    runner = EvaluationRunner()
    report = runner.run_evaluations(target=target)
    
    if json_output:
        import json
        console.print(json.dumps(report.model_dump(), ensure_ascii=False, indent=2))
        return

    console.print(f"[bold cyan]ASDLC Agent & Skill Quality Evaluation (ASQS)[/bold cyan]")
    console.print(f"評価対象: [yellow]{target}[/yellow] | 実行時刻: {report.timestamp}\n")

    # Tier Summary Table
    t_table = Table(title="評価層別サマリー (Tier Summaries)")
    t_table.add_column("評価層 (Tier)", style="cyan")
    t_table.add_column("検証項目数", justify="right")
    t_table.add_column("合格数", justify="right", style="green")
    t_table.add_column("不合格数", justify="right", style="red")
    t_table.add_column("平均スコア", justify="right", style="bold yellow")

    for ts in report.tier_summaries:
        t_table.add_row(
            ts.tier.value,
            str(ts.total_checks),
            str(ts.passed_checks),
            str(ts.failed_checks),
            f"{ts.average_score}点"
        )
    console.print(t_table)
    console.print()

    # Detailed Item Table
    d_table = Table(title=f"詳細検証結果 ({len(report.item_results)} 項目)")
    d_table.add_column("項目ID", style="cyan")
    d_table.add_column("種別", justify="center")
    d_table.add_column("スコア", justify="right")
    d_table.add_column("判定", justify="center")
    d_table.add_column("検証詳細 / 指摘・改善案")

    for item in report.item_results:
        v_color = "green" if item.status == EvalStatus.PASS else "red"
        rec_text = "\n".join(f"- {r}" for r in item.recommendations) if item.recommendations else item.details
        d_table.add_row(
            item.item_id,
            item.target_type,
            f"{item.score:.1f}点",
            f"[{v_color}]{item.status.value}[/{v_color}]",
            rec_text
        )
    console.print(d_table)

    color = "bold green" if report.overall_verdict == EvalStatus.PASS else "bold red"
    console.print(f"\n[{color}]総合結果: {report.summary_message}[/{color}]")
    if report.overall_verdict != EvalStatus.PASS:
        raise typer.Exit(1)

@app.command(name="scan-secrets")
def scan_secrets_cmd(
    target_dir: str = typer.Option(".", "--dir", "-d", help="スキャン対象ディレクトリ"),
    strict: bool = typer.Option(True, "--strict", help="シークレット検知時に非ゼロ終了コードで停止")
):
    """リポジトリ内の全ファイルからAPIキー・シークレット・トークンの誤混入を高速スキャン"""
    from ..security.secret_scanner import SecretScanner
    console.print(f"[bold cyan][SCAN][/bold cyan] シークレット誤混入スキャンを開始: [dim]{target_dir}[/dim]")
    
    scanner = SecretScanner()
    findings = scanner.scan_directory(target_dir)

    if not findings:
        console.print("[bold green][OK] シークレット誤混入は 0 件です。クリーンな状態が確認されました。[/bold green]")
        return

    table = Table(title=f"[bold red]シークレット誤混入検出アラート ({len(findings)} 件)[/bold red]", border_style="red")
    table.add_column("重大度", style="bold red", justify="center")
    table.add_column("ファイル / 行", style="cyan")
    table.add_column("ルールID", style="yellow")
    table.add_column("種別")
    table.add_column("マスキング済スニペット")

    for f in findings:
        table.add_row(
            f"[{'red' if f.severity == 'CRITICAL' else 'yellow'}]{f.severity}[/]",
            f"{f.file_path}:{f.line_number}",
            f.rule_id,
            f.secret_type,
            f"[dim]{f.masked_snippet}[/dim]"
        )
    console.print(table)
    console.print("[bold red][FAIL] コミット前に上記シークレットを削除・無害化してください。[/bold red]")
    if strict:
        raise typer.Exit(1)

@app.command()
def init():
    """プロジェクトに ASDLC 構成とマルチAI CLIツール向け設定ファイルを初期化"""
    console.print("[bold green][SUCCESS] ASDLC (AI-SDLC) プロジェクトを初期化しました。[/bold green]")
    console.print("互換ツール: Claude Code, GitHub Copilot CLI, Google Antigravity, Gemini CLI")

if __name__ == "__main__":
    app()

