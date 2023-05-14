module default {
    abstract type HasHistory {
        required property created_at -> datetime;
        required property modified_at -> datetime;
    }

    type RenderedAudio extending HasHistory{
        required property raw -> str;
        required property nonsilent -> str;
        required property processed -> str;
        required property extended -> str;
    }

    type RenderedAudioReport extending HasHistory {
        required property speech_rate -> float64;
        required property retime_pct -> int64;
        required property noise_factor -> float64;
        required property raw_length -> int64;
        required property nonsilent_length -> int64;
        required property silent_length -> int64;
        required property extended_length -> int64;
        required property random_silence_duration -> int64;
    }

    type Fragment extending HasHistory {
        required property idx -> int64;
        required property text -> str;

        optional link report -> RenderedAudioReport;
        optional link rendered_audio -> RenderedAudio;
    }

    type Clause extending HasHistory {
        required property idx -> int64;
        optional property audio -> str;

        multi link fragments -> Fragment;
    }

    type Section extending HasHistory {
        required property idx -> int64;
        required property name -> str;
        optional property audio -> str;

        multi link clauses -> Clause;
    }

    type Script extending HasHistory {
        required property name -> str;
        optional property audio -> str;

        multi link sections -> Section;
    }
}
