import os
import json
from dataclasses import asdict
import webbrowser
from pathlib import Path

from pydub import AudioSegment
from jinja2 import Template

from common import find_files_in_directory
from classes import Script, RenderedClause, RenderedSection
from fetch_audio import fetch
from process_audio import process_fragments, align_transcript


def generate_report(rendered_sections: list[RenderedSection], output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    segments_dir = output_dir / "segments"
    segments_dir.mkdir(exist_ok=True)

    html_parts = []

    for section_idx, section in enumerate(rendered_sections):
        html_parts.append(f'<h2>Section: {section.name}</h2>')

        for clause_idx, clause in enumerate(section.clauses):
            html_parts.append(f'<h3>Clause {clause_idx + 1}: {clause.text}</h3>')
            table_rows = []

            for fragment_idx, fragment in enumerate(clause.fragments):
                audio_files = {}
                fragment_audio = asdict(fragment.audio).items()
                for audio_type, audio in fragment_audio:
                    audio_file = segments_dir / f"{section_idx}_{clause_idx}_{fragment_idx}_{audio_type}.wav"
                    audio.export(audio_file, format="wav")
                    audio_files[audio_type] = audio_file.relative_to(output_dir)

                fragment_table_row = (
                    [f'<td>{fragment.text}</td>'] + 
                    [f"""
                        <td>
                            <audio controls>
                                <source src="{value}" type="audio/wav">
                            </audio>
                        </td>
                    """
                    for value in audio_files.values()] + 
                    [
                        f"<td>{format(value, '.4f') if isinstance(value, float) else value}</td>" 
                        for key, value in asdict(fragment.report).items()
                    ]
                )

                table_rows.append('<tr>' + ''.join(fragment_table_row) + '</tr>')

            html_parts.append(f"""
                <table border="1" cellpadding="5">
                    <tr>
                        <th>Text</th>
                        <th>Raw Audio</th>
                        <th>Nonsilent Audio</th>
                        <th>Processed Audio</th>
                        <th>Extended Audio</th>
                        <th>Speech Rate</th>
                        <th>Retime %</th>
                        <th>Noise Factor</th>
                        <th>Raw Length</th>
                        <th>Non-silent Length</th>
                        <th>Silent Length</th>
                        <th>Extended Length</th>
                        <th>Random Silence Duration</th>
                    </tr>
                    {"".join(table_rows)}
                </table>
            """)

    html_content = "\n".join(html_parts)
    report_file_path = output_dir / "report.html"
    with open(report_file_path, "w") as report_file:
        report_file.write(html_content)

    # Open the report in the default web browser
    webbrowser.open(str(report_file_path))

def main():
    for script_file in find_files_in_directory("scripts", "\.json"):
        with open(script_file, "r") as script_file:
            script = Script.from_json(script_file.read())

        audio_dir = Path("audio", script.name)
        raw_dir = audio_dir / "raw"
        fetch("Sleepy Sister", script, raw_dir)

        output = AudioSegment.empty()
        report = []
        for section_ix, section in enumerate(script.sections):
            rendered_section = RenderedSection(
                name=section.name, 
                audio=AudioSegment.empty(),
                clauses=[]
            )   
            for clause_ix, clause in enumerate(section.clauses):
                name = f"{section_ix}_{section.name}_{clause_ix}.wav"
                fragments = process_fragments(
                    AudioSegment.from_file(raw_dir / name), 
                    align_transcript(raw_dir / name, clause), 
                    extend_silence_ms=500, 
                    min_silence_ms=250, 
                    noise_scale=100, 
                    target_speech_rate=3.5,
                    shift_fragment_windows=-50
                )
                all_segments = sum([s.audio.extended for s in fragments])
                rendered_clause = RenderedClause(
                    audio=all_segments,
                    fragments=fragments,
                )  
                rendered_section.audio += all_segments
                rendered_section.clauses.append(rendered_clause)
            output += rendered_section.audio
            report.append(rendered_section)
        output.export(audio_dir / "output.wav", format="wav")

        report = generate_report(report, audio_dir)


if __name__ == "__main__":
    main()
