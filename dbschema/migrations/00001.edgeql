CREATE MIGRATION m1uqbstvwom42syrjel5cedvf7beydrs5rzivklsru776cyhy65o2a
    ONTO initial
{
  CREATE FUTURE nonrecursive_access_policies;
  CREATE TYPE default::RenderedAudio {
      CREATE REQUIRED PROPERTY extended -> std::bytes;
      CREATE REQUIRED PROPERTY nonsilent -> std::bytes;
      CREATE REQUIRED PROPERTY processed -> std::bytes;
      CREATE REQUIRED PROPERTY raw -> std::bytes;
  };
  CREATE TYPE default::RenderedAudioReport {
      CREATE REQUIRED PROPERTY extended_length -> std::int64;
      CREATE REQUIRED PROPERTY noise_factor -> std::float64;
      CREATE REQUIRED PROPERTY nonsilent_length -> std::int64;
      CREATE REQUIRED PROPERTY random_silence_duration -> std::int64;
      CREATE REQUIRED PROPERTY raw_length -> std::int64;
      CREATE REQUIRED PROPERTY retime_pct -> std::int64;
      CREATE REQUIRED PROPERTY silent_length -> std::int64;
      CREATE REQUIRED PROPERTY speech_rate -> std::float64;
  };
  CREATE TYPE default::Fragment {
      CREATE OPTIONAL LINK rendered_audio -> default::RenderedAudio;
      CREATE OPTIONAL LINK report -> default::RenderedAudioReport;
      CREATE REQUIRED PROPERTY idx -> std::int64;
      CREATE REQUIRED PROPERTY text -> std::str;
  };
  CREATE TYPE default::Clause {
      CREATE MULTI LINK fragments -> default::Fragment;
      CREATE OPTIONAL PROPERTY audio -> std::bytes;
      CREATE REQUIRED PROPERTY idx -> std::int64;
  };
  CREATE TYPE default::Section {
      CREATE MULTI LINK clauses -> default::Clause;
      CREATE OPTIONAL PROPERTY audio -> std::bytes;
      CREATE REQUIRED PROPERTY idx -> std::int64;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
  CREATE TYPE default::Script {
      CREATE MULTI LINK sections -> default::Section;
      CREATE OPTIONAL PROPERTY audio -> std::bytes;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
};
