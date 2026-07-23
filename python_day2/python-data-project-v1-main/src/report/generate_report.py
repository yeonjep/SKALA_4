from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUTS_DIR = PROJECT_ROOT / "output"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "report.md"
DEFAULT_LOG_PATH = PROJECT_ROOT / "logs" / "report_generation.log"
DEFAULT_TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "report_template.md"

SEABORN_CHART_CANDIDATES = [
    "seaborn_distribution.png",
    "trip_distance_distribution.png",
    "seaborn_trip_distance_distribution.png",
    "trip_distance_hist_kde.png",
    "figures/seaborn_distribution.png",
    "figures/trip_distance_distribution.png",
    "figures/seaborn_trip_distance_distribution.png",
    "figures/trip_distance_hist_kde.png",
    "figures/seaborn_chart.png",
    "figures/seaborn.png",
    "figures/static_chart.png",
]

PLOTLY_CHART_CANDIDATES = [
    "plotly_group_comparison.html",
    "hourly_average_fare.html",
    "hourly_average_fare_by_payment_type.html",
    "plotly_hourly_average_fare.html",
    "figures/plotly_group_comparison.html",
    "figures/hourly_average_fare.html",
    "figures/hourly_average_fare_by_payment_type.html",
    "figures/plotly_hourly_average_fare.html",
    "figures/plotly_chart.html",
    "figures/plotly.html",
    "figures/interactive_chart.html",
]


def setup_logger(log_path: Path) -> logging.Logger:
    """Create a logger for report generation."""
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("report_generation")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def get_value(data: dict[str, Any], keys: list[str], default: Any = "미제공") -> Any:
    """Return the first present value from a list of possible keys."""
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return default


def to_builtin(value: Any) -> Any:
    """Convert scientific Python values into Jinja friendly values."""
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass

    if hasattr(value, "to_dict"):
        try:
            return value.to_dict()
        except (TypeError, ValueError):
            pass

    if isinstance(value, dict):
        return {str(key): to_builtin(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_builtin(item) for item in value]
    if isinstance(value, tuple):
        return [to_builtin(item) for item in value]

    return value


def format_value(value: Any) -> str:
    """Format Python values for Markdown."""
    if value in (None, ""):
        return "미제공"
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (str, int, bool)):
        return str(value)
    return str(value)


def format_inline(value: Any) -> str:
    """Format compact values for list items."""
    if isinstance(value, (dict, list)):
        return "`복합 값 - 상세 결과 참고`"
    return format_value(value)


def dict_to_markdown_table(data: dict[str, Any], empty_message: str = "미제공") -> str:
    """Render a flat dictionary as a Markdown table."""
    if not data:
        return empty_message

    rows = ["| 항목 | 값 |", "| --- | --- |"]
    for key, value in data.items():
        rows.append(f"| {key} | {format_value(value).replace(chr(10), '<br>')} |")
    return "\n".join(rows)


def list_to_markdown(values: list[Any]) -> str:
    """Render a list as Markdown."""
    if not values:
        return "미제공"

    lines = []
    for value in values:
        if isinstance(value, dict):
            lines.append(dict_to_markdown_table(value))
        else:
            lines.append(f"- {format_value(value)}")
    return "\n\n".join(lines)


def nested_mapping_to_markdown(data: Any, empty_message: str = "미제공") -> str:
    """Render nested dict/list data into Markdown without a top-level heading."""
    if not data:
        return empty_message

    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.extend([f"#### {key}", dict_to_markdown_table(value), ""])
            elif isinstance(value, list):
                lines.extend([f"#### {key}", list_to_markdown(value), ""])
            else:
                lines.append(f"- {key}: {format_inline(value)}")
        return "\n".join(lines).strip()

    if isinstance(data, list):
        return list_to_markdown(data)

    return format_value(data)


def relative_to_project(path: Path | None) -> str:
    """Return a project-relative path for Markdown links."""
    if path is None:
        return "미제공"

    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def path_exists_project_relative(value: Any) -> Path | None:
    """Resolve a path that may be absolute or project-root relative."""
    if not isinstance(value, str) or not value.strip():
        return None

    path = Path(value)
    if path.is_absolute():
        return path if path.exists() else None

    project_relative = PROJECT_ROOT / path
    if project_relative.exists():
        return project_relative

    return None


def resolve_output_path(outputs_dir: Path, value: Any) -> Path | None:
    """Resolve a path as absolute, output-relative, or project-relative."""
    if not isinstance(value, str) or not value.strip():
        return None

    path = Path(value)
    if path.is_absolute():
        return path if path.exists() else None

    output_relative = outputs_dir / path
    if output_relative.exists():
        return output_relative

    project_relative = PROJECT_ROOT / path
    if project_relative.exists():
        return project_relative

    return None


def summarize_dataframe(data_frame: Any) -> dict[str, Any]:
    """Create data summary values from the cleaned pandas DataFrame."""
    if data_frame is None or not hasattr(data_frame, "shape"):
        return {}

    rows, columns = data_frame.shape
    missing_by_column = data_frame.isna().sum()

    return {
        "dataset": "NYC Yellow Taxi Trip Data 2026-05",
        "rows": int(rows),
        "columns": int(columns),
        "missing_values": {
            "total_missing_cells": int(missing_by_column.sum()),
            "columns_with_missing": int((missing_by_column > 0).sum()),
        },
        "duplicates": {
            "duplicate_rows": int(data_frame.duplicated().sum()),
            "action": "drop_duplicates 및 dropna 적용",
        },
        "pandas_polars_comparison": "phase1.py에서 Pandas/Polars 로딩 시간을 비교하여 콘솔에 출력",
    }


def find_chart(outputs_dir: Path, candidates: list[str]) -> Path | None:
    """Find the first existing chart path from candidate relative paths."""
    for candidate in candidates:
        path = outputs_dir / candidate
        if path.exists():
            return path
    return None


def find_chart_from_summary(
    outputs_dir: Path,
    eda_summary: dict[str, Any],
    path_keys: list[str],
    candidates: list[str],
    suffix: str,
) -> Path | None:
    """Find chart path from EDA summary first, then known filenames, then suffix."""
    for key in path_keys:
        chart_path = resolve_output_path(outputs_dir, eda_summary.get(key))
        if chart_path:
            return chart_path

    chart_path = find_chart(outputs_dir, candidates)
    if chart_path:
        return chart_path

    for path in sorted(outputs_dir.glob(f"**/*{suffix}")):
        if path.is_file():
            return path

    return None


def build_data_context(data_summary: dict[str, Any]) -> dict[str, Any]:
    """Build template context for data preparation results."""
    missing = get_value(data_summary, ["missing_values", "missing_summary", "nulls"])
    duplicates = get_value(data_summary, ["duplicates", "duplicate_count"])
    pandas_polars = get_value(
        data_summary,
        ["pandas_polars_comparison", "loader_comparison", "pandas_vs_polars"],
    )

    return {
        "dataset": format_inline(
            get_value(data_summary, ["dataset", "dataset_name", "source", "data_path"])
        ),
        "rows": format_inline(get_value(data_summary, ["rows", "row_count", "n_rows"])),
        "columns": format_inline(
            get_value(data_summary, ["columns", "column_count", "n_columns"])
        ),
        "missing": format_inline(missing),
        "duplicates": format_inline(duplicates),
        "pandas_polars": format_inline(pandas_polars),
        "missing_detail": nested_mapping_to_markdown(missing)
        if isinstance(missing, dict)
        else "",
        "duplicates_detail": nested_mapping_to_markdown(duplicates)
        if isinstance(duplicates, dict)
        else "",
        "pandas_polars_detail": nested_mapping_to_markdown(pandas_polars)
        if isinstance(pandas_polars, dict)
        else "",
    }


def build_eda_context(eda_summary: dict[str, Any], outputs_dir: Path) -> dict[str, Any]:
    """Build template context for EDA and visualization results."""
    seaborn_chart = find_chart_from_summary(
        outputs_dir,
        eda_summary,
        [
            "seaborn_chart_path",
            "seaborn_path",
            "static_chart_path",
            "distribution_chart_path",
            "trip_distance_distribution_path",
        ],
        SEABORN_CHART_CANDIDATES,
        ".png",
    )
    plotly_chart = find_chart_from_summary(
        outputs_dir,
        eda_summary,
        [
            "plotly_chart_path",
            "plotly_path",
            "interactive_chart_path",
            "group_chart_path",
            "hourly_average_fare_path",
        ],
        PLOTLY_CHART_CANDIDATES,
        ".html",
    )

    observations = get_value(
        eda_summary,
        ["observations", "key_findings", "summary"],
        default=[],
    )
    excluded_keys = {
        "observations",
        "key_findings",
        "summary",
        "seaborn_chart_path",
        "seaborn_path",
        "static_chart_path",
        "distribution_chart_path",
        "trip_distance_distribution_path",
        "plotly_chart_path",
        "plotly_path",
        "interactive_chart_path",
        "group_chart_path",
        "hourly_average_fare_path",
    }
    extra = {key: value for key, value in eda_summary.items() if key not in excluded_keys}

    return {
        "observations": list_to_markdown(observations)
        if isinstance(observations, list)
        else f"- {observations}",
        "expected_outputs": [
            "`output/seaborn_distribution.png`",
            "`output/plotly_group_comparison.html`",
        ],
        "seaborn_chart_path": relative_to_project(seaborn_chart)
        if seaborn_chart
        else "미제공",
        "plotly_chart_path": relative_to_project(plotly_chart)
        if plotly_chart
        else "미제공",
        "has_seaborn_chart": seaborn_chart is not None,
        "has_plotly_chart": plotly_chart is not None,
        "extra": nested_mapping_to_markdown(extra) if extra else "",
    }


def build_stats_context(stats_summary: dict[str, Any]) -> dict[str, Any]:
    """Build template context for statistical analysis results."""
    descriptive = get_value(
        stats_summary,
        ["descriptive_statistics", "descriptive_stats", "describe"],
        default={},
    )
    correlations = get_value(
        stats_summary,
        ["correlations", "correlation_matrix", "correlation"],
        default={},
    )
    if not correlations and "corr_coefficient" in stats_summary:
        correlations = {
            "trip_distance_vs_fare_amount": stats_summary["corr_coefficient"]
        }

    t_test = get_value(stats_summary, ["t_test", "ttest_ind", "t_test_result"], default={})
    if not t_test and any(
        key in stats_summary for key in ["t_statistic", "p_value", "interpretation"]
    ):
        t_test = {
            "t_statistic": stats_summary.get("t_statistic"),
            "p_value": stats_summary.get("p_value"),
            "interpretation": stats_summary.get("interpretation"),
            "short_mean": stats_summary.get("short_mean"),
            "long_mean": stats_summary.get("long_mean"),
        }

    p_value = "미제공"
    interpretation = "미제공"
    t_test_detail = ""
    if isinstance(t_test, dict):
        p_value = get_value(t_test, ["p_value", "pvalue", "p"])
        interpretation = get_value(t_test, ["interpretation", "p_value_interpretation"])
        detail = {
            key: value
            for key, value in t_test.items()
            if key
            not in {
                "p_value",
                "pvalue",
                "p",
                "interpretation",
                "p_value_interpretation",
            }
        }
        t_test_detail = nested_mapping_to_markdown(detail) if detail else ""

    return {
        "descriptive": nested_mapping_to_markdown(descriptive),
        "correlations": nested_mapping_to_markdown(correlations),
        "t_test_p_value": format_inline(p_value),
        "t_test_interpretation": format_inline(interpretation),
        "t_test_detail": t_test_detail,
    }


def build_ml_context(ml_metrics: dict[str, Any], outputs_dir: Path) -> dict[str, Any]:
    """Build template context for ML pipeline results."""
    model_path_value = get_value(ml_metrics, ["model_path", "saved_model_path"], default="")
    model_path = outputs_dir / "model" / "model.joblib"
    if model_path_value:
        candidate = Path(str(model_path_value))
        model_path = candidate if candidate.is_absolute() else PROJECT_ROOT / candidate

    importance_path = path_exists_project_relative(
        get_value(ml_metrics, ["importance_path"], default="")
    )
    flat_metric_keys = [
        "accuracy",
        "f1",
        "precision",
        "recall",
        "n_train",
        "n_test",
        "confusion_matrix",
    ]
    flat_metrics = {
        key: ml_metrics[key]
        for key in flat_metric_keys
        if key in ml_metrics and ml_metrics[key] not in (None, "")
    }
    nested_metrics = get_value(
        ml_metrics,
        ["metrics", "evaluation_metrics", "scores"],
        default={},
    )
    metrics = nested_metrics if nested_metrics else flat_metrics
    default_pipeline_steps = {
        "preprocessing": "ColumnTransformer: numeric imputer/scaler + categorical imputer/one-hot",
        "model": "RandomForestClassifier",
        "target": "payment_type",
    }

    excluded_keys = {
        "model",
        "model_name",
        "estimator",
        "task_type",
        "task",
        "metrics",
        "evaluation_metrics",
        "scores",
        *flat_metric_keys,
        "report",
        "top_features",
        "importance_path",
        "pipeline_steps",
        "steps",
        "preprocessing",
        "model_path",
        "saved_model_path",
    }
    extra = {key: value for key, value in ml_metrics.items() if key not in excluded_keys}

    return {
        "task_type": format_inline(
            get_value(ml_metrics, ["task_type", "task"], default="classification")
        ),
        "model_name": format_inline(
            get_value(
                ml_metrics,
                ["model", "model_name", "estimator"],
                default="RandomForestClassifier",
            )
        ),
        "model_path": relative_to_project(model_path) if model_path.exists() else "미제공",
        "pipeline_steps": nested_mapping_to_markdown(
            get_value(
                ml_metrics,
                ["pipeline_steps", "steps", "preprocessing"],
                default=default_pipeline_steps,
            )
        ),
        "metrics": nested_mapping_to_markdown(metrics),
        "classification_report": ml_metrics.get("report", ""),
        "top_features": ml_metrics.get("top_features", []),
        "importance_path": relative_to_project(importance_path) if importance_path else "미제공",
        "has_importance_chart": importance_path is not None,
        "extra": nested_mapping_to_markdown(extra) if extra else "",
    }


def build_report_context(
    summaries: dict[str, dict[str, Any]],
    outputs_dir: Path,
    report_path: Path,
    log_path: Path,
    command: str,
) -> dict[str, Any]:
    """Build the complete Jinja2 template context."""
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": build_data_context(summaries["data"]),
        "eda": build_eda_context(summaries["eda"], outputs_dir),
        "stats": build_stats_context(summaries["stats"]),
        "ml": build_ml_context(summaries["ml"], outputs_dir),
        "reproducibility": {
            "outputs_dir": relative_to_project(outputs_dir),
            "report_path": relative_to_project(report_path),
            "log_path": relative_to_project(log_path),
            "command": command,
        },
    }


def render_template(template_path: Path, context: dict[str, Any]) -> str:
    """Render the Markdown report template with Jinja2."""
    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError as exc:
        raise RuntimeError("Jinja2가 설치되어 있지 않습니다. `pip install Jinja2`를 실행하세요.") from exc

    environment = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    template = environment.get_template(template_path.name)
    return template.render(**context)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate report.md from analysis outputs.")
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=DEFAULT_OUTPUTS_DIR,
        help="Directory containing analysis output files.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path where the Markdown report will be written.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Path where report generation logs will be written.",
    )
    parser.add_argument(
        "--template-path",
        type=Path,
        default=DEFAULT_TEMPLATE_PATH,
        help="Jinja2 Markdown template path.",
    )
    return parser.parse_args()


def generate_report(
    outputs_dir: Path = DEFAULT_OUTPUTS_DIR,
    report_path: Path = DEFAULT_REPORT_PATH,
    log_path: Path = DEFAULT_LOG_PATH,
    template_path: Path = DEFAULT_TEMPLATE_PATH,
    data_frame: Any = None,
    stats_results: dict[str, Any] | None = None,
    ml_results: dict[str, Any] | None = None,
    command: str = "python3 src/report/generate_report.py",
) -> Path:
    """Generate report.md and return the generated report path."""
    outputs_dir = outputs_dir.resolve()
    report_path = report_path.resolve()
    log_path = log_path.resolve()
    template_path = template_path.resolve()

    logger = setup_logger(log_path)
    logger.info("Starting report generation")
    logger.info("Outputs directory: %s", outputs_dir)
    logger.info("Template path: %s", template_path)

    summaries: dict[str, dict[str, Any]] = {
        "data": {},
        "eda": {},
        "stats": {},
        "ml": {},
    }
    runtime_summaries = {
        "data": summarize_dataframe(data_frame),
        "stats": to_builtin(stats_results or {}),
        "ml": to_builtin(ml_results or {}),
    }
    for section, values in runtime_summaries.items():
        if values:
            summaries[section].update(values)
            logger.info("Merged runtime results for section: %s", section)

    context = build_report_context(
        summaries=summaries,
        outputs_dir=outputs_dir,
        report_path=report_path,
        log_path=log_path,
        command=command,
    )
    report = render_template(template_path, context)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    logger.info("Report written: %s", report_path)
    return report_path


def main() -> int:
    args = parse_args()
    generate_report(
        outputs_dir=args.outputs_dir,
        report_path=args.report_path,
        log_path=args.log_path,
        template_path=args.template_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
