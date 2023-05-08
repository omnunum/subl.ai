module default {
    type RenderedAudio {
        required property raw -> bytes;
        required property nonsilent -> bytes;
        required property processed -> bytes;
        required property extended -> bytes;
    }

    type RenderedAudioReport {
        required property speech_rate -> float64;
        required property retime_pct -> int64;
        required property noise_factor -> float64;
        required property raw_length -> int64;
        required property nonsilent_length -> int64;
        required property silent_length -> int64;
        required property extended_length -> int64;
        required property random_silence_duration -> int64;
    }

    type Fragment {
        required property idx -> int64;
        required property text -> str;

        optional link report -> RenderedAudioReport;
        optional link rendered_audio -> RenderedAudio;
    }

    type Clause {
        required property idx -> int64;
        optional property audio -> bytes;

        multi link fragments -> Fragment;
    }

    type Section {
        required property idx -> int64;
        required property name -> str;
        optional property audio -> bytes;

        multi link clauses -> Clause;
    }

    type Script {
        required property name -> str;
        optional property audio -> bytes;

        multi link sections -> Section;
    }
}
