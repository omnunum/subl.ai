brew update
brew install sound-touch 
brew install ffmpeg 
brew install espeak
AENEAS_WITH_CEW=False pip install -r requirements.txt
python -m spacy download en_core_web_sm